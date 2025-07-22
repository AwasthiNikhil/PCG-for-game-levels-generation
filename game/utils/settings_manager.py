import json
import requests
import os

class SettingsManager:
    def __init__(self, file_path="settings.json"):
        self.file_path = file_path
        self.settings = self._load_settings()

    def _load_settings(self, userid=None):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {} # Return empty dict if file doesn't exist

    def save_settings(self, settings_data):
        with open(self.file_path, 'w') as f:
            json.dump(settings_data, f, indent=4)
        requests.post(f'http://localhost:5000/settings?uid={settings_data["USERID"]}', json=settings_data)
        
        
    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings[key] = value
        self.save_settings(self.settings) # Save immediately on change for simplicity
