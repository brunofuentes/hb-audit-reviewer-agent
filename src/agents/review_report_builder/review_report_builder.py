from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from src.utils.get_langchain_llm import get_langchain_llm


class ReviewReportBuilder:
    def __init__(self, model_name: str = "openai"):
        self.llm = get_langchain_llm(model_name=model_name)
        self.agent = self._initialize_agent()

    def _create_report_tool(self) -> BaseTool:
        class ReportGenerationTool(BaseTool):
            name: str = "report_generator"
            description: str = (
                "Generate comprehensive review reports from analysis data"
            )

            def _run(self, text: str) -> str:
                return f"Generating report from {len(text)} characters of analysis..."

        return ReportGenerationTool()

    def _initialize_agent(self):
        tools = [self._create_report_tool()]
        agent = create_react_agent(self.llm, tools)
        return agent

    def _create_prompt(self, syntax_analysis: dict, quality_analysis: dict) -> str:
        """Create a prompt for generating a consolidated review report."""
        return f"""Generate a comprehensive review report based on the following analyses:

        SYNTAX ANALYSIS:
        ```
        {syntax_analysis['analysis_result']}
        ```

        QUALITY ANALYSIS:
        ```
        {quality_analysis['full_analysis']}
        ```

        Please create a concise, professional report that:
        1. Summarizes the key findings from both analyses
        2. Highlights the most critical issues that need attention
        3. Provides concrete recommendations for improvement
        4. Includes a brief assessment of overall report quality (using the structure score
        of {quality_analysis['structure_score']}/10 and clarity score of {quality_analysis['clarity_score']}/10)

        The report should be formatted for easy reading, with clear sections and professional language.
        Ensure the report is actionable and provides value to someone who wants to improve their audit report quality.
        Aim for a concise summary that doesn't exceed 1000 words.
        """

    async def build_report(self, syntax_analysis: dict, quality_analysis: dict) -> dict:
        """Build a consolidated review report from syntax and quality analyses."""
        prompt = self._create_prompt(syntax_analysis, quality_analysis)
        messages = [HumanMessage(content=prompt)]
        result = self.agent.invoke({"messages": messages})

        if "messages" in result and len(result["messages"]) > 0:
            report = result["messages"][-1].content

            overall_score = self._calculate_overall_score(quality_analysis)
            assessment = self._get_assessment(overall_score)

            return {
                "report": report,
                "overall_score": overall_score,
                "assessment": assessment,
                "structure_score": quality_analysis.get("structure_score", None),
                "clarity_score": quality_analysis.get("clarity_score", None),
                "has_major_issues": syntax_analysis.get("issues_detected", False)
                or quality_analysis.get("quality_issues_detected", False),
            }

        return {
            "report": "Unable to generate report",
            "overall_score": None,
            "assessment": "Unable to assess",
            "structure_score": None,
            "clarity_score": None,
            "has_major_issues": None,
        }

    def _calculate_overall_score(self, quality_analysis: dict) -> float:
        """Calculate overall score based on structure and clarity scores."""
        structure = quality_analysis.get("structure_score", 5.0)
        clarity = quality_analysis.get("clarity_score", 5.0)

        if structure is None and clarity is None:
            return 5.0
        elif structure is None:
            return clarity
        elif clarity is None:
            return structure

        # Weight structure slightly higher than clarity
        return (structure * 0.6) + (clarity * 0.4)

    def _get_assessment(self, score: float) -> str:
        """Get a qualitative assessment based on the overall score."""
        if score is None:
            return "Unable to assess"
        elif score >= 8.5:
            return "Excellent"
        elif score >= 7.0:
            return "Good"
        elif score >= 5.5:
            return "Adequate"
        elif score >= 4.0:
            return "Needs Improvement"
        else:
            return "Poor"
