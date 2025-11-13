import json
from pathlib import Path
from config import AUTH_PATH

class AuthManager:
    def __init__(self):
        self.auth_path = AUTH_PATH
        self.auth_path.parent.mkdir(parents=True, exist_ok=True)
        self.credentials = self._load_credentials()

    def _load_credentials(self):
        if self.auth_path.exists():
            try:
                with open(self.auth_path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_credentials(self):
        with open(self.auth_path, 'w') as f:
            json.dump(self.credentials, f, indent=2)

    def set_auth(self, platform, auth_data):
        self.credentials[platform] = auth_data
        self._save_credentials()

    def get_auth(self, platform):
        return self.credentials.get(platform)

    def has_auth(self, platform):
        return platform in self.credentials

    def clear_auth(self, platform):
        if platform in self.credentials:
            del self.credentials[platform]
            self._save_credentials()
