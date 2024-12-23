import os
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'podcast.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ListenNotes API Configuration
    LISTENNOTES_API_KEY = os.environ.get('LISTENNOTES_API_KEY')
    LISTENNOTES_API_BASE_URL = 'https://listen-api.listennotes.com/api/v2'
    
    # Scheduler Configuration
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = "UTC"
    
    # Update schedule (default: every day at midnight UTC)
    UPDATE_SCHEDULE_HOURS = int(os.environ.get('UPDATE_SCHEDULE_HOURS', 24))
    
    # Embedding Configuration
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_BATCH_SIZE = 32
    
    # Transcript Segmentation
    MAX_SEGMENT_LENGTH = 500  # characters
    
    # API Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
