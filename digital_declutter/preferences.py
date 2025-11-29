import json
import os
from typing import Dict, Optional

class PreferenceStore:
    def __init__(self, filepath: str = "preferences.json"):
        self.filepath = filepath
        self.preferences: Dict[str, str] = {}
        self.load()

    def load(self):
        """Loads preferences from the JSON file."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.preferences = json.load(f)
            except json.JSONDecodeError:
                self.preferences = {}
        else:
            self.preferences = {}

    def save(self):
        """Saves preferences to the JSON file."""
        with open(self.filepath, 'w') as f:
            json.dump(self.preferences, f, indent=4)

    def get_rule(self, sender: str) -> Optional[str]:
        """Returns the rule for a specific sender, if any."""
        return self.preferences.get(sender)

    def set_rule(self, sender: str, action: str):
        """Sets a rule for a specific sender (e.g., 'delete', 'important')."""
        self.preferences[sender] = action
        self.save()

    def get_all_rules(self) -> Dict[str, str]:
        """Returns all stored rules."""
        return self.preferences
