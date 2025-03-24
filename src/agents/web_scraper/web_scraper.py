from langchain.tools import BaseTool
from langchain.agents import initialize_agent, AgentType
from langchain_community.document_loaders import WebBaseLoader
from langchain.agents.agent import AgentExecutor
from src.utils.get_langchain_llm import get_langchain_llm


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
        return initialize_agent(
            tools, self.llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=False
        )

    def _create_prompt(self, url: str, instructions: str) -> str:
        """Create a prompt template for scraping."""
        return f"Please extract the following information from the webpage at {url}: {instructions}"

    async def scrape(self, url: str, instructions: str) -> str:
        """Scrape content from a given URL"""
        prompt = self._create_prompt(url, instructions)
        result = self.agent.invoke({"input": prompt})

        raw_content = result["output"]
        return raw_content

    async def scrape_multiple(self, urls: list[str]) -> list[str]:
        """Scrape content from multiple URLs"""
        return [await self.scrape(url) for url in urls]
