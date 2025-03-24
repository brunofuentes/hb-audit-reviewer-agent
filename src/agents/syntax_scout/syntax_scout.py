from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from src.utils.get_langchain_llm import get_langchain_llm


class SyntaxScout:
    def __init__(self, model_name: str = "openai"):
        self.llm = get_langchain_llm(model_name=model_name)
        self.agent = self._initialize_agent()

    def _create_analysis_tool(self) -> BaseTool:
        class TextAnalysisTool(BaseTool):
            name: str = "text_analysis"
            description: str = (
                "Analyze text for linguistic syntax errors and potential improvements"
            )

            def _run(self, text: str) -> str:
                return f"Analyzing text of {len(text)} characters..."

        return TextAnalysisTool()

    def _initialize_agent(self):
        tools = [self._create_analysis_tool()]
        agent = create_react_agent(self.llm, tools)
        return agent

    def _create_prompt(self, text_content: str) -> str:
        """Create a prompt for linguistic analysis."""
        return f"""Analyze the following text for linguistic syntax errors, grammar issues, and potential improvements:

        Text to analyze:
        '''
        {text_content}
        '''

        Provide a detailed report with:
        1. A list of any grammar errors found (specify line or sentence)
        2. Punctuation errors
        3. Spelling mistakes
        4. Awkward phrasings or unclear sentences
        5. Style and consistency issues
        6. Specific suggestions for improving each identified issue

        Format your response as a structured list of issues and recommendations.
        """

    async def analyze(self, text_content: str) -> dict:
        """Analyze text content and return structured feedback."""
        prompt = self._create_prompt(text_content=text_content)
        messages = [HumanMessage(content=prompt)]
        result = self.agent.invoke({"messages": messages})

        # Extract the analysis from the result
        if "messages" in result and len(result["messages"]) > 0:
            analysis = result["messages"][-1].content

            # Structure the response as a dictionary
            return {
                "raw_text": (
                    text_content[:100] + "..."
                    if len(text_content) > 100
                    else text_content
                ),
                "issues_detected": (
                    True
                    if "error" in analysis.lower() or "issue" in analysis.lower()
                    else False
                ),
                "analysis_result": analysis,
            }

        return {
            "raw_text": (
                text_content[:100] + "..." if len(text_content) > 100 else text_content
            ),
            "issues_detected": False,
            "analysis_result": "No analysis could be performed",
        }
