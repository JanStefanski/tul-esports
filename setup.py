from server.utils.league_api_util import get_current_patch
import os
import argparse
import re
import sys
import tarfile
import json
from rich.prompt import Prompt, Confirm
from rich.console import Console
import requests

console = Console()


def download_data_dragon(location:str = 'server/download', version:str= None):
    """
    Helper Function used to download data dragon if necessary.
     Highly doubt it would be really that necessary, but just in case.
    :param location:
    :param version:
    :return: None
    """
    version = version or get_current_patch()
    with console.status("[bold green]Processing Data Dragon...", spinner='dots') as status:
        req = requests.get("https://ddragon.leagueoflegends.com/cdn/dragontail-{}.tgz".format(version))
        folder = os.path.join(os.getcwd(), location)
        if not os.path.exists(folder):
            os.makedirs(folder)
            console.log(f"Destination folder {location} created")
        with open(os.path.join(folder, 'dragontail-{}.tgz'.format(version)), 'wb') as dragon_file:
            dragon_file.write(req.content)
            console.log(f"Data Dragon v.{version} successfully downloaded...")
        with tarfile.open(os.path.join(folder, 'dragontail-{}.tgz'.format(version))) as dragon_file:
            console.log("Unpacking Data Dragon...")
            dragon_file.extractall(os.path.join(folder, version))
    console.log("Finished. You can explore Data Dragon in the directory: {}".format(os.path.join(folder, version)))

def update_lol_key(key: str) -> bool:
    """
    Updates League of Legends API Key to new one.
    :param key: League API key
    :return: Boolean if key will be updated
    """
    # TODO: When .env will be done properly, this will have to be changed.
    if re.search("^(RGAPI)-\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$", key):
        config_path = os.path.join(os.getcwd(), 'server/utils/config/config.json')
        with open(config_path, 'w+') as config_file:
            json.dump({"league_api_key": key} , config_file)
        return True
    else:
        return False

def create_db(db_name:str = "tulesp.sqlite"):
    # TODO: When DB will be ready implement creation of db in setup
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Setup TUL E-sports.")
    parser.add_argument("-ulk", "--update_league_key", help="Instead of doing whole setup update only League API Key",
                        action="store_true")
    parser.add_argument("--heroku", help="Use special heroku deployment configuration",
                        action="store_true")
    args = parser.parse_args()
    console.print("[bold]TUL Esports Server Setup[/bold] - Welcome", style="green")
    if args.update_league_key:
        league_key = Prompt.ask("Enter new League API Key")
        if not update_lol_key(league_key):
            console.print("Invalid Key!", style="bold red")
        sys.exit()
    if not args.heroku:
        console.print("First, we need to set up a League of Legends API Key", style="cyan")
        console.print("If you don't have it already, please get it [link https://developer.riotgames.com/]here[/link https://developer.riotgames.com/]")
        league_key = ""
        while not update_lol_key(league_key):
            console.print("Invalid Key!", style="bold red")
            league_key = Prompt.ask("Enter new League API Key")
        else:
            console.print("Key Updated", style="bold green")
        if Confirm.ask("Do you want to download Data Dragon? (Not necessary, only to explore League Assets)"):
            download_data_dragon()
        console.print("Setup Finished!", style="bold green")
        console.print("You can now run the server with:", style="bold blue")
        console.print("`waitress-serve server:app`", style="cyan")