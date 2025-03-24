import asyncio
from src.agents.web_scraper import WebScraper


async def main():
    scraper = WebScraper()

    # Single URL
    url = "https://www.halborn.com/audits/the-vault/the-vault---directed-stake-program-fbc4ff"
    instructions = "Just get the full text of the page and return it as a string."
    result = await scraper.scrape(url=url, instructions=instructions)
    print(result)

    return 0


if __name__ == "__main__":
    asyncio.run(main())
