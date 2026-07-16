# app/llm/provider.py
import os
# from langchain_openai import ChatOpenAI
# Alternative: from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models import ActionPlan
from dotenv import load_dotenv

load_dotenv()

def get_llm_planner():
    """
    Initializes the LLM and forces it to strictly follow our ActionPlan schema.
    Make sure your API keys (e.g., OPENAI_API_KEY) are set in your environment.
    """
    # Using a capable reasoning/coding model variant

    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=0.7,
    )


        # Enforce structured output formatting mapping
    return llm.with_structured_output(ActionPlan)
