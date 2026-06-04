import json
import os

class Options(dict):
    """A simple dictionary subclass to hold SSH options."""
    def __init__(self, filepath="options.json"):
        super().__init__()
        self.filepath = filepath
        self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    super().update(json.load(f))
            except json.JSONDecodeError:
                pass
        self.setdefault("host", "N/A")
        self.setdefault("user", "N/A")
        self.setdefault("x11", False)
        self.setdefault("jump_host", "N/A")
        self.setdefault("port_forward", "N/A")

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self, f, indent=4)
