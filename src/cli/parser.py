import argparse
from src.cli.commands import (
    run_analysis,
    list_reports,
    show_report_summary,
    view_full_report,
)


def create_parser():
    parser = argparse.ArgumentParser(description="Audit Report Reviewer CLI")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze an audit report")
    analyze_parser.add_argument("url", help="URL of the audit report to analyze")
    analyze_parser.add_argument(
        "--debug", action="store_true", help="Print debug information"
    )
    analyze_parser.set_defaults(func=run_analysis)

    # List reports command
    list_parser = subparsers.add_parser("list", help="List all reports")
    list_parser.set_defaults(func=list_reports)

    # View report summary
    summary_parser = subparsers.add_parser("summary", help="View a report summary")
    summary_parser.add_argument("report_path", help="Path to the report file")
    summary_parser.set_defaults(func=show_report_summary)

    # View full report
    view_parser = subparsers.add_parser("view", help="View a full report")
    view_parser.add_argument("report_path", help="Path to the report file")
    view_parser.set_defaults(func=view_full_report)

    return parser
