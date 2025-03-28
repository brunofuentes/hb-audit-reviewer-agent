import os
import re
import datetime
from urllib.parse import urlparse
from src.agents.schemas import ReviewReportBuilderOutput


def save_report(url: str, review_report: ReviewReportBuilderOutput):
    """Save report to a file with a formatted name based on URL"""
    parsed_url = urlparse(url)
    url_path = parsed_url.path
    last_path_part = os.path.basename(url_path)

    clean_filename = re.sub(r"[^\w\-]", "_", last_path_part)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{clean_filename}_{timestamp}.md"

    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    report_path = os.path.join(reports_dir, filename)

    with open(report_path, "w") as f:
        f.write("# Audit Report Review\n\n")
        f.write(
            f"**Overall Assessment:** {review_report.json_result['overall_score']}\n\n"
        )
        f.write(review_report.json_result["report"])

    return report_path
