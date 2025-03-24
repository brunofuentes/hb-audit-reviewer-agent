import asyncio
from src.agents.web_scraper import WebScraper
from src.agents.syntax_scout import SyntaxScout


async def main():
    scraper = WebScraper()

    # Single URL
    url = "https://www.halborn.com/audits/the-vault/the-vault---directed-stake-program-fbc4ff"
    instructions = "Just get the full text of the page and return it as a string."
    scrape_result = await scraper.scrape(url=url, instructions=instructions)
    print(scrape_result)

    print("\n--- ANALYZING TEXT FOR SYNTAX ISSUES ---")

    scout = SyntaxScout()
    analysis_result = await scout.analyze(text_content=scrape_result)

    print("\n--- TEXT ANALYSIS RESULTS ---")
    print(f"Issues detected: {analysis_result['issues_detected']}")
    print("\nDetailed Analysis:")
    print(analysis_result["analysis_result"])

    return 0


if __name__ == "__main__":
    asyncio.run(main())
