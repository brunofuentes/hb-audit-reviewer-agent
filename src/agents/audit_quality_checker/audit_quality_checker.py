from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from src.utils.get_langchain_llm import get_langchain_llm


class AuditQualityChecker:
    def __init__(self, model_name: str = "openai"):
        self.llm = get_langchain_llm(model_name=model_name)
        self.agent = self._initialize_agent()

    def _create_analysis_tool(self) -> BaseTool:
        class AuditAnalysisTool(BaseTool):
            name: str = "audit_analysis"
            description: str = (
                "Analyze audit reports for quality, structure, and clarity"
            )

            def _run(self, text: str) -> str:
                return f"Analyzing audit report of {len(text)} characters..."

        return AuditAnalysisTool()

    def _initialize_agent(self):
        tools = [self._create_analysis_tool()]
        agent = create_react_agent(self.llm, tools)
        return agent

    def _create_prompt(self, audit_content: str) -> str:
        """Create a prompt for audit report quality analysis."""
        return f"""Analyze the following audit report for overall quality, structure, and clarity:

        Audit Report:
        '''
        {audit_content}
        '''

        Provide a comprehensive analysis covering:
        1. Structure Assessment:
           - Is the report well-structured with clear sections?
           - Are findings logically organized?
           - Is there a clear executive summary and conclusion?

        2. Language and Clarity:
           - Is the language accessible and easy to understand?
           - Are technical concepts explained adequately?
           - Is the report free of unnecessary jargon?

        3. Completeness:
           - Does the report cover all necessary aspects of an audit?
           - Are findings substantiated aligned with the methodology applied?
           - Are recommendations actionable and clear?

        4. Overall Quality:
           - General assessment of the report's professional quality
           - Strengths of the report
           - Areas needing improvement

        5. Improvement Suggestions:
           - Specific recommendations for enhancing the report's quality
           - Examples of how unclear sections could be rewritten
           - Structural changes that would improve readability

        Format your response as a structured evaluation with clear sections and actionable feedback.
        """

    async def analyze(self, audit_content: str) -> dict:
        """Analyze audit report content and return structured feedback."""
        prompt = self._create_prompt(audit_content=audit_content)
        messages = [HumanMessage(content=prompt)]
        result = self.agent.invoke({"messages": messages})

        # Extract the analysis from the result
        if "messages" in result and len(result["messages"]) > 0:
            analysis = result["messages"][-1].content

            # Structure the response as a dictionary
            return {
                "report_preview": (
                    audit_content[:100] + "..."
                    if len(audit_content) > 100
                    else audit_content
                ),
                "quality_issues_detected": (
                    True
                    if "improvement" in analysis.lower()
                    or "enhance" in analysis.lower()
                    or "lacking" in analysis.lower()
                    else False
                ),
                "structure_score": self._extract_structure_score(analysis),
                "clarity_score": self._extract_clarity_score(analysis),
                "full_analysis": analysis,
            }

        return {
            "report_preview": (
                audit_content[:100] + "..."
                if len(audit_content) > 100
                else audit_content
            ),
            "quality_issues_detected": False,
            "structure_score": None,
            "clarity_score": None,
            "full_analysis": "No analysis could be performed",
        }

    def _extract_structure_score(self, analysis: str) -> float:
        """Estimate a structure score from the analysis text (0.0-10.0)."""
        if (
            "well-structured" in analysis.lower()
            or "excellent structure" in analysis.lower()
        ):
            return 9.0
        elif "good structure" in analysis.lower() or "organized" in analysis.lower():
            return 7.5
        elif (
            "adequate structure" in analysis.lower()
            or "reasonable structure" in analysis.lower()
        ):
            return 6.0
        elif "poor structure" in analysis.lower() or "disorganized" in analysis.lower():
            return 3.5
        else:
            return 5.0  # Default middle score

    def _extract_clarity_score(self, analysis: str) -> float:
        """Estimate a clarity score from the analysis text (0.0-10.0)."""
        if "very clear" in analysis.lower() or "excellent clarity" in analysis.lower():
            return 9.0
        elif "clear" in analysis.lower() or "understandable" in analysis.lower():
            return 7.5
        elif (
            "somewhat clear" in analysis.lower()
            or "moderate clarity" in analysis.lower()
        ):
            return 6.0
        elif "unclear" in analysis.lower() or "confusing" in analysis.lower():
            return 3.5
        else:
            return 5.0  # Default middle score
