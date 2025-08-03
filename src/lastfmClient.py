import pylast
import sys
from datetime import datetime, timedelta
from colorama import Fore

class lastfmClient:
    def __init__(self, config_manager):
        self.config = config_manager
        self.network = self._authenticate()
    
    def _authenticate(self):
        try:
            network = pylast.LastFMNetwork(
                api_key=self.config.api_key,
                api_secret=self.config.api_secret,
                username=self.config.username,
                password_hash=pylast.md5(self.config.password)
            )
            return network
        except pylast.NetworkError as e:
            print(Fore.RED + f'Please check your internet connection\n{e}')
            sys.exit()
        except pylast.WSError as e:
            print(Fore.RED + f'On of your details incorrect, or API already used.\n{e}')
            sys.exit()
    
    def get_today_scrobble_count(self):
        try:
            user = self.network.get_user(self.config.username)
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            recent_tracks = user.get_recent_tracks(
                limit=self.config.max_daily_scrobbles, 
                time_from=int(yesterday.timestamp())
            )
            return len(recent_tracks)
        except Exception as e:
            print(Fore.RED + f'Error getting scrobble count: {e}')
            return 0
    
    def get_album_tracks(self, artist, album_name):
        try:
            album_obj = self.network.get_album(artist, album_name)
            return album_obj.get_tracks()
        except Exception as e:
            print(Fore.RED + f'Error getting album tracks: {e}')
            return []
    
    def scrobble_track(self, artist, title, album_name, timestamp):
        try:
            self.network.scrobble(
                artist=artist, 
                title=title, 
                timestamp=timestamp, 
                album=album_name
            )
            return True
        except Exception as e:
            print(Fore.RED + f'Error scrobbling track: {e}')
            return False