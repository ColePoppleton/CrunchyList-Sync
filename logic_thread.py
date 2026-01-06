import threading
import json
import os
import time
from crunchyroll import CrunchyrollClient
from anilist_client import AniListClient

HISTORY_FILE = "crunchyroll_history.json"


class WorkerThread(threading.Thread):
    def __init__(self, mode, token, log_callback, done_callback):
        super().__init__()
        self.mode = mode
        self.token = token
        self.log = log_callback
        self.done = done_callback
        self._stop_event = threading.Event()

    def run(self):
        try:
            if self.mode == 'full_sync':
                self.run_fetch()
                if not self._stop_event.is_set():
                    self.run_sync()
            elif self.mode == 'fetch':
                self.run_fetch()
            elif self.mode == 'sync':
                self.run_sync()
        except Exception as e:
            self.log(f"❌ Critical Thread Error: {e}")
        finally:
            self.done()

    def stop(self):
        self._stop_event.set()

    def run_fetch(self):
        self.log("🔵 [1/2] Fetching Crunchyroll History...")
        try:
            cr = CrunchyrollClient(log_func=self.log)
            history = cr.get_watch_history()

            if history:
                self.log(f"   -> Saving {len(history)} items to json...")
                with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                    json.dump(history, f, indent=4)
                self.log("✅ Crunchyroll backup complete.")
            else:
                self.log("⚠️ No history found on Crunchyroll.")
        except Exception as e:
            self.log(f"❌ Fetch Failed: {e}")

    def run_sync(self):
        if not os.path.exists(HISTORY_FILE):
            self.log(f"❌ Error: {HISTORY_FILE} missing. Fetch failed?")
            return

        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)

        self.log("🔵 [2/2] Syncing to AniList...")

        al = AniListClient(token=self.token, log_func=self.log)

        current_library = al.get_user_list(al.validate_token()['id'])
        search_cache = {}

        self.log(f"🚀 Processing {len(history)} items against AniList...")
        for item in reversed(history):
            if self._stop_event.is_set():
                self.log("🛑 Sync Stopped by user.")
                break

            title = item['title']
            cr_episode = int(item['episode'])
            if title in search_cache:
                anime_data = search_cache[title]
            else:
                anime_data = al.search_anime(title)
                if anime_data:
                    search_cache[title] = anime_data
                    time.sleep(0.5)
                else:
                    self.log(f"❌ Skipped: '{title}' (No match found)")
                    continue

            anime_id = anime_data['id']
            anime_title = anime_data['title'].get('english') or anime_data['title']['romaji']

            current_progress = current_library.get(anime_id, 0)

            if current_progress >= cr_episode:
                pass
            else:
                self.log(f"✨ Updating: {anime_title} (Ep {current_progress} -> {cr_episode})")
                if al.update_list(anime_id, cr_episode):
                    current_library[anime_id] = cr_episode
                    time.sleep(1.0)

        self.log("🎉 Sync Process Finished!")