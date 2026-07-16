from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage
from app.models import RepositorySnapshot, ActionPlan

class GitAgentState(TypedDict):
    repository_path: str
    snapshot: Optional[RepositorySnapshot]
    plan: Optional[ActionPlan]
    execution_result: Optional[dict]
    is_verified: bool
    messages: List[BaseMessage]