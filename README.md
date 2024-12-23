# Podcast Service

A microservice for managing podcast transcripts and providing semantic search capabilities.

## Features

- Automatically fetches and processes podcast transcripts from Listen Notes API
- Creates embeddings for podcast segments using transformer models
- Provides API endpoints for semantic search across podcast content
- Web interface for managing shows and API tokens
- Scheduled updates of podcast content

## Setup

1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a `.env` file with your configuration:
```
FLASK_APP=podcast_service.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
LISTENNOTES_API_KEY=your-listennotes-api-key
DATABASE_URL=sqlite:///podcast.db  # or your database URL
```

3. Initialize the database:
```bash
flask db init
flask db migrate
flask db upgrade
```

4. Run the application:
```bash
flask run
```

## API Usage

The service exposes the following API endpoints:

### Search Segments
```http
POST /api/search
Content-Type: application/json
X-API-Token: your-api-token

{
    "embedding": [...],  # Vector of floats
    "threshold": 0.7,    # Optional similarity threshold
    "limit": 5          # Optional limit of results
}
```

### List Shows
```http
GET /api/shows
X-API-Token: your-api-token
```

### Get Show Episodes
```http
GET /api/shows/<show_id>/episodes
X-API-Token: your-api-token
```

### Get Episode Segments
```http
GET /api/episodes/<episode_id>/segments
X-API-Token: your-api-token
```

## Web Interface

The web interface provides the following features:

- Dashboard showing all shows and API tokens
- Add new shows using Listen Notes IDs
- View show details and episode status
- Create and manage API tokens
- Monitor transcript processing status

## Development

To run tests:
```bash
pytest
```

To run with debug mode:
```bash
FLASK_ENV=development flask run
```

## License

MIT License
