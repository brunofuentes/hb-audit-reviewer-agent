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
        {syntax_analysis.result}
        '''

        Quality Analysis:
        '''
        {quality_analysis.result}
        '''

        Return the review report in a JSON format with the following structure:

        {{
            "report": Consolidated report content, well formatted containing the list of issues in list format,
            "issues": List of all issues from both analysis, with a description of the issue and its severity,
            "overall_score": A score from 0-10, where 10 is perfect
        }}

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
