import json
import os
from dotenv import load_dotenv

class configHandler:
    def __init__(self):
        load_dotenv()
        self.project_root = self._get_project_root()
        self.config = self._load_config()
        
    def _get_project_root(self):
        current_dir = os.path.dirname(__file__) 
        return os.path.dirname(current_dir) 
        
    def _load_config(self):
        file_path = os.path.join(self.project_root, 'config.json')
        try:
            with open(file_path, 'r', encoding='utf-8') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found at {file_path}")
    
    @property
    def api_key(self):
        return os.getenv('API_KEY')
    
    @property
    def api_secret(self):
        return os.getenv('API_SECRET')
    
    @property
    def username(self):
        return os.getenv('LASTFM_USERNAME')
    
    @property
    def password(self):
        return os.getenv('LASTFM_PASSWORD')
    
    @property
    def albums(self):
        return self.config['ALBUMS']
    
    @property
    def interval_min(self):
        return self.config.get('INTERVAL_MIN', 5)
    
    @property
    def interval_max(self):
        return self.config.get('INTERVAL_MAX', 15)
    
    @property
    def max_daily_scrobbles(self):
        return self.config.get('MAX_DAILY_SCROBBLES', 2000)