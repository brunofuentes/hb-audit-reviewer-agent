from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv

load_dotenv()


def get_langchain_llm(model_name="openai"):
    """Get the LangChain LLM based on the chosen model name.

    Args:
        model_name (str): The name of the model to use - "gemini", "claude", or "openai"

    Returns:
        The LangChain model instance configured for use
    """
    models = {
        "anthropic": ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            temperature=0,
        ),
        "openai": ChatOpenAI(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0,
        ),
    }

    return models.get(model_name.lower(), models["openai"])
