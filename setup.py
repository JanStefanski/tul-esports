from server.utils.league_api_util import get_current_patch
import os
import argparse
import re
import sys
import tarfile
import json
from zipfile import ZipFile
import requests

def download_data_dragon(location:str = 'server/download', version:str= None):
    """
    Helper Function used to download data dragon if necessary.
     Highly doubt it would be really that necessary, but just in case.
    :param location:
    :param version:
    :return: None
    """
    version = version or get_current_patch()
    req = requests.get("https://ddragon.leagueoflegends.com/cdn/dragontail-{}.tgz".format(version))
    folder = os.path.join(os.getcwd(), location)
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Destination folder {location} created")
    with open(os.path.join(folder, 'dragontail-{}.tgz'.format(version)), 'wb') as dragon_file:
        dragon_file.write(req.content)
        print(f"Data Dragon v.{version} successfully downloaded...")
    with tarfile.open(os.path.join(folder, 'dragontail-{}.tgz'.format(version))) as dragon_file:
        print("Unpacking Data Dragon...")
        dragon_file.extractall(os.path.join(folder, version))
    print("Finished. You can explore Data Dragon in the directory: {}".format(os.path.join(folder, version)))

def download_assets(downloads_location:str = 'server/download', assets_location:str = 'server/static/img/ranked_tiers'):
    req = requests.get("https://static.developer.riotgames.com/docs/lol/ranked-emblems.zip")
    download_folder = os.path.join(os.getcwd(), downloads_location)
    assets_folder = os.path.join(os.getcwd(), assets_location)
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    if not os.path.exists(assets_folder):
        os.makedirs(assets_folder)
    print("Destination folders created")
    with open(os.path.join(download_folder, 'ranked-emblems.zip'), 'wb') as dragon_file:
        dragon_file.write(req.content)
        print("Ranked assets successfully downloaded...")
    with ZipFile(os.path.join(download_folder, 'ranked-emblems.zip'), 'r') as assets:
        os.chdir(assets_location)
        assets.extractall()
    print("Finished downloading assets.")

def update_lol_key(key: str) -> bool:
    """
    Updates League of Legends API Key to new one.
    :param key: League API key
    :return: Boolean if key will be updated
    """
    # TODO: When .env will be done properly, this will have to be changed.
    if not key:
        return False
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
    parser.add_argument("-ulk", "--update_league_key", metavar='API_KEY', help="Instead of doing whole setup, update only League API Key")
    parser.add_argument("--heroku", help="Use special heroku deployment configuration",
                        action="store_true")
    args = parser.parse_args()
    if args.update_league_key:
        if not update_lol_key(args.update_league_key):
            print("Invalid Key!")
        else:
            print("Key updated!")
        sys.exit()
    if not args.heroku:
        print("TUL Esports Server Setup - Welcome")
        print("First, we need to set up a League of Legends API Key")
        print("If you don't have it already, please get it on https://developer.riotgames.com/")
        league_key = None
        while not update_lol_key(league_key):
            if not league_key is None:
                print("Invalid Key!")
            league_key = input("Enter new League API Key: ")
        else:
            print("Key Updated")
        if input("Do you want to download Data Dragon? (Not necessary, only to explore League Assets) <y/N>").lower() == "y":
            download_data_dragon()
        if input("Do you need to download assets? (only download if this is a first time setup) <y/N>").lower() == "y":
            download_assets()
        print("Setup Finished!")
        print("You can now run the server with:")
        print("$  waitress-serve server:app")
    else:
        print("Doing heroku setup...")
        download_assets()
        create_db()
else:
    raise ImportError("This script cannot be imported!")