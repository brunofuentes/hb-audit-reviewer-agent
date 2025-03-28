from src.utils.get_langchain_llm import get_langchain_llm
from src.agents.schemas import (
    SyntaxScoutOutput,
    AuditQualityCheckerOutput,
    ReviewReportBuilderOutput,
)
import json


class ReviewReportBuilder:
    def __init__(self, model_name: str = "openai-json"):
        self.llm = get_langchain_llm(model_name=model_name)

    def _create_prompt(
        self,
        webpage_content: str,
        syntax_analysis: SyntaxScoutOutput,
        quality_analysis: AuditQualityCheckerOutput,
    ) -> str:
        """Create a prompt for generating a consolidated review report."""
        return f"""
        
        Generate a comprehensive review report based on the webpage content following analysis:

        Webpage Content:
        '''
        {webpage_content}
        '''

        Syntax Analysis:
        '''
        {syntax_analysis.json_result["issues"]}
        '''

        Quality Analysis:
        '''
        {quality_analysis.json_result["issues"]}
        '''

        First, evaluate all issues from both analyses:
        - Remove any issues that don't make sense in context
        - Filter out vague or poorly defined issues
        - Resolve contradictions between the two analyses (if any)
        - Ensure each issue is actionable and clear

        Return the review report in a JSON format with the following structure:

        {{
            "report": Consolidated report content, well formatted containing the list of issues in list format,
            "issues": [
                {{
                    // Maintain all original key-value pairs from the source issue
                    // Add a severity field if not already present
                    "severity": "Critical/High/Medium/Low"
                }}
            ],
            "overall_score": A score from 0-10, where 10 is perfect
        }}

           Severity levels:
            - Critical: Issues that significantly impact security, functionality, or credibility
            - High: Important problems that should be addressed promptly
            - Medium: Issues that affect quality but don't compromise core functionality
            - Low: Minor improvements or style suggestions

        For the "report" field:
        - Use proper markdown formatting with headers (##), bullet points, and emphasis
        - Include sections for critical issues, improvements, and recommendations
        - Add a summary section that highlights the most important findings
        - Add a "Found Issues" section that lists the issues of the issues field and
            its key-value pairs as bullet points

        For the "issues" field:
        - Keep all original key-value pairs from both analyses
        - Add a "severity" field to each issue if not present (Critical, High, Medium, or Low)
        - Sort issues from most critical to least critical
        - If an issue appears in both analyses, merge them and keep the higher severity level

        For the "overall_score" field, provide a numerical score from 0-10, where 10 is perfect.

        Do not include any other explanation or formatting outside of this JSON structure.
        """

    def get_prompt(
        self,
        webpage_content: str,
        syntax_analysis: SyntaxScoutOutput,
        quality_analysis: AuditQualityCheckerOutput,
    ) -> str:
        """Get the prompt for generating a consolidated review report."""
        return self._create_prompt(
            webpage_content=webpage_content,
            syntax_analysis=syntax_analysis,
            quality_analysis=quality_analysis,
        )

    async def build_report(
        self,
        webpage_content: str,
        syntax_analysis: SyntaxScoutOutput,
        quality_analysis: AuditQualityCheckerOutput,
    ) -> ReviewReportBuilderOutput:
        """Build a consolidated review report from syntax and quality analyses."""
        prompt = self._create_prompt(
            webpage_content=webpage_content,
            syntax_analysis=syntax_analysis,
            quality_analysis=quality_analysis,
        )

        try:

            response = self.llm.invoke(prompt)
            content = response.content

            return ReviewReportBuilderOutput(
                result=content, json_result=json.loads(content), error=None
            )
        except Exception as e:
            return ReviewReportBuilderOutput(
                result="Report building failed", error=str(e)
            )
