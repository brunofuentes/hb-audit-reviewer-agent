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

    # Create review entry in database
    db = get_db()
    review_obj = ReviewCreate(audit_url=url)
    db_review = review.create(db=db, obj_in=review_obj)

    scraper_model_name = "openai"
    model_name_syntax = "openai-json"
    model_name_quality = "openai-json-temp-03"
    model_name_report = "openai-json"

    if debug:
        print(
            f"Created review: ID={db_review.id}, URL={db_review.audit_url}, Status={db_review.status}"
        )

    print("Scraping content...")

    scraper = WebScraper(model_name=scraper_model_name)
    webpage_content = await scraper.scrape(url=url)
    print("Content scraped successfully.")

    scraping_step_obj = ReviewStepCreate(
        review_id=db_review.id,
        name=StepName.SCRAPING,
        input=scraper.get_prompt(url),
        output=webpage_content.model_dump(),
        llm_model=scraper_model_name,
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

    scout = SyntaxScout(model_name=model_name_syntax)
    quality_checker = AuditQualityChecker(model_name=model_name_quality)
    report_builder = ReviewReportBuilder(model_name=model_name_report)

    print("Analyzing for syntax issues...")
    syntax_analysis = await scout.analyze(webpage_content.raw_content)

    syntax_step_obj = ReviewStepCreate(
        review_id=db_review.id,
        name=StepName.SYNTAX_CHECK,
        input=scout.get_prompt(webpage_content.raw_content),
        output=syntax_analysis.json_result,
        llm_model=model_name_syntax,
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
    quality_analysis = await quality_checker.analyze(webpage_content.raw_content)

    # Create review step entry in database
    quality_step_obj = ReviewStepCreate(
        review_id=db_review.id,
        name=StepName.QUALITY_CHECK,
        input=quality_checker.get_prompt(webpage_content.raw_content),
        output=quality_analysis.json_result,
        llm_model=model_name_quality,
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
    review_report = await report_builder.build_report(
        webpage_content=webpage_content.raw_content,
        syntax_analysis=syntax_analysis,
        quality_analysis=quality_analysis,
    )

    report_step_obj = ReviewStepCreate(
        review_id=db_review.id,
        name=StepName.REPORT_GEN,
        input=report_builder.get_prompt(
            webpage_content=webpage_content.raw_content,
            syntax_analysis=syntax_analysis,
            quality_analysis=quality_analysis,
        ),
        output=review_report.json_result,
        llm_model=model_name_report,
    )

    db_report_step = review_step.create(db=db, obj_in=report_step_obj)

    if review_report.json_result and "overall_score" in review_report.json_result:
        review.update_score(
            db=db,
            review_id=db_review.id,
            score=review_report.json_result["overall_score"],
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
    print(f"Overall score: {review_report.json_result['overall_score']}")
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
