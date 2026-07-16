from typing import TypedDict, List, Optional
from langchain_core.messages import BaseMessage
from app.models import RepositorySnapshot, ActionPlan

class GitAgentState(TypedDict):
    # Context
    repository_path: str
    
    # Snapshot of the current local state
    snapshot: Optional[RepositorySnapshot]
    
    # The evaluation/decision from the LLM
    plan: Optional[ActionPlan]
    
    # Execution logs and verification
    execution_result: Optional[dict]
    is_verified: bool
    
    # LangChain message tracking (optional, useful if debugging decision loops)
    messages: List[BaseMessage]