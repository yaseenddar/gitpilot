# app/services/policy.py
import re
from typing import Tuple, List
from app.models import ActionPlan, RepositorySnapshot

class PolicyService:
    # A list of common patterns that should NEVER be committed
    BLOCKED_PATTERNS = [
        (re.compile(r"sk-[a-zA-Z0-9]{48}"), "OpenAI API Key leaked"),
        (re.compile(r"AIzaSy[a-zA-Z0-9-_]{35}"), "Google API Key leaked"),
        (re.compile(r"pdb\.set_trace\(\)"), "Leftover Python debugger breakpoint"),
        (re.compile(r"print\("), "Debug print statement detected (use logging instead)")
    ]

    @classmethod
    def evaluate(cls, plan: ActionPlan, snapshot: RepositorySnapshot) -> Tuple[bool, List[str]]:
        """
        Evaluates the plan and snapshot against the project policies.
        Returns (is_allowed, list_of_violations).
        """
        violations = []

        # Rule 1: Prevent empty or placeholder commits
        if plan.action == "commit":
            msg = plan.parameters.get("commit_message", "")
            if len(msg) < 10:
                violations.append("Commit message is too short (must be at least 10 characters).")
            if not any(msg.startswith(prefix) for prefix in ["feat", "fix", "chore", "docs", "refactor", "style", "test"]):
                violations.append("Commit message does not follow Conventional Commits format (e.g., 'feat(auth): ...').")

        # Rule 2: Scan active diffs for credentials or debug artifacts
        for change in snapshot.unstaged_files + snapshot.staged_files:
            if not change.diff:
                continue
            
            # Check only added lines (lines starting with '+') to avoid flagging existing code
            added_lines = [line for line in change.diff.split("\n") if line.startswith("+") and not line.startswith("+++")]
            
            for line in added_lines:
                for pattern, description in cls.BLOCKED_PATTERNS:
                    if pattern.search(line):
                        violations.append(f"Security/Style violation in {change.path}: {description}")

        is_allowed = len(violations) == 0
        return is_allowed, violations