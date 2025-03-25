import os
import re


async def list_all_reports():
    """List all existing reports in the reports directory"""
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        print("No reports found.")
        return 0

    reports = [f for f in os.listdir(reports_dir) if f.endswith(".md")]

    if not reports:
        print("No reports found.")
        return 0

    print(f"Found {len(reports)} reports:")
    for i, report in enumerate(reports, 1):
        print(f"{i}. {report}")

    print("\nUse 'summary <report_path>' to view a report summary")
    print("Use 'view <report_path>' to view the full report")

    return 0


async def get_report_summary(report_path):
    """Extract and display the summary of a report"""
    try:
        with open(report_path, "r") as f:
            content = f.read()

        # Extract and print the overall assessment line
        assessment_match = re.search(r"\*\*Overall Assessment:\*\* (.*)", content)
        if assessment_match:
            print(f"Report: {os.path.basename(report_path)}")
            print(f"Assessment: {assessment_match.group(1)}")
            print("\nUse 'view <report_path>' to see the full report")
        else:
            print("Couldn't parse the report format.")

    except FileNotFoundError:
        print(f"Error: Report {report_path} not found")

    return 0


async def get_full_report(report_path):
    """Display the full content of a report"""
    try:
        with open(report_path, "r") as f:
            content = f.read()

        print(f"\n{'=' * 80}")
        print(f"REPORT: {os.path.basename(report_path)}")
        print(f"{'=' * 80}\n")
        print(content)

    except FileNotFoundError:
        print(f"Error: Report {report_path} not found")

    return 0
