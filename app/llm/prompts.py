# app/llm/prompts.py
from langchain_core.prompts import ChatPromptTemplate

PLANNER_SYSTEM_PROMPT = """
You are GitPilot, an elite autonomous DevOps agent.
Your goal is to evaluate the provided local file changes against the high-level project architecture and formulate a clean conventional commit.

Rules:
1. "commit" - Use this if there are active, uncommitted changes that represent a logical piece of work.
2. "none" - Use this if the changes are empty, trivial, or do not warrant a commit.

Commit Message Format:
Follow the Conventional Commits specification (e.g., feat(graph): add node execution limits). Be highly descriptive based on the diff.
"""

def get_planner_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages([
        ("system", PLANNER_SYSTEM_PROMPT),
        ("human", """
Here is the high-level overview of the project we are building:
=========================================
{project_readme}
=========================================

And here are the EXACT lines of code that were changed in this workspace event:
=========================================
{changed_lines_diff}
=========================================

Formulate your action plan now.
""")
    ])