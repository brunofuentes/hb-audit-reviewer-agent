import enum


class StepName(enum.Enum):
    EXTRACT_CONTENT = "extract_content"
    SYNTAX_CHECK = "syntax_check"
    QUALITY_CHECK = "quality_check"
    REPORT_GEN = "report_gen"
