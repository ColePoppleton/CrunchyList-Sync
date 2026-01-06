import json
import os

CONFIG_FILE = "config.json"

class ConfigManager:
    def __init__(self):
        if not os.path.exists(CONFIG_FILE):
            self._write_config({})

    def _read_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _write_config(self, data):
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def get(self, key, default=None):
        config = self._read_config()
        return config.get(key, default)

    def set(self, key, value):
        config = self._read_config()
        config[key] = value
        self._write_config(config)

    @staticmethod
    def save_token(token):
        cm = ConfigManager()
        cm.set("access_token", token)

    @staticmethod
    def get_token():
        cm = ConfigManager()
        return cm.get("access_token")

    @staticmethod
    def clear_token():
        cm = ConfigManager()
        config = cm._read_config()
        if "access_token" in config:
            del config["access_token"]
            cm._write_config(config)