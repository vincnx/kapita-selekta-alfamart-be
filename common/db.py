from pymongo import MongoClient 
from config import Config

class Database:
    def __init__(self):
        try:
            self.db = {}
            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client[Config.MONGODB_DB]
        except Exception as e:
            print(f'Error: Failed connect to database {e}')

dbInstance = Database()

