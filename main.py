import sys
import os
from colorama import init, Fore

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
init(autoreset=True)

from src import configHandler, lastfmClient, scrobbleManager


def main():
    try:
        config = configHandler()
        client = lastfmClient(config)        
        scrobbler = scrobbleManager(client, config)
        
        scrobbler.run_continuous_scrobbling()
        
    except Exception as e:
        print(Fore.RED + f"Error, {e}")
        print(Fore.YELLOW + "Please check your configuration and try again.")

if __name__ == "__main__":
    main()