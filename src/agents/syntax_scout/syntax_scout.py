from src.utils.get_langchain_llm import get_langchain_llm
from src.agents.schemas import SyntaxScoutOutput
import json


class SyntaxScout:
    def __init__(self, model_name: str = "openai-json"):
        self.llm = get_langchain_llm(model_name=model_name)

    def _create_prompt(self, text_content: str) -> str:
        """Create a prompt for linguistic analysis."""
        return f"""Analyze the following text for linguistic syntax errors, grammar issues, and potential improvements:

        Text to analyze:
        '''
        {text_content}
        '''
        Perform a comprehensive linguistic analysis and return results in a JSON format with the following structure:
        
        {{
            "issues": [
                {{
                    "type": "grammar",
                    "issue": "Exact issue description",
                    "location": "Quote of the problematic text",
                    "correction": "Full corrected version",
                    "explanation": "Brief explanation of why this is an issue"
                }},
                {{
                    "type": "punctuation",
                    "issue": "Exact issue description",
                    "location": "Quote of the problematic text",
                    "correction": "Full corrected version",
                    "explanation": "Brief explanation of why this is an issue"
                }},
                {{
                    "type": "spelling",
                    "issue": "Exact issue description",
                    "location": "Quote of the problematic text",
                    "correction": "Full corrected version",
                    "explanation": "Brief explanation of why this is an issue"
                }},
                {{
                    "type": "style",
                    "issue": "Exact issue description",
                    "location": "Quote of the problematic text",
                    "correction": "Full corrected version",
                    "explanation": "Brief explanation of why this is an issue"
                }}
            ],
            "summary": "Brief summary of most critical issues (max 3) and overall assessment",
            "score": 7 // A score from 1-10, where 10 is perfect
        }}
        
        For the issues array, only include items that represent actual issues found.
        Quote the exact problematic text rather than describing its location.
        For each issue, provide the full corrected version of the text.
        Limit your analysis to the most significant issues (max 15 total issues).
        Do not include any other explanation or formatting outside of this JSON structure.
        """

    def get_prompt(self, text_content: str) -> str:
        """Get the prompt for linguistic analysis."""
        return self._create_prompt(text_content=text_content)

    async def analyze(self, text_content: str) -> SyntaxScoutOutput:
        """Analyze text content and return structured feedback."""
        prompt = self._create_prompt(text_content=text_content)

        try:
            response = self.llm.invoke(prompt)
            analysis = response.content

            return SyntaxScoutOutput(
                result=analysis,
                json_result=json.loads(analysis),
                error=None,
            )
        except Exception as e:
            return SyntaxScoutOutput(result="Analysis failed", error=str(e))
