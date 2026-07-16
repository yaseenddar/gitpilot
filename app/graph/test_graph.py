# F:\gitpilot\gitpilot\test_graph.py
import os
import sys
from pathlib import Path

# Force the root directory into sys.path so 'app' packages resolve flawlessly
ROOT_DIR = "F:\langGraph"
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# Force offline debug mode to avoid making any live LLM API calls
os.environ["GITPILOT_DEBUG"] = "1"

from .builder import create_git_graph

def run_test():
    # 1. Compile the LangGraph
    print("⚡ Compiling LangGraph...")
    graph = create_git_graph()
    
    # 2. Define the initial state (just like the watcher does)
    initial_state = {
        "repository_path": str(ROOT_DIR),
        "snapshot": None,
        "plan": None,
        "execution_result": None,
        "is_verified": False,
        "messages": []
    }
    
    print("🚀 Invoking Graph Workflow (Single Sync Pass)...")
    print("=" * 60)
    
    # 3. Execute the workflow synchronously
    final_state = graph.invoke(initial_state)
    
    print("=" * 60)
    print("🏁 Execution Complete!")
    print(f"📊 Final Verification Status: {final_state.get('is_verified')}")
    print(f"📦 Execution Result: {final_state.get('execution_result')}")

if __name__ == "__main__":
    run_test()