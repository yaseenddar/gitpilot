import time
from datetime import datetime


class LiveBranchTracker:
    """
    Simulates live tracking of Git repository activity.

    Future implementation ideas:
    - Watch the current branch for new commits.
    - Detect force pushes.
    - Notify when teammates push to the same branch.
    - Stream events to the GitPilot dashboard.
    """

    def __init__(self, repository: str):
        self.repository = repository
        self.is_tracking = False

    def start_tracking(self):
        """Starts monitoring repository activity."""
        self.is_tracking = True
        print(f"👀 Live tracking started for '{self.repository}'.")

    def poll_repository(self):
        """
        Dummy implementation that pretends to receive
        repository updates every few seconds.
        """
        if not self.is_tracking:
            print("Tracking has not been started.")
            return

        fake_events = [
            "New commit detected on feature/login-ui",
            "Pull request #42 was updated",
            "Branch 'develop' received 3 new commits",
            "Repository synchronized with remote origin",
        ]

        for event in fake_events:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 📡 {event}")
            time.sleep(1)

    def stop_tracking(self):
        """Stops monitoring repository activity."""
        self.is_tracking = False
        print("🛑 Live tracking stopped.")


if __name__ == "__main__":
    tracker = LiveBranchTracker("GitPilot")
    tracker.start_tracking()
    tracker.poll_repository()
    tracker.stop_tracking()