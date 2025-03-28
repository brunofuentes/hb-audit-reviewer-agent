from langchain.tools import BaseTool
from langchain_community.document_loaders import WebBaseLoader
from langchain.agents.agent import AgentExecutor
from src.utils.get_langchain_llm import get_langchain_llm
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from src.agents.schemas import WebScraperOutput


class WebScraper:
    def __init__(self, model_name: str = "openai"):
        self.llm = get_langchain_llm(model_name=model_name)
        self.model_name = model_name
        self.agent = self._initialize_agent()

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
                "If needed, use multiple responses to return ALL content. "
                "Ensure you extract ALL text from the webpage, including content that might "
                "require scrolling down or expanding sections. I need EVERYTHING, exactly as it appears."
            )

        return base_prompt

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
        prompt = self._create_prompt(url)
        messages = [HumanMessage(content=prompt)]

        try:
            # First attempt
            result = self.agent.invoke({"messages": messages})

            if "messages" in result and len(result["messages"]) > 0:
                content = result["messages"][-1].content
                # Ensure content is a string
                if not isinstance(content, str):
                    if hasattr(content, "__str__"):
                        content = str(content)
                    else:
                        content = repr(content)

                # If no verification text needed or it's found, return the content
                if verification_text is None or verification_text in content:
                    return WebScraperOutput(raw_content=content)

                # Verification failed, try direct approach with WebBaseLoader
                retry_count = 0
                while retry_count < max_retries:
                    retry_count += 1

                    # Update prompt for retries
                    retry_prompt = (
                        f"The previous scrape of {url} was incomplete. "
                        f"I need to find text containing: '{verification_text}'. "
                        f"Please scrape the ENTIRE webpage and return ALL content. "
                        f"Do not summarize or truncate ANY content."
                    )

                    # Try direct method first on retries
                    try:
                        loader = WebBaseLoader(url)
                        docs = loader.load()
                        direct_content = docs[0].page_content

                        if verification_text in direct_content:
                            return WebScraperOutput(raw_content=direct_content)
                    except Exception:
                        pass

                    # Retry with updated prompt using agent
                    retry_messages = [HumanMessage(content=retry_prompt)]
                    retry_result = self.agent.invoke({"messages": retry_messages})

                    if "messages" in retry_result and len(retry_result["messages"]) > 0:
                        retry_content = retry_result["messages"][-1].content
                        if (
                            isinstance(retry_content, str)
                            and verification_text in retry_content
                        ):
                            return WebScraperOutput(raw_content=retry_content)

                # All retries failed but return the best content we have (the original)
                return WebScraperOutput(
                    raw_content=content,
                    error=f"Verification failed: Could not find '{verification_text}' in content",
                )

            return WebScraperOutput(raw_content="No content retrieved")
        except Exception as e:
            return WebScraperOutput(raw_content="", error=str(e))
