from src.agents.web_scraper import WebScraper
from src.agents.syntax_scout import SyntaxScout
from src.agents.audit_quality_checker import AuditQualityChecker
from src.agents.review_report_builder import ReviewReportBuilder
from src.utils.file_utils import save_report
from src.database.session import get_db
from src.database.crud.review import ReviewCreate, review
from src.database.enums import StepName
from src.database.crud.review_step import ReviewStepCreate, review_step
from src.database.models.review import ReviewStatus
from sqlalchemy.orm import Session


async def analyze_audit_url(
    url: str, model_name: str = "openai", debug: bool = False
) -> dict:
    """Run the complete analysis pipeline on a single audit URL"""
    print(f"Starting analysis of: {url}")

    if model_name:
        print(f"Using model from: {model_name}")

    # Create review entry in database
    db = get_db()
    review_obj = ReviewCreate(audit_url=url)
    db_review = review.create(db=db, obj_in=review_obj)

    if debug:
        print(
            f"Created review: ID={db_review.id}, URL={db_review.audit_url}, Status={db_review.status}"
        )

    print("Scraping content...")
    scraper = WebScraper(model_name=model_name)
    instructions = """
            Return the complete raw content of the webpage without any summarization,
            interpretation, or additional comments.
            Do not describe what you're doing, just output the exact text content.
        """
    webpage_content = await scraper.scrape(url=url, instructions=instructions)
    print("Content scraped successfully.")

    scraping_step_obj = ReviewStepCreate(
        review_id=db_review.id,
        name=StepName.SCRAPING,
        input=url,
        output=webpage_content.model_dump(),
        llm_model=model_name,
    )
    db_scraping_step = review_step.create(db=db, obj_in=scraping_step_obj)

    if debug:
        print(
            f"Created review step: ID={db_scraping_step.id}, "
            f"Review ID={db_scraping_step.id}, "
            f"Step Name={db_scraping_step.name}, "
            f"Input={db_scraping_step.input}, "
            f"Output={db_scraping_step.output}"
        )

    print("Analyzing for syntax issues...")
    scout = SyntaxScout(model_name=model_name)
    syntax_analysis = await scout.analyze(webpage_content.raw_content)

    syntax_step_obj = ReviewStepCreate(
        review_id=db_review.id,
        name=StepName.SYNTAX_CHECK,
        input=webpage_content.raw_content,
        output=syntax_analysis.model_dump(),
        llm_model=model_name,
    )
    db_syntax_step = review_step.create(db=db, obj_in=syntax_step_obj)

    if debug:
        print(
            f"Created review step: ID={db_syntax_step.id}, "
            f"Review ID={db_syntax_step.review_id}, "
            f"Step Name={db_syntax_step.name}, "
            f"Input={db_syntax_step.input}, "
            f"Output={db_syntax_step.output}"
        )

    # Run quality analysis
    print("Analyzing audit report quality...")
    quality_checker = AuditQualityChecker(model_name=model_name)
    quality_analysis = await quality_checker.analyze(webpage_content.raw_content)

    # Create review step entry in database
    quality_step_obj = ReviewStepCreate(
        review_id=db_review.id,
        name=StepName.QUALITY_CHECK,
        input=webpage_content.raw_content,
        output=quality_analysis.model_dump(),
        llm_model=model_name,
    )
    db_quality_step = review_step.create(db=db, obj_in=quality_step_obj)

    if debug:
        print(
            f"Created review step: ID={db_quality_step.id}, "
            f"Review ID={db_quality_step.review_id}, "
            f"Step Name={db_quality_step.name}, "
            f"Input={db_quality_step.input}, "
            f"Output={db_quality_step.output}"
        )

    print("Building consolidated review report...")
    report_builder = ReviewReportBuilder(model_name=model_name)
    review_report = await report_builder.build_report(syntax_analysis, quality_analysis)

    both_analysis_text = f"Syntax Analysis: {syntax_analysis.result}\nQuality Analysis: {quality_analysis}"

    report_step_obj = ReviewStepCreate(
        review_id=db_review.id,
        name=StepName.REPORT_GEN,
        input=both_analysis_text,
        output=review_report.model_dump(),
        llm_model=model_name,
    )
    db_report_step = review_step.create(db=db, obj_in=report_step_obj)

    if review_report.overall_score is not None:
        review.update_score(
            db=db, review_id=db_review.id, score=review_report.overall_score
        )

    if debug:
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
        f"Overall Assessment: {review_report.assessment} ({review_report.overall_score:.1f}/10)"
    )
    print(f"Full report saved to: {report_path}")

    _update_review_status(db=db, review_id=db_review.id)

    return 0


def _update_review_status(db: Session, review_id: int):
    """
    Check if all required steps are completed and update review status accordingly.
    Sets status to SUCCESS if all required steps are complete, otherwise FAILURE.
    """
    review_steps = review_step.get_by_review_id(db=db, review_id=review_id)

    required_steps = [
        StepName.SCRAPING,
        StepName.SYNTAX_CHECK,
        StepName.QUALITY_CHECK,
        StepName.REPORT_GEN,
    ]

    all_steps_completed = True
    for step_name in required_steps:
        step = next((s for s in review_steps if s.name == step_name), None)
        if not step or step.output is None:
            all_steps_completed = False
            break

    if all_steps_completed:
        review.update_status(db=db, review_id=review_id, status=ReviewStatus.SUCCESS)
    else:
        review.update_status(db=db, review_id=review_id, status=ReviewStatus.FAILURE)
