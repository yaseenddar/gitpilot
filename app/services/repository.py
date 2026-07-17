import subprocess
from pathlib import Path
from typing import List, Optional
from app.models import RepositorySnapshot, FileChange

class GitService:
    def __init__(self, repo_path: str | Path):
        self.repo_path = Path(repo_path).resolve()
        if not (self.repo_path / ".git").exists():
            raise FileNotFoundError(f"No git repository found at {self.repo_path}")

    def _run_git(self, args: List[str]) -> str:
        """Helper to run a git command, forcing UTF-8 encoding to prevent Windows crash bugs."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                encoding="utf-8",  # <-- CRITICAL: Prevents cp1252 UnicodeDecodeError
                check=True
            )
            return result.stdout.strip() if result.stdout else ""
        except subprocess.CalledProcessError as e:
            # Safely decode stderr as well using utf-8 or fallback replacement
            error_msg = e.stderr.strip() if e.stderr else "Unknown Git Error"
            print(f"Git command error running {' '.join(args)}: {error_msg}")
            raise e

    def get_current_branch(self) -> str:
        return self._run_git(["branch", "--show-current"])

    def get_recent_commits(self, count: int = 5) -> List[str]:
        try:
            output = self._run_git(["log", f"-n", str(count), "--oneline"])
            return output.split("\n") if output else []
        except subprocess.CalledProcessError as e:
            # Safely fetch error message text
            err_str = e.stderr if isinstance(e.stderr, str) else ""
            if "fatal: your current branch" in err_str and "does not have any commits yet" in err_str:
                return [] 
            raise e
    def get_file_changes(self) -> tuple[List[FileChange], List[FileChange], List[FileChange]]:
        """Parses git status --porcelain to classify changed files."""
        staged = []
        unstaged = []
        untracked = []
        
        # --porcelain=v1 ensures machine-readable stable output
        status_lines = self._run_git(["status", "--porcelain=v1"])
        if not status_lines:
            return staged, unstaged, untracked
        print(f"###########: Status Lines: \n{status_lines}")
        for line in status_lines.split("\n"):
            if not line:
                continue
            
            # Index status (staged) and Working tree status (unstaged)
            xy = line[:2] 
            file_path = line[2:].strip()

            # Untracked files   
            if xy == "??":
                untracked.append(FileChange(path=file_path, status="untracked"))
                continue

            # Staged changes (X flag)
            if xy[0] in ["M", "A", "D", "R"]:
                status_map = {"M": "modified", "A": "staged", "D": "deleted", "R": "staged"}
                # Get the diff for staged changes
                diff = self._run_git(["diff", "--staged", "--", file_path])
                staged.append(FileChange(path=file_path, status=status_map.get(xy[0], "staged"), diff=diff))

            # Unstaged changes (Y flag)
            if xy[1] in ["M", "D"]:
                status_map = {"M": "modified", "D": "deleted"}
                diff = self._run_git(["diff", "--", file_path])
                unstaged.append(FileChange(path=file_path, status=status_map.get(xy[1], "modified"), diff=diff))
        print
        return staged, unstaged, untracked

    def get_snapshot(self) -> RepositorySnapshot:
        """Main orchestrator that constructs the full immutable state representation."""
        staged, unstaged, untracked = self.get_file_changes()
        has_changes = bool(staged or unstaged or untracked)
        
        return RepositorySnapshot(
            current_branch=self.get_current_branch(),
            has_changes=has_changes,
            staged_files=staged,
            unstaged_files=unstaged,
            untracked_files=untracked,
            recent_commits=self.get_recent_commits()
        )

    # Mutation Operations (To be wrapped by Executor nodes later)
    def stage_all(self):
        self._run_git(["add", "."])

    def stage_file(self, path: str):
        self._run_git(["add", path])

    def create_commit(self, message: str):
        self._run_git(["commit", "-m", message])

# test_git_service.py

if __name__ == "__main__":
    # Point this to a local test git repository 
    git_service = GitService(repo_path=".") 
    
    snapshot = git_service.get_snapshot() 
    
    print("--- REPOSITORY SNAPSHOT ---")
    print(f"Branch: {snapshot.current_branch}")
    print(f"Has changes: {snapshot.has_changes}")
    print(f"Staged Files Count: {len(snapshot.staged_files)}")
    print(f"Unstaged Files Count: {len(snapshot.unstaged_files)}")
    print(f"Recent Commits: {snapshot.recent_commits[:2]}")