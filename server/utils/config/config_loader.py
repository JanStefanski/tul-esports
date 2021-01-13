import json
import os

CONFIG_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(CONFIG_ROOT, 'config.json')


class ConfigLoader:

    def __init__(self):
        print("Loading Config...")
        if os.path.exists(CONFIG_FILE):     # Check if config file exists (for local use), if it exists, then take vars from file.
            with open(CONFIG_FILE, 'r') as configuration_file:
                json_config = json.load(configuration_file)
                self.league_api_key = json_config['league_api_key']
        else:   # In other case (production), let us search for environment vars for keys.
            self.league_api_key = os.environ['LEAGUE_API_KEY']
