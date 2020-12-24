from pymongo import MongoClient
from .config.config_loader import CONFIG

def check_mongo():
    client = MongoClient(CONFIG.mongo_connection_string)
    db = client.test
    return db