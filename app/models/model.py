from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class FileChange(BaseModel):
    path: str
    status: Literal["modified", "untracked", "deleted", "staged"]
    diff: Optional[str] = None

class RepositorySnapshot(BaseModel):
    current_branch: str
    has_changes: bool
    staged_files: List[FileChange] = []
    unstaged_files: List[FileChange] = []
    untracked_files: List[FileChange] = []
    recent_commits: List[str] = Field(..., description="Last 3-5 commit hashes and messages")

class ActionPlan(BaseModel):
    action: Literal["commit", "suggest_branch", "generate_docs", "none"]
    reason: str = Field(..., description="Justification for why this action is necessary or why no action is taken.")
    confidence: float = Field(..., description="Value between 0.0 and 1.0 indicating decision confidence.")
    parameters: dict = Field(default_factory=dict, description="Arguments for tools, e.g., {'commit_message': '...'} or {'branch_name': '...'}")
    summary: str = Field(description="if need return make the updated summary for the changes to to for next context and return summary modified true")
    summary_modified:bool = Field(description="return true for summary modifed")