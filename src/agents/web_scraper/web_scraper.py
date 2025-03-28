from langchain.tools import BaseTool
from langchain_community.document_loaders import WebBaseLoader
from langchain.agents.agent import AgentExecutor
from src.utils.get_langchain_llm import get_langchain_llm
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any, Optional, TypedDict
from langgraph.graph import StateGraph, END
from src.agents.schemas import WebScraperOutput


class WebScraper:
    def __init__(self, model_name: str = "openai"):
        self.llm = get_langchain_llm(model_name=model_name)
        self.model_name = model_name
        self.agent = self._initialize_agent()
        self.graph = self._build_graph()

    def _create_scraper_tool(self) -> BaseTool:
        class WebScraperTool(BaseTool):
            name: str = "web_scraper"
            description: str = "Use this tool to scrape a website for information"

            def _run(self, url: str) -> str:
                loader = WebBaseLoader(url)
                docs = loader.load()
                return docs[0].page_content

        return WebScraperTool()

    def _initialize_agent(self) -> AgentExecutor:
        tools = [self._create_scraper_tool()]
        agent = create_react_agent(self.llm, tools)
        return agent

    def _create_prompt(self, url: str) -> str:
        """Create a prompt template for scraping."""
        base_prompt = (
            f"Visit the webpage at {url}, extract the full raw content, "
            "and return it as a plain text string. Do not include any additional formatting, "
            "explanations, or metadata—only the extracted content."
        )

        # Add specific instructions for anthropic models
        if "anthropic" in self.model_name.lower():
            base_prompt += (
                " The content might be lengthy. DO NOT truncate or summarize the content. "
                "Ensure you extract ALL text from the webpage, including content that might "
                "require scrolling down or expanding sections. I need EVERYTHING, exactly as it appears."
            )

        return base_prompt

    def _route_after_verification(self, state: Dict[str, Any]) -> str:
        """Router function to determine the next node after verification"""
        if state.get("verified", False):
            return "verified"
        else:
            return "not_verified"

    def _build_graph(self):
        """Build a simple graph for the scraping process"""

        class ScraperState(TypedDict):
            url: str
            content: Optional[str]
            verification_text: Optional[str]
            verified: Optional[bool]
            retry_count: Optional[int]
            max_retries: Optional[int]
            error: Optional[str]
            scrape_success: Optional[bool]

        # Define the scraping workflow as a graph with the correct constructor
        workflow = StateGraph(ScraperState)

        # Add nodes to the graph
        workflow.add_node("scrape", self._scrape_node)
        workflow.add_node("verify", self._verify_node)
        workflow.add_node("retry", self._retry_node)

        # Define edges with the correct API
        workflow.add_edge("scrape", "verify")

        # Use if_else instead of condition parameter
        workflow.add_conditional_edges(
            "verify",
            self._route_after_verification,
            {"verified": END, "not_verified": "retry"},
        )

        # Set the entry point
        workflow.set_entry_point("scrape")

        return workflow.compile()

    def _scrape_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node that scrapes the content"""
        url = state.get("url", "")
        prompt = self._create_prompt(url)
        messages = [HumanMessage(content=prompt)]

        try:
            result = self.agent.invoke({"messages": messages})

            if "messages" in result and len(result["messages"]) > 0:
                content = result["messages"][-1].content
                # Ensure content is a string
                if not isinstance(content, str):
                    content = str(content)

                return {
                    **state,
                    "content": content,
                    "scrape_success": True,
                    "retry_count": 0,
                }

            return {**state, "content": "", "scrape_success": False}
        except Exception as e:
            return {**state, "content": "", "scrape_success": False, "error": str(e)}

    def _verify_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node that verifies content is complete"""
        content = state.get("content", "")
        verification_text = state.get("verification_text", "")

        if not verification_text or verification_text in content:
            return {**state, "verified": True}

        # Try direct WebBaseLoader as an alternative verification
        try:
            url = state.get("url", "")
            loader = WebBaseLoader(url)
            docs = loader.load()
            direct_content = docs[0].page_content

            if verification_text in direct_content:
                return {**state, "content": direct_content, "verified": True}
        except Exception:
            pass

        return {**state, "verified": False}

    def _retry_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Node that retries if verification fails"""
        url = state.get("url", "")
        verification_text = state.get("verification_text", "")
        retry_count = state.get("retry_count", 0) + 1
        max_retries = state.get("max_retries", 3)

        if retry_count > max_retries:
            return {
                **state,
                "retry_count": retry_count,
                "error": f"Verification failed after {retry_count} retries",
            }

        # Update prompt for retries with more emphasis on completeness
        retry_prompt = (
            f"The previous scrape of {url} was incomplete. "
            f"I need to find text containing: '{verification_text}'. "
            f"Please scrape the ENTIRE webpage and return ALL content. "
            f"This is retry {retry_count} of {max_retries}. "
            f"Do not summarize or truncate ANY content."
        )

        retry_messages = [
            SystemMessage(
                content=(
                    "You are an expert web scraper. "
                    "Your task is to extract COMPLETE content without omitting anything."
                )
            ),
            HumanMessage(content=retry_prompt),
        ]

        try:
            retry_result = self.agent.invoke({"messages": retry_messages})

            if "messages" in retry_result and len(retry_result["messages"]) > 0:
                retry_content = retry_result["messages"][-1].content
                if isinstance(retry_content, str):
                    if verification_text in retry_content:
                        return {
                            **state,
                            "content": retry_content,
                            "verified": True,
                            "retry_count": retry_count,
                        }
                    return {
                        **state,
                        "content": retry_content,
                        "verified": False,
                        "retry_count": retry_count,
                    }

            return {**state, "retry_count": retry_count}
        except Exception as e:
            return {**state, "retry_count": retry_count, "error": str(e)}

    def _is_verified(self, state: Dict[str, Any]) -> bool:
        """Condition to check if content is verified"""
        return state.get("verified", False)

    def _not_verified(self, state: Dict[str, Any]) -> bool:
        """Condition to check if content is not verified"""
        return not state.get("verified", False)

    def get_prompt(self, url: str) -> str:
        """Get the prompt used for scraping a URL."""
        return self._create_prompt(url)

    async def scrape(
        self,
        url: str,
        verification_text: str = "Halborn 2025. All rights reserved.",
        max_retries: int = 3,
    ) -> WebScraperOutput:
        """
        Scrape content from a given URL with verification

        Args:
            url: The URL to scrape
            verification_text: Optional text to verify in the response
            max_retries: Maximum number of retry attempts
        """
        # Initialize the state
        initial_state = {
            "url": url,
            "verification_text": verification_text,
            "max_retries": max_retries,
        }

        # Run the graph
        try:
            final_state = self.graph.invoke(initial_state)

            content = final_state.get("content", "")
            error = final_state.get("error", None)
            verified = final_state.get("verified", False)

            if not verified and error:
                return WebScraperOutput(raw_content=content, error=error)

            return WebScraperOutput(raw_content=content)
        except Exception as e:
            return WebScraperOutput(
                raw_content="", error=f"Graph execution failed: {str(e)}"
            )
