from langchain.tools import BaseTool
from langchain_community.document_loaders import WebBaseLoader
from langchain.agents.agent import AgentExecutor
from src.utils.get_langchain_llm import get_langchain_llm
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage


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

    def _create_prompt(self, url: str, instructions: str) -> str:
        """Create a prompt template for scraping."""
        return f"Please extract the following information from the webpage at {url}: {instructions}"

    async def scrape(self, url: str, instructions: str) -> str:
        """Scrape content from a given URL"""
        prompt = self._create_prompt(url, instructions)
        # LangGraph agents expect messages, not just strings
        messages = [HumanMessage(content=prompt)]
        result = self.agent.invoke({"messages": messages})

        # Extract the content from the result
        if "messages" in result and len(result["messages"]) > 0:
            return result["messages"][-1].content
        return "No content retrieved"

    async def scrape_multiple(self, urls: list[str], instructions: str) -> list[str]:
        """Scrape content from multiple URLs"""
        return [await self.scrape(url, instructions) for url in urls]
