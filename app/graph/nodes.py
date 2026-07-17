from app.state.agent_state import GitAgentState
from app.services.repository import GitService
from app.llm.provider import get_llm_planner
from app.llm.prompts import get_planner_prompt
from app.models import ActionPlan
from app.services.policy import PolicyService
from pathlib import Path
from rich import print
import json
import os
import re
def get_project_readme() -> str:
    readme_path = Path(__file__).resolve().parent.parent / "context" / "CONTEXT.md"
    if readme_path.exists():
        try:
            content = readme_path.read_text(encoding="utf-8")
            return content[:1500] if len(content) > 1500 else content
        except Exception:
            pass
    return "GitPilot: An autonomous local Git agent workflow."

def observe_node(state: GitAgentState) -> dict:
    print("\n🔍 [Node: Observe] Fetching repository snapshot context...")
    service = GitService(state["repository_path"])
    return {"snapshot": service.get_snapshot()}

def plan_node(state: GitAgentState) -> dict:
    snapshot = state["snapshot"]
    
    if not snapshot:
        raise ValueError("No repository snapshot available to reason over.")

    # 1. Local Guard: Skip entirely if there are no changes
    if not snapshot.has_changes:
        print("🧠 [Node: Plan] Local Guard: Repository is clean. Skipping LLM call.")
        return {"plan": ActionPlan(action="none", reason="No pending changes.", confidence=1.0, parameters={})}

    # ─── 2. DEBUG MODE SHORT-CIRCUIT (NO LLM CALL) ───
    if os.getenv("GITPILOT_DEBUG") == "0":
        print("🛠️ [Node: Plan] [DEBUG MODE] Simulating reasoning flow locally...")
        
        # Look at the first changed file to formulate a fake but realistic conventional commit
        sample_file = (snapshot.unstaged_files + snapshot.staged_files + snapshot.untracked_files)[0]
        file_name = Path(sample_file.path).name
        parent_dir = Path(sample_file.path).parent.name or "workspace"
        
        # Auto-generate a dummy conventional commit plan
        plan = ActionPlan(
            action="commit",
            reason=f"Offline Debugging: Detected modifications in '{file_name}' under '{parent_dir}'.",
            confidence=1.0,
            parameters={
                "commit_message": f"chore({parent_dir}): update {file_name} (offline debug sync)"
            }
        )
        
        print(f"   👉 Debug Decision: {plan.action.upper()}")
        print(f"   👉 Reason: {plan.reason}")
        print(f"   👉 Mock Parameters: {json.dumps(plan.parameters)}")
        return {"plan": plan}
    # ─────────────────────────────────────────────────

    # 3. Standard Live LLM Chain Path
    print("🧠 [Node: Plan] Passing README map and exact diff lines to LLM...")
    diff_lines = []
    for f in snapshot.unstaged_files + snapshot.staged_files:
        if f.diff:
            relevant_lines = [line for line in f.diff.split("\n") if line.startswith("+") or line.startswith("-")]
            diff_lines.append(f"File: {f.path}\nChanges:\n" + "\n".join(relevant_lines[:50]))

    changed_lines_diff = "\n\n".join(diff_lines) if diff_lines else "No line-level changes detected."
    project_readme = get_project_readme()
    # print(f"############# Lines changed \n {changed_lines_diff}")
    prompt_template = get_planner_prompt()
    llm_planner = get_llm_planner()
    # print(f" ####### Summary project \n {project_readme}")
    # print(f" ####### whole prompt \n {changed_lines_diff}")

    chain = prompt_template | llm_planner
    print(f"&&&&&&&&&&&&&&& Changed LInes \n{changed_lines_diff}")
    plan = chain.invoke({
        "project_readme": project_readme,
        "changed_lines_diff": changed_lines_diff
    })
    print(f"############: LLm Response \n{plan}\n\n")
    print(f"   👉 LLM Decision: {plan.action.upper()}")
    print(f"   👉 Reason: {plan.reason}")
    if plan.parameters:
        print(f"   👉 Parameters: {json.dumps(plan.parameters)}")
    
    return {"plan": plan}

def update_readme_summary(new_summary: str):
    """
    Slices the new summary cleanly into README.md under an 'Active Feature Map' 
    header instead of wiping the entire document.
    """
    readme_path =Path(__file__).resolve().parent.parent / "context" / "CONTEXT.md"
    header_marker = "## Active Feature Map"
    
    if not readme_path.exists():
        # Fallback if README doesn't exist
        readme_path.write_text(f"# GitPilot Workspace\n\n{header_marker}\n{new_summary}\n", encoding="utf-8")
        return

    content = readme_path.read_text(encoding="utf-8")
    
    # Format the incoming summary neatly
    formatted_section = f"{header_marker}\n{new_summary}\n"

    if header_marker in content:
        # Regex to replace everything from '## Active Feature Map' down to the next major header (##) or end of file
        pattern = re.compile(rf"{header_marker}.*?(?=\n## |$)", re.DOTALL)
        updated_content = pattern.sub(formatted_section.strip(), content)
    else:
        # If the header doesn't exist, append it cleanly to the end of the file
        updated_content = content.rstrip() + f"\n\n{formatted_section}"

    readme_path.write_text(updated_content, encoding="utf-8")


def execute_node(state: GitAgentState) -> dict:
    print("🚀 [Node: Execute] Performing planned operations...")
    plan = state["plan"]
    snapshot = state["snapshot"]
    service = GitService(state["repository_path"])
    
    if not plan or plan.action == "none":
        return {"execution_result": {"status": "skipped", "message": "No action required"}}
        
    # ─── 1. POLICY ENFORCEMENT ───
    is_allowed, violations = PolicyService.evaluate(plan, snapshot)
    if not is_allowed:
        print("⚠️ [Policy Block] The action plan failed security/policy verification:")
        for violation in violations:
            print(f"   ❌ {violation}")
        return {"execution_result": {"status": "blocked", "error": "Policy violation", "violations": violations}}

    # ─── 2. SUMMARY UPDATE ENFORCEMENT ───
    if plan.summary_modified and plan.summary:
        print("📝 [Node: Execute] Splicing new architecture update into CONTEXT.md...")
        update_readme_summary(plan.summary)

    # ─── 3. COMMIT EXECUTION ───
    if plan.action == "commit":
        msg = plan.parameters.get("commit_message", "chore: auto sync workspace state")
        print(f"   Staging files and executing live commit: '{msg}'")
        service.stage_all()
        service.create_commit(msg)
        return {"execution_result": {"status": "success", "action": "commit"}}
        
    return {"execution_result": {"status": "failed", "error": "Unknown action"}}


def verify_node(state: GitAgentState) -> dict:
    print("✅ [Node: Verify] Checking post-execution repository stability...")
    service = GitService(state["repository_path"])
    post_snapshot = service.get_snapshot()
    
    plan = state["plan"]
    if plan and plan.action == "commit":
        is_verified = not post_snapshot.has_changes
    else:
        is_verified = True
        
    print(f"   Status Verified: {is_verified}")
    return {"is_verified": is_verified}

# app/graph/nodes.py (Update execute_node)

def execute_node(state: GitAgentState) -> dict:
    print("🚀 [Node: Execute] Performing planned operations...")
    plan = state["plan"]
    snapshot = state["snapshot"]
    service = GitService(state["repository_path"])
    
    if not plan or plan.action == "none":
        return {"execution_result": {"status": "skipped", "message": "No action required"}}
        
    # ─── POLICY ENFORCEMENT ───
    is_allowed, violations = PolicyService.evaluate(plan, snapshot)
    if not is_allowed:
        print("⚠️ [Policy Block] The action plan failed security/policy verification:")
        for violation in violations:
            print(f"   ❌ {violation}")
        return {
            "execution_result": {
                "status": "blocked", 
                "error": "Policy violation", 
                "violations": violations
            }
        }
    # ──────────────────────────

    if plan.action == "commit":
        msg = plan.parameters.get("commit_message")
        print(f"   Staging files and executing live commit: '{msg}'")
        service.stage_all()
        service.create_commit(msg)
        return {"execution_result": {"status": "success", "action": "commit"}}
        
    return {"execution_result": {"status": "failed", "error": "Unknown action"}}

if __name__ == "__main__":
    print(get_project_readme())