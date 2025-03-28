from src.utils.get_langchain_llm import get_langchain_llm
from src.agents.schemas import AuditQualityCheckerOutput
import json


class AuditQualityChecker:
    def __init__(self, model_name: str = "openai-json-temp-05"):
        self.llm = get_langchain_llm(model_name=model_name)

    def _create_prompt(self, audit_content: str) -> str:
        """Create a prompt for audit report quality analysis."""
        return f"""
        Analyze the following audit report for problems related to:
        - Risk Methodology
        - Comprehensiveness
        - Findings Methodology Alignment

        Audit Report:
        '''
        {audit_content}
        '''
        
        Perform a critical analysis focused on identifying problems and return results in JSON format
        with the following structure:
        
        {{
            "issues": [
                {{
                    "type": "risk_methodology",
                    "issue": "Clear description of the specific problem",
                    "location": "Quote of the problematic text",
                    "explanation": "Brief explanation of why this is a problem"
                }},
                {{
                    "type": "comprehensiveness",
                    "issue": "Clear description of the specific problem",
                    "location": "Quote of the problematic text",
                    "explanation": "Brief explanation of why this is a problem"
                }},
                {{
                    "type": "findings_methodology_alignment",
                    "issue": "Clear description of the specific problem",
                    "location": "Quote of the problematic text",
                    "explanation": "Brief explanation of why this is a problem"
                }}
            ],
            "semantic_recommendations": [
                "Specific, actionable recommendation for improving the text",
                "Another specific recommendation for improvement",
                "A third recommendation focused on semantic clarity"
            ],
            "summary": "Brief summary of the most critical issues (max 3 sentences)",
            "score": 7 // A score from 1-10, where 10 is perfect
        }}
        
        For the issues array, only include items that represent actual problems found.
        Each issue must have a specific type from the list:
        - risk_methodology
        - comprehensiveness
        - findings_methodology_alignment

        The issues must only be about the audit report, not the audit process itself.
        Quote the exact problematic text rather than describing its location.
        Provide 3-5 specific semantic recommendations as simple strings.
        Limit your analysis to the most significant issues (max 10 total issues).
        Be critical and thorough in identifying problems.
        Do not include any other explanation or formatting outside of this JSON structure.
        """

    def get_prompt(self, audit_content: str) -> str:
        """Get the prompt for audit report quality analysis."""
        return self._create_prompt(audit_content=audit_content)

    async def analyze(self, audit_content: str) -> AuditQualityCheckerOutput:
        """Analyze audit report content and return structured feedback."""
        prompt = self._create_prompt(audit_content=audit_content)

        try:
            response = self.llm.invoke(prompt)
            analysis = response.content

            return AuditQualityCheckerOutput(
                result=analysis,
                json_result=json.loads(analysis),
                error=None,
            )

        except Exception as e:
            return AuditQualityCheckerOutput(
                result="Analysis failed",
                json_result=None,
                error=str(e),
            )
