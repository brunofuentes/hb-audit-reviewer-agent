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
        return (
            f"Visit the webpage at {url}, extract the full raw content, "
            "and return it as a plain text string. Do not include any additional formatting, "
            "explanations, or metadata—only the extracted content."
        )

    def get_prompt(self, url: str) -> str:
        """Get the prompt used for scraping a URL."""
        return self._create_prompt(url)

    async def scrape(self, url: str) -> WebScraperOutput:
        """Scrape content from a given URL"""
        prompt = self._create_prompt(url)

        messages = [HumanMessage(content=prompt)]
        try:
            result = self.agent.invoke({"messages": messages})

            if "messages" in result and len(result["messages"]) > 0:
                content = result["messages"][-1].content
                # Ensure content is a string
                if not isinstance(content, str):
                    if hasattr(content, "__str__"):
                        content = str(content)
                    else:
                        content = repr(content)
                return WebScraperOutput(raw_content=content)
            return WebScraperOutput(raw_content="No content retrieved")
        except Exception as e:
            return WebScraperOutput(raw_content="", error=str(e))
