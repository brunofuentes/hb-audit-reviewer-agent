from src.core.analyzer import analyze_audit_url
from src.core.report import list_all_reports, get_report_summary, get_full_report


async def run_analysis(args):
    """Run full analysis on an audit URL"""
    return await analyze_audit_url(url=args.url, debug=args.debug)


async def list_reports(args):
    """List all existing reports"""
    return await list_all_reports()


async def show_report_summary(args):
    """Display a summary of an existing report"""
    return await get_report_summary(args.report_path)


async def view_full_report(args):
    """Display the full content of a report"""
    return await get_full_report(args.report_path)
