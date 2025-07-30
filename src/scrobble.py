import pylast
import json
import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from colorama import init, Fore
init(autoreset = True)  

# Load
load_dotenv()
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir, 'config.json')
with open(file_path, 'r') as json_file:
    config = json.load(json_file)  

api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
username = os.getenv('LASTFM_USERNAME')
password = os.getenv('LASTFM_PASSWORD')
albums = config['ALBUMS']
interval = config['INTERVAL']
MAX_DAILY_SCROBBLES = 2000

# Debug print — loaded environment variables (without secrets)
print(Fore.CYAN + "=== Environment Variables ===")
for key in ["API_KEY", "API_SECRET", "LASTFM_USERNAME", "LASTFM_PASSWORD"]:
    value = os.getenv(key)
    print(f"{key}: {'✓' if value else '❌'}")

# Debug print — config.json path and contents
print(Fore.CYAN + f"\n=== Loaded config.json from: {file_path} ===")
try:
    with open(file_path, 'r') as json_file:
        config = json.load(json_file)
    print(json.dumps(config, indent=4))
except Exception as e:
    print(Fore.RED + f"Failed to load config.json: {e}")
    sys.exit(1)

# Login
try:
    network = pylast.LastFMNetwork(
    api_key=api_key,
    api_secret=api_secret,
    username=username,
    password_hash=pylast.md5(password)
    )
except pylast.NetworkError as e:
    print(Fore.RED + f'Please check your internet connection\n{e}')
    sys.exit()
except pylast.WSError as e:
    print(Fore.RED + f'Please check your creditentials at .env file\n{e}')
    sys.exit()

def get_today_scrobble_count():
    try:
        user = network.get_user(username)
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        recent_tracks = user.get_recent_tracks(limit=MAX_DAILY_SCROBBLES, time_from=int(yesterday.timestamp()))
        return len(recent_tracks)
    except Exception as e:
        print(Fore.RED + f'Error getting scrobble count: {e}')
        return 0

# Scrobble
def scrobble():
    total_scrobbled = 0
    current_album_index = 0

    while True:
        try:
            if total_scrobbled >= MAX_DAILY_SCROBBLES:
                print(Fore.YELLOW + "\nReached daily scrobble limit. Waiting for next reset...")
   
                tomorrow = datetime.now() + timedelta(days=1)
                tomorrow = tomorrow.replace(hour=0, minute=1, second=0, microsecond=0)
                sleep_seconds = (tomorrow - datetime.now()).total_seconds()
                print(Fore.BLUE + f"Resuming in {int(sleep_seconds/3600)} hours {int((sleep_seconds%3600)/60)} minutes")
                time.sleep(sleep_seconds)
                total_scrobbled = 0 
                continue
           
            album_info = albums[current_album_index]
            artist = album_info['ARTIST']
            album_name = album_info['ALBUM']
            
            album_obj = network.get_album(artist, album_name)
            tracks = album_obj.get_tracks()
            total_tracks = len(tracks)
            
            print(Fore.BLUE + f'\nStarting to scrobble {album_name} by {artist} ({total_tracks} tracks)')
            print(Fore.BLUE + f'Daily scrobbles so far: {total_scrobbled}/{MAX_DAILY_SCROBBLES}')
            
            for index, track in enumerate(tracks, 1):
                if total_scrobbled >= MAX_DAILY_SCROBBLES:
                    break    
                track_title = track.get_title()
                network.scrobble(artist=artist, title=track_title, timestamp=int(time.time()), album=album_name)
                total_scrobbled += 1
                
                print(Fore.BLUE + f'\rScrobbling {track_title} by {artist} {index}/{total_tracks} (Total today: {total_scrobbled})', end='', flush=True)
                time.sleep(interval)            
            print(Fore.GREEN + f"\nCompleted scrobbling {album_name} by {artist}")
            

            current_album_index = (current_album_index + 1) % len(albums)
            
        except pylast.NetworkError as e:
            print(Fore.RED + f'\nPlease check your internet connection\n{e}')
            time.sleep(30) 
        except Exception as e:
            print(Fore.RED + f'\nError: {e}')
            time.sleep(30) 