import os
import re
import datetime
from urllib.parse import urlparse


def save_report(url, review_report):
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
            f"**Overall Assessment:** {review_report['assessment']} ({review_report['overall_score']:.1f}/10)\n\n"
        )
        f.write(review_report["report"])

    return report_path
