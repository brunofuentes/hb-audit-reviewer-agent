import asyncio
from src.agents.web_scraper import WebScraper
from src.agents.syntax_scout import SyntaxScout
from src.agents.audit_quality_checker import AuditQualityChecker
from src.agents.review_report_builder import ReviewReportBuilder
import os
import datetime
import re
from urllib.parse import urlparse


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

    # After getting syntax_analysis and quality_analysis:
    print("\n--- BUILDING CONSOLIDATED REVIEW REPORT ---")
    report_builder = ReviewReportBuilder()
    review_report = await report_builder.build_report(syntax_analysis, quality_analysis)

    print("\n--- FINAL REVIEW REPORT ---")
    print(
        f"Overall Assessment: {review_report['assessment']} ({review_report['overall_score']:.1f}/10)"
    )
    print("\nReport:")
    print(review_report["report"])

    # Extract the last part of the URL for the filename
    parsed_url = urlparse(url)
    url_path = parsed_url.path
    last_path_part = os.path.basename(url_path)
    # Clean the filename by removing special characters
    clean_filename = re.sub(r"[^\w\-]", "_", last_path_part)

    # Add timestamp to make it unique (format: YYYYMMDD_HHMMSS)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{clean_filename}_{timestamp}.md"

    # Ensure reports directory exists
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    # Full path for the report file
    report_path = os.path.join(reports_dir, filename)

    # Save the report
    with open(report_path, "w") as f:
        f.write("# Audit Report Review\n\n")
        f.write(
            f"**Overall Assessment:** {review_report['assessment']} ({review_report['overall_score']:.1f}/10)\n\n"
        )
        f.write(review_report["report"])

    print(f"\nReport saved to: {report_path}")

    return 0


if __name__ == "__main__":
    asyncio.run(main())
