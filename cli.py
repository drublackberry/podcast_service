from flask.cli import FlaskGroup
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set FLASK_APP environment variable
os.environ['FLASK_APP'] = 'podcast_service.py'

from podcast_service import app

cli = FlaskGroup(app)

if __name__ == '__main__':
    cli()
