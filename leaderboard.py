import json
import os

class LeaderboardManager:
    def __init__(self, filename="leaderboard.json", max_entries=5):
        self.filename = filename
        self.max_entries = max_entries
        self.data = {"scores": []}
        self.load_scores()

    def get_save_path(self):
        if "ANDROID_ARGUMENT" in os.environ or "ANDROID_PRIVATE" in os.environ:
            try:
                from android.storage import app_storage_path
                return os.path.join(app_storage_path(), self.filename)
            except ImportError:
                        # Desktop fallback safeguard if environment flags are spoofed
                return self.filename
        return self.filename
    def load_scores(self):
        """Loads score records out from text storage file safely."""
        path = self.get_save_path()
        if os.path.exists(path):
            try:
                with open(path, "r") as file:
                    self.data = json.load(file)
            except (json.JSONDecodeError, IOError):
                # Fallback pattern resets profile if corrupted files encountered
                self.data = {"scores": []}
        else:
            self.data = {"scores": []}

    def save_scores(self):
        """Writes current local dictionary memory data to hardware space."""
        path = self.get_save_path()
        try:
            with open(path, "w") as file:
                json.dump(self.data, file, indent=4)
        except IOError as error:
            print(f"File writing permission exception flagged: {error}")

    def is_high_score(self, score):
        """Checks if a game performance qualifies for a leaderboard rank placement."""
        scores_list = self.data.get("scores", [])
        if len(scores_list) < self.max_entries:
            return True
        # Check if score beats worst current entry
        return score > scores_list[-1]["score"]

    def add_score(self, name, score):
        """Inserts record entries, handles sort positioning updates, and truncates excess rows."""
        import datetime
        today_str = datetime.date.today().isoformat()

        new_entry = {
            "name": str(name).upper()[:3],  # Traditional 3-letter arcade tag limit
            "score": int(score),
            "date": today_str
        }

        self.data["scores"].append(new_entry)

        # Sort scores highest to lowest
        self.data["scores"].sort(key=lambda x: x["score"], reverse=True)

        # Truncate array to hold only the maximum allowed placement limit
        self.data["scores"] = self.data["scores"][:self.max_entries]

        self.save_scores()

    def get_scores(self):
        """Returns sorted structural ranking dictionary records arrays directly."""
        return self.data.get("scores", [])
