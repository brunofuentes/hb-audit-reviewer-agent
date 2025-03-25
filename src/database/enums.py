import enum


class StepName(enum.Enum):
    SCRAPING = "scraping"
    SYNTAX_CHECK = "syntax_check"
    QUALITY_CHECK = "quality_check"
    REPORT_GEN = "report_gen"
