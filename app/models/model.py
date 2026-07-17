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

from pydantic import BaseModel, Field
from typing import Literal

# app/state/models.py
from pydantic import BaseModel, Field
from typing import Literal

class ActionPlan(BaseModel):
    action: Literal["commit", "suggest_branch", "generate_docs", "none"]
    reason: str = Field(..., description="Justification for why this action is necessary or why no action is taken.")
    confidence: float = Field(..., description="Value between 0.0 and 1.0 indicating decision confidence.")
    parameters: dict = Field(default_factory=dict, description="Arguments for tools, e.g., {'commit_message': '...'} or {'branch_name': '...'}")
    
    summary_modified: bool = Field(
        default=False, 
        description=(
            "Set to true ONLY if a new file, new module, or significant architectural change "
            "has occurred that needs to be documented in the README map. Otherwise, set to false."
        )
    )
    summary: str = Field(
        default="", 
        description=(
            "If summary_modified is true, provide the updated Markdown summary mapping the new modules/files. "
            "If summary_modified is false, this field MUST be an empty string (''). Do not write anything here."
        )
    )