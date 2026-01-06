import cloudscraper
import os
import json
import base64
import sys
import time
from config_manager import ConfigManager


class CrunchyrollClient:
    def __init__(self, log_func=print):
        self.log = log_func
        cm = ConfigManager()
        raw_token = cm.get("CR_TOKEN") or ""
        if raw_token.startswith('"'): raw_token = raw_token[1:-1]
        if "Bearer " in raw_token:
            self.token_clean = raw_token.split("Bearer ")[1].strip()
        else:
            self.token_clean = raw_token

        if not self.token_clean:
            raise ValueError("CR Token missing in Settings")

        self.token = f"Bearer {self.token_clean}"
        self.scraper = cloudscraper.create_scraper()
        self.account_id = self._extract_account_id(self.token_clean)
        self.base_url = "https://www.crunchyroll.com/content/v2"
        self.headers = {
            "Authorization": self.token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def _extract_account_id(self, token_body):
        try:
            parts = token_body.split('.')
            payload = parts[1] + "=" * ((4 - len(parts[1]) % 4) % 4)
            data = json.loads(base64.urlsafe_b64decode(payload))
            return data.get('account_id') or data.get('etp_user_id') or data.get('sub')
        except:
            return None

    def get_watch_history(self):
        endpoint = f"{self.base_url}/{self.account_id}/watch-history"
        all_history = []
        page = 1

        while True:
            params = {"page_size": 100, "page": page}
            try:
                response = self.scraper.get(endpoint, headers=self.headers, params=params)
                if response.status_code != 200: break

                items = response.json().get('data', [])
                if not items: break

                for item in items:
                    meta = item.get('panel', {}).get('episode_metadata', {})
                    title = meta.get('series_title') or item.get('title')
                    ep = meta.get('episode_number')
                    if title and ep:
                        all_history.append({"title": title, "episode": ep})

                self.log(f"   -> Fetched Page {page} (Total: {len(all_history)})")
                page += 1
                time.sleep(0.5)
            except Exception as e:
                self.log(f"❌ Error on page {page}: {e}")
                break

        return all_history