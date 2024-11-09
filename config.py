from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    SESSION_TYPE = 'redis'
    SESSION_REDIS = 'redis://localhost:6379'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 60 * 60
    
    MONGODB_URI = os.getenv('MONGODB_URI')
    MONGODB_DB = os.getenv('MONGODB_DB')