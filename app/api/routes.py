from flask import jsonify, request, current_app
from app import db
from app.api import bp
from app.models import Show, Episode, Segment, APIToken
from app.services.embedding_service import create_embedding, find_similar_segments
from datetime import datetime
import numpy as np
from functools import wraps

def require_api_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-API-Token')
        if not token:
            return jsonify({'error': 'API token is required'}), 401
        
        api_token = APIToken.query.filter_by(token=token, is_active=True).first()
        if not api_token:
            return jsonify({'error': 'Invalid or inactive API token'}), 401
        
        # Update token usage
        api_token.last_used = datetime.utcnow()
        api_token.requests_count += 1
        db.session.commit()
        
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/search', methods=['POST'])
@require_api_token
def search():
    """Search for similar podcast segments using an embedding"""
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
    
    data = request.get_json()
    if 'embedding' not in data:
        return jsonify({'error': 'embedding is required'}), 400
    
    try:
        query_embedding = np.array(data['embedding'])
        threshold = data.get('threshold', 0.7)
        limit = data.get('limit', 5)
        
        similar_segments = find_similar_segments(query_embedding, threshold, limit)
        
        results = []
        for segment, similarity in similar_segments:
            episode = segment.episode
            show = episode.show
            results.append({
                'similarity': float(similarity),
                'segment': {
                    'text': segment.text,
                    'start_time': segment.start_time,
                    'end_time': segment.end_time
                },
                'episode': {
                    'id': episode.listennotes_id,
                    'title': episode.title,
                    'audio_url': episode.audio_url,
                    'published_at': episode.published_at.isoformat() if episode.published_at else None
                },
                'show': {
                    'id': show.listennotes_id,
                    'title': show.title
                }
            })
        
        return jsonify({'results': results})
    
    except Exception as e:
        current_app.logger.error(f"Search error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/shows', methods=['GET'])
@require_api_token
def get_shows():
    """Get all shows"""
    shows = Show.query.all()
    return jsonify({
        'shows': [{
            'id': show.listennotes_id,
            'title': show.title,
            'description': show.description,
            'publisher': show.publisher,
            'website': show.website,
            'last_updated': show.last_updated.isoformat() if show.last_updated else None
        } for show in shows]
    })

@bp.route('/shows/<show_id>/episodes', methods=['GET'])
@require_api_token
def get_show_episodes(show_id):
    """Get episodes for a specific show"""
    show = Show.query.filter_by(listennotes_id=show_id).first_or_404()
    episodes = Episode.query.filter_by(show_id=show.id).all()
    
    return jsonify({
        'episodes': [{
            'id': episode.listennotes_id,
            'title': episode.title,
            'description': episode.description,
            'audio_url': episode.audio_url,
            'published_at': episode.published_at.isoformat() if episode.published_at else None,
            'duration': episode.duration,
            'transcript_status': episode.transcript_status
        } for episode in episodes]
    })

@bp.route('/episodes/<episode_id>/segments', methods=['GET'])
@require_api_token
def get_episode_segments(episode_id):
    """Get segments for a specific episode"""
    episode = Episode.query.filter_by(listennotes_id=episode_id).first_or_404()
    segments = Segment.query.filter_by(episode_id=episode.id).all()
    
    return jsonify({
        'segments': [{
            'id': segment.id,
            'start_time': segment.start_time,
            'end_time': segment.end_time,
            'text': segment.text
        } for segment in segments]
    })
