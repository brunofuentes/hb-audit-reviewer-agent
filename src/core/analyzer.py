from src.agents.web_scraper import WebScraper
from src.agents.syntax_scout import SyntaxScout
from src.agents.audit_quality_checker import AuditQualityChecker
from src.agents.review_report_builder import ReviewReportBuilder
from src.utils.file_utils import save_report


async def analyze_audit_url(url):
    """Run the complete analysis pipeline on a single audit URL"""
    print(f"Starting analysis of: {url}")

    # Scrape content
    print("Scraping content...")
    scraper = WebScraper()
    instructions = "Just get the full text of the page and return it as a string."
    content = await scraper.scrape(url=url, instructions=instructions)
    print("Content scraped successfully.")

    # Run syntax analysis
    print("Analyzing for syntax issues...")
    scout = SyntaxScout()
    syntax_analysis = await scout.analyze(content)

    # Run quality analysis
    print("Analyzing audit report quality...")
    quality_checker = AuditQualityChecker()
    quality_analysis = await quality_checker.analyze(content)

    # Build the final report
    print("Building consolidated review report...")
    report_builder = ReviewReportBuilder()
    review_report = await report_builder.build_report(syntax_analysis, quality_analysis)

    # Save the report and return the path
    report_path = save_report(url, review_report)

    print("\nAnalysis complete!")
    print(
        f"Overall Assessment: {review_report['assessment']} ({review_report['overall_score']:.1f}/10)"
    )
    print(f"Full report saved to: {report_path}")

    return 0
