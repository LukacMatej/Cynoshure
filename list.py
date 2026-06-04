import json
import os

class HistoryStore(list):
    """A list subclass to manage connection history."""
    def __init__(self, filepath="history.json"):
        super().__init__()
        self.filepath = filepath
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self.extend(json.load(f))
            except json.JSONDecodeError:
                pass

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self, f, indent=4)

    def add_entry(self, entry):
        for existing in self:
            if existing.get("target") == entry.get("target"):
                return False
        self.append(entry)
        self.save()
        return True

    def remove_entry(self, target):
        for existing in self:
            if existing.get("target") == target:
                self.remove(existing)
                self.save()
                return True
        return False

class SessionStore(list):
    """A list subclass to manage saved sessions (favorites)."""
    def __init__(self, filepath="sessions.json"):
        super().__init__()
        self.filepath = filepath
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    self.extend(json.load(f))
            except json.JSONDecodeError:
                pass

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self, f, indent=4)

    def add_entry(self, entry):
        for existing in self:
            if existing.get("target") == entry.get("target"):
                return False
        self.append(entry)
        self.save()
        return True
    
    def remove_entry(self, target):
        for existing in self:
            if existing.get("target") == target:
                self.remove(existing)
                self.save()
                return True
        return False
