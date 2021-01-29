from shutil import copyfile
from server.utils.league_api_util import get_current_patch
from server.utils.db_util import init_db
import os
import argparse
import re
import sys
import tarfile
from zipfile import ZipFile
import requests

def downloader(download_url: str, file_name: str = None, location: str = 'server/download'):
    """
    Helper function for downloading files.
    :param download_url: URL to download file from
    :param file_name: (optional) Name that file should be saved as
    :param location:
    :return:
    """
    file_name = file_name or os.path.basename(download_url)
    folder = os.path.join(os.getcwd(), location)
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Destination folder {location} created")
    req = requests.get(download_url)
    with open(os.path.join(folder, file_name), 'wb') as file:
        file.write(req.content)
        print(f"File {file_name} successfully downloaded...")
    return os.path.join(folder, file_name)

def download_data_dragon(version:str= None):
    """
    Helper Function used to download data dragon if necessary.
     Highly doubt it would be really that necessary, but just in case.
    :param version: Patch version of league that data dragon should be fetched from
    :return: None
    """
    version = version or get_current_patch()
    file = downloader("https://ddragon.leagueoflegends.com/cdn/dragontail-{}.tgz".format(version))
    if file:
        with tarfile.open(file) as dragon_file:
            print("Unpacking Data Dragon...")
            dragon_file.extractall(os.path.join(file, version))
        print("Finished. You can explore Data Dragon in the directory: {}".format(os.path.join(file, version)))

def download_assets(assets_location:str = 'server/static/img/ranked_tiers'):
    assets_folder = os.path.join(os.getcwd(), assets_location)
    if not os.path.exists(assets_folder):
        os.makedirs(assets_folder)
        print("Destination folders created")
    file = downloader("https://static.developer.riotgames.com/docs/lol/ranked-emblems.zip")
    with ZipFile(os.path.join(file, 'ranked-emblems.zip'), 'r') as assets:
        os.chdir(assets_location)
        assets.extractall()
    print("Finished downloading assets.")

def update_env(key: str, value: str):
    if not os.path.exists('.env'):
        copyfile('.env_sample', '.env')
    with open('.env', 'r+') as env:
        env_vars = {line.split('=')[0]: line.split('=')[1].replace('\n', '') for line in env.readlines()}
        env_vars[key] = value
        updated_vars = [f"{key}={value}\n" for key, value in env_vars.items()]
        env.seek(0)
        env.writelines(updated_vars)
        env.truncate()

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
        update_env('LEAGUE_API_KEY', key)
        return True
    else:
        return False


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Setup TUL E-sports.")
    parser.add_argument("-ulk", "--update_league_key", metavar='API_KEY', help="Instead of doing whole setup, update only League API Key")
    args = parser.parse_args()
    if args.update_league_key:
        if not update_lol_key(args.update_league_key):
            print("Invalid Key!")
        else:
            print("Key updated!")
        sys.exit()
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
    secret_key = input('Please provide secret key (As random as possible, as its used for security purposes): ')
    update_env('SECRET_KEY', secret_key)
    if input("Will the server use HTTPS? (Used to determine if cookies should have 'secure' parameter) <Y/n>: ").lower() == "n":
        update_env('SESSION_COOKIE_SECURE', 'False')
        update_env('CSRF_COOKIE_SECURE', 'False')
    if input("Do you want to download Data Dragon? (Not necessary, only to explore League Assets) <y/N>: ").lower() == "y":
        download_data_dragon()
    if input("Do you need to download assets? (only download if this is a first time setup) <y/N>: ").lower() == "y":
        download_assets()
    print("Creating and setting up database...")
    init_db()
    print("Setup Finished!")
    print("You can now run the server with:")
    print("$  waitress-serve server:app")

else:
    raise ImportError("This script cannot be imported!")