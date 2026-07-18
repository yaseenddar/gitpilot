# app/services/watcher.py
import os
import time
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from app.graph.builder import create_git_graph

# Configuration variables
INACTIVITY_TIMEOUT_SECONDS = 3  # 1 Hour
TIMESTAMP_FILE = ROOT_DIR / "app" / "state" / ".last_activity"

class InactivityHandler(FileSystemEventHandler):
    def __init__(self):
        self.ignore_dirs = ["app", "context", ".git", "__pycache__", ".venv"]
        # Ensure directory exists and initialize state
        TIMESTAMP_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.log_activity()

    def log_activity(self):
        """Records the exact epoch time of the latest modification."""
        TIMESTAMP_FILE.write_text(str(time.time()), encoding="utf-8")

    def on_any_event(self, event):
        if event.is_directory:
            return

        relative_path = Path(event.src_path).relative_to(ROOT_DIR)
        top_dir = relative_path.parts[0] if relative_path.parts else ""

        if top_dir in self.ignore_dirs or relative_path.name.endswith((".pyc", ".tmp")):
            return

        print(f"⚡ Activity logged: {event.event_type} -> {relative_path}")
        self.log_activity()

def check_and_run_loop():
    """Background check loop that polls the activity timestamp."""
    graph = create_git_graph()
    print(f"👀 Monitoring project targets. Will run after {INACTIVITY_TIMEOUT_SECONDS // 60} minutes of silence.")
    
    while True:
        try:
            time.sleep(10) # Check status every 10 seconds to save CPU
            
            if not TIMESTAMP_FILE.exists():
                continue
                
            last_activity = float(TIMESTAMP_FILE.read_text(encoding="utf-8").strip())
            elapsed = time.time() - last_activity
            
            # If the user has been inactive for more than an hour
            if elapsed >= INACTIVITY_TIMEOUT_SECONDS:
                print(f"\n🤖 [Watcher] {INACTIVITY_TIMEOUT_SECONDS // 60} minutes of inactivity reached!")
                print("🚀 Booting Autonomous Loop to consolidate your work...")
                
                initial_state = {
                    "repository_path": str(ROOT_DIR),
                    "snapshot": None,
                    "plan": None,
                    "execution_result": None,
                    "is_verified": False,
                    "messages": []
                }
                
                graph.invoke(initial_state)
                
                # Reset timestamp after a successful run so it doesn't loop endlessly
                InactivityHandler().log_activity()
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Error during background monitoring check: {e}")

def start_watcher():
    event_handler = InactivityHandler()
    observer = Observer()
    observer.schedule(event_handler, path=str(ROOT_DIR), recursive=True)
    observer.start()
    
    print("System active. Press Ctrl+C to stop.")
    try:
        check_and_run_loop()
    finally:
        print("\nStopping watcher daemon safely...")
        observer.stop()
        observer.join()

if __name__ == "__main__":
    start_watcher()