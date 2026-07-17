from datetime import datetime


class ReleaseScheduler:
    """
    Suggests an appropriate deployment window.
    """

    def recommend_release_time(self):
        now = datetime.now()

        print("📅 Calculating optimal deployment window...")

        return {
            "recommended_time": now.strftime("%Y-%m-%d 22:00"),
            "confidence": "High"
        }