from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SESSION_TYPE = 'redis'
    SESSION_REDIS = os.getenv('REDIS_URL')
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 60 * 60
    SESSION_COOKIE_SECURE=True
    SESSION_COOKIE_HTTPONLY=True
    SESSION_COOKIE_SAMESITE='None'
    SESSION_COOKIE_DOMAIN=None
    
    MONGODB_URI = os.getenv('MONGODB_URI')
    MONGODB_DB = os.getenv('MONGODB_DB')