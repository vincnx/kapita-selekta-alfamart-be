from pymongo import MongoClient

from config import MONGODB_DB, MONGODB_URI

class Database:
    def __init__(self):
        try:
            self.db = {}
            self.client = MongoClient(MONGODB_URI)
            self.db = self.client[MONGODB_DB]
        except Exception as e:
            print(f'Error: Failed connect to database {e}')

dbInstance = Database()

