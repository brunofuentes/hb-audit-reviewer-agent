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
        # SYSTEM MESSAGE
        You are a professional copywriter and text quality reviewer specializing in technical documentation. 
        Your job is ONLY to evaluate the writing quality, clarity, readability, grammar, and presentation of the text.
        You are NOT a security auditor or technical analyst - do not comment on or evaluate the technical content or security findings described in the text.
        Focus exclusively on how well the information is communicated, not whether the information itself is correct.

        Generate a comprehensive text review report based on the webpage content following analysis:

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
        
        # YOUR TASK
        First, evaluate all text-related issues from both analyses:
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

        # IMPORTANT GUIDELINES
        Severity levels:
         - Critical: Significant text issues that severely impact understanding (e.g., contradictions, missing crucial information)
         - High: Important text problems that should be addressed promptly (e.g., unclear explanations, confusing structure)
         - Medium: Issues that affect text quality but don't compromise overall understanding (e.g., minor awkward phrasing)
         - Low: Minor text improvements or style suggestions (e.g., word choice, formatting inconsistencies)

        For the "report" field:
        - Use proper markdown formatting with headers (##), bullet points, and emphasis
        - Include sections for critical text issues, improvements, and recommendations
        - Act only as a text reviewer/copywriter, NOT a security analyst or technical auditor
        - Add a summary section that highlights the most important text quality findings
        - Add a "Found Issues" section that lists only the text-related issues from both analyses. Keep all text quality issues, unless they are the same issue. DO NOT include any security or technical issues related to the audit's findings.

        For the "issues" field:
        - Keep all original key-value pairs from both analyses that relate to text quality
        - Add a "severity" field to each issue if not present (Critical, High, Medium, or Low)
        - Sort issues from most critical to least critical
        - If an issue appears in both analyses, merge them and keep the higher severity level

        For the "overall_score" field, provide a numerical score from 0-10, where 10 is perfect text quality.

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

            # Parse the JSON content
            json_result = json.loads(content)

            # Add the issues as a code block to the report field if it exists
            if "report" in json_result and "issues" in json_result:
                # Create a JSON string representation of the issues
                issues_json = json.dumps(json_result["issues"], indent=2)

                # Add the issues as a markdown code block to the end of the report
                json_result[
                    "report"
                ] += f"\n\n## Raw Issues Data\n\n```json\n{issues_json}\n```"

            return ReviewReportBuilderOutput(
                result=content, json_result=json_result, error=None
            )
        except Exception as e:
            return ReviewReportBuilderOutput(
                result="Report building failed", error=str(e)
            )
