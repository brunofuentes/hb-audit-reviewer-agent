import asyncio
from src.agents.web_scraper import WebScraper
from src.agents.syntax_scout import SyntaxScout
from src.agents.audit_quality_checker import AuditQualityChecker


async def main():
    scraper = WebScraper()

    # Single URL
    url = "https://www.halborn.com/audits/the-vault/the-vault---directed-stake-program-fbc4ff"
    instructions = "Just get the full text of the page and return it as a string."
    result = await scraper.scrape(url=url, instructions=instructions)
    print("--- SCRAPED CONTENT ---")
    print(result[:500] + "..." if len(result) > 500 else result)

    # Syntax analysis
    print("\n--- ANALYZING TEXT FOR SYNTAX ISSUES ---")
    scout = SyntaxScout()
    syntax_analysis = await scout.analyze(result)
    print("\n--- SYNTAX ANALYSIS RESULTS ---")
    print(f"Issues detected: {syntax_analysis['issues_detected']}")
    print("\nSyntax Analysis:")
    print(syntax_analysis["analysis_result"])

    # Quality analysis
    print("\n--- ANALYZING AUDIT REPORT QUALITY ---")
    quality_checker = AuditQualityChecker()
    quality_analysis = await quality_checker.analyze(result)
    print("\n--- AUDIT QUALITY ANALYSIS RESULTS ---")
    print(f"Structure Score: {quality_analysis['structure_score']}/10")
    print(f"Clarity Score: {quality_analysis['clarity_score']}/10")
    print(f"Quality issues detected: {quality_analysis['quality_issues_detected']}")
    print("\nQuality Analysis:")
    print(quality_analysis["full_analysis"])

    return 0


if __name__ == "__main__":
    asyncio.run(main())
