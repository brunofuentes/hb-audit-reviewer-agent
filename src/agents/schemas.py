from pydantic import BaseModel, Field
from typing import Optional


class WebScraperOutput(BaseModel):
    """Output schema for web scraper agent"""

    raw_content: str = Field(description="Raw content retrieved from the webpage")
    error: Optional[str] = Field(
        default=None, description="Error message if scraping failed"
    )


class BaseAgentOutput(BaseModel):
    """Base output schema for all agents"""

    result: str = Field(description="The full analysis result or explanation")
    error: Optional[str] = Field(
        default=None, description="Error message if analysis failed"
    )


class SyntaxScoutOutput(BaseAgentOutput):
    """Output schema for syntax scout agent"""

    json_result: Optional[dict] = Field(
        default=None,
        description="Structured analysis of the result",
    )


class AuditQualityCheckerOutput(BaseAgentOutput):
    """Output schema for audit quality checker agent"""

    json_result: Optional[dict] = Field(
        default=None,
        description="Structured analysis of the result",
    )


class ReviewReportBuilderOutput(BaseAgentOutput):
    """Output schema for review report builder agent"""

    structure_score: Optional[float] = Field(
        default=None, description="Score for the structure of the audit report"
    )
    clarity_score: Optional[float] = Field(
        default=None, description="Score for the clarity of the audit report"
    )

    overall_score: Optional[float] = Field(
        default=None, description="Overall score for the audit report"
    )
    assessment: Optional[str] = Field(
        default=None, description="Assessment of the audit report"
    )
