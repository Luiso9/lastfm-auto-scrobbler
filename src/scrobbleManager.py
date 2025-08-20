import time
import random
from datetime import datetime, timedelta
from colorama import Fore
import httpx
import asyncio
import pylast


class scrobbleManager:
    def __init__(self, lastfm_client, config_manager):
        self.client = lastfm_client
        self.config = config_manager
        self.total_scrobbled = 0
        self.current_album_index = 0

    def get_random_interval(self):
        return random.uniform(self.config.interval_min, self.config.interval_max)

    def wait_for_next_day(self):
        print(Fore.YELLOW + "\nDaily scrobble reached.")

        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=0, minute=1, second=0, microsecond=0)
        sleep_seconds = (tomorrow - datetime.now()).total_seconds()

        hours = int(sleep_seconds / 3600)
        minutes = int((sleep_seconds % 3600) / 60)
        print(Fore.BLUE + f"Resuming in {hours} hours {minutes} minutes")

        time.sleep(sleep_seconds)
        self.total_scrobbled = 0

    def fetchTrackQueue(self):
        with httpx.Client() as client:
            res = client.get("http://54.254.230.226:8080")
            pretty = res.json()
            return [(item["artist"], item["track"]) for item in pretty["queue"]]

    def scrobble_tracks_from_api(self):
        tracks = self.fetchTrackQueue()
        if not tracks:
            print(Fore.RED + "No tracks returned from API")
            return False

        total_tracks = len(tracks)
        print(Fore.BLUE + f"\nStarting to scrobble {total_tracks} tracks from API")
        print(
            Fore.BLUE
            + f"Daily scrobbles so far: {self.total_scrobbled}/{self.config.max_daily_scrobbles}"
        )

        for index, (artist, track_title) in enumerate(tracks, 1):
            if self.total_scrobbled >= self.config.max_daily_scrobbles:
                break

            if self.client.scrobble_track(artist, track_title, None, int(time.time())):
                self.total_scrobbled += 1
                print(
                    Fore.BLUE
                    + f"\rScrobbling {track_title} by {artist} {index}/{total_tracks} (Total today: {self.total_scrobbled})",
                    end="",
                    flush=True,
                )

                if index < total_tracks:
                    interval = self.get_random_interval()
                    time.sleep(interval)

        print(Fore.GREEN + f"\nCompleted scrobbling {total_tracks} tracks from API")
        return True

    def run_continuous_scrobbling(self):
        while True:
            try:
                if self.total_scrobbled >= self.config.max_daily_scrobbles:
                    self.wait_for_next_day()
                    continue

                self.scrobble_tracks_from_api()

            except pylast.NetworkError as e:
                print(Fore.RED + f"\nPlease check your internet connection\n{e}")
                time.sleep(30)
            except Exception as e:
                print(Fore.RED + f"\nError: {e}")
                time.sleep(30)
