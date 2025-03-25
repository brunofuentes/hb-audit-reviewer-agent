from src.agents.web_scraper import WebScraper
from src.agents.syntax_scout import SyntaxScout
from src.agents.audit_quality_checker import AuditQualityChecker
from src.agents.review_report_builder import ReviewReportBuilder
from src.utils.file_utils import save_report
from src.database.session import get_db
from src.database.crud.review import ReviewCreate, review
from src.database.enums import StepName
from src.database.crud.review_step import ReviewStepCreate, review_step


async def analyze_audit_url(url):
    """Run the complete analysis pipeline on a single audit URL"""
    print(f"Starting analysis of: {url}")

    # Create review entry in database
    db = get_db()
    review_obj = ReviewCreate(audit_url=url)
    db_review = review.create(db=db, obj_in=review_obj)

    print(
        f"Created review: ID={db_review.id}, URL={db_review.audit_url}, Status={db_review.status}"
    )

    # Scrape content
    print("Scraping content...")
    scraper = WebScraper()
    instructions = "Just get the full text of the page and return it as a string."
    webpage_content = await scraper.scrape(url=url, instructions=instructions)
    print("Content scraped successfully.")

    # Create review step entry in database
    scraping_step_obj = ReviewStepCreate(
        review_id=db_review.id,
        name=StepName.SCRAPING,
        input=url,
        output=webpage_content,
    )
    db_scraping_step = review_step.create(db=db, obj_in=scraping_step_obj)
    print(
        f"Created review step: ID={db_scraping_step.id}, "
        f"Review ID={db_scraping_step.id}, "
        f"Step Name={db_scraping_step.name}, "
        f"Input={db_scraping_step.input}, "
        f"Output={db_scraping_step.output}"
    )

    # Run syntax analysis
    print("Analyzing for syntax issues...")
    scout = SyntaxScout()
    syntax_analysis = await scout.analyze(webpage_content["raw_content"])

    # Create review step entry in database
    syntax_step_obj = ReviewStepCreate(
        review_id=db_review.id,
        name=StepName.SYNTAX_CHECK,
        input=webpage_content["raw_content"],
        output=syntax_analysis,
    )
    db_syntax_step = review_step.create(db=db, obj_in=syntax_step_obj)
    print(
        f"Created review step: ID={db_syntax_step.id}, "
        f"Review ID={db_syntax_step.review_id}, "
        f"Step Name={db_syntax_step.name}, "
        f"Input={db_syntax_step.input}, "
        f"Output={db_syntax_step.output}"
    )

    # Run quality analysis
    print("Analyzing audit report quality...")
    quality_checker = AuditQualityChecker()
    quality_analysis = await quality_checker.analyze(webpage_content["raw_content"])

    # Create review step entry in database
    quality_step_obj = ReviewStepCreate(
        review_id=db_review.id,
        name=StepName.QUALITY_CHECK,
        input=webpage_content["raw_content"],
        output=quality_analysis,
    )
    db_quality_step = review_step.create(db=db, obj_in=quality_step_obj)
    print(
        f"Created review step: ID={db_quality_step.id}, "
        f"Review ID={db_quality_step.review_id}, "
        f"Step Name={db_quality_step.name}, "
        f"Input={db_quality_step.input}, "
        f"Output={db_quality_step.output}"
    )

    # Build the final report
    print("Building consolidated review report...")
    report_builder = ReviewReportBuilder()
    review_report = await report_builder.build_report(syntax_analysis, quality_analysis)

    both_analysis_text = (
        f"Syntax Analysis: {syntax_analysis}\nQuality Analysis: {quality_analysis}"
    )

    # Create review step entry in database
    report_step_obj = ReviewStepCreate(
        review_id=db_review.id,
        name=StepName.REPORT_GEN,
        input=both_analysis_text,
        output=review_report,
    )
    db_report_step = review_step.create(db=db, obj_in=report_step_obj)
    print(
        f"Created review step: ID={db_report_step.id}, "
        f"Review ID={db_report_step.review_id}, "
        f"Step Name={db_report_step.name}, "
        f"Input={db_report_step.input}, "
        f"Output={db_report_step.output}"
    )

    # Save the report and return the path
    report_path = save_report(url, review_report)

    print("\nAnalysis complete!")
    print(
        f"Overall Assessment: {review_report['assessment']} ({review_report['overall_score']:.1f}/10)"
    )
    print(f"Full report saved to: {report_path}")

    return 0
