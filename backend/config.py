import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class."""
    # The MongoDB connection string
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/smart_assistant'
    
    # Secret key for sessions/JWT later
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key-change-in-production'
