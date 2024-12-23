from datetime import datetime, timedelta
import requests
from flask import current_app
from app import db, scheduler
from app.models import Show, Episode, Segment
from app.services.embedding_service import create_embedding
import logging

logger = logging.getLogger(__name__)

class ListenNotesAPI:
    def __init__(self):
        self.base_url = current_app.config['LISTENNOTES_API_BASE_URL']
        self.api_key = current_app.config['LISTENNOTES_API_KEY']
        self.headers = {
            'X-ListenAPI-Key': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_episode_transcript(self, episode_id):
        url = f"{self.base_url}/episodes/{episode_id}/transcript"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_episode_details(self, episode_id):
        url = f"{self.base_url}/episodes/{episode_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

def segment_transcript(transcript_text, max_length=500):
    """Split transcript into segments of approximately max_length characters"""
    words = transcript_text.split()
    segments = []
    current_segment = []
    current_length = 0
    
    for word in words:
        word_length = len(word) + 1  # +1 for space
        if current_length + word_length > max_length and current_segment:
            segments.append(' '.join(current_segment))
            current_segment = [word]
            current_length = word_length
        else:
            current_segment.append(word)
            current_length += word_length
    
    if current_segment:
        segments.append(' '.join(current_segment))
    
    return segments

def process_episode_transcript(episode):
    """Process transcript for an episode and create embeddings"""
    try:
        api = ListenNotesAPI()
        transcript_data = api.get_episode_transcript(episode.listennotes_id)
        
        if not transcript_data or 'transcript' not in transcript_data:
            episode.transcript_status = 'failed'
            db.session.commit()
            return
        
        # Split transcript into segments
        segments = segment_transcript(
            transcript_data['transcript'],
            current_app.config['MAX_SEGMENT_LENGTH']
        )
        
        # Create segments with embeddings
        for i, text in enumerate(segments):
            # Calculate approximate time ranges based on position in transcript
            total_duration = episode.duration or 0
            segment_duration = total_duration / len(segments)
            start_time = int(i * segment_duration)
            end_time = int((i + 1) * segment_duration)
            
            # Create embedding for segment
            embedding = create_embedding(text)
            
            segment = Segment(
                episode_id=episode.id,
                start_time=start_time,
                end_time=end_time,
                text=text
            )
            segment.set_embedding(embedding)
            db.session.add(segment)
        
        episode.transcript_status = 'completed'
        episode.last_updated = datetime.utcnow()
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error processing transcript for episode {episode.id}: {str(e)}")
        episode.transcript_status = 'failed'
        db.session.commit()

def update_show_episodes(show):
    """Update episodes for a show and process their transcripts"""
    try:
        api = ListenNotesAPI()
        
        # Get episodes that need transcript processing
        pending_episodes = Episode.query.filter_by(
            show_id=show.id,
            transcript_status='pending'
        ).all()
        
        for episode in pending_episodes:
            # Update episode details if needed
            episode_data = api.get_episode_details(episode.listennotes_id)
            if episode_data:
                episode.title = episode_data.get('title', episode.title)
                episode.description = episode_data.get('description', episode.description)
                episode.audio_url = episode_data.get('audio', episode.audio_url)
                episode.published_at = datetime.fromtimestamp(episode_data.get('pub_date_ms', 0)/1000)
                episode.duration = episode_data.get('audio_length_sec', 0)
                db.session.commit()
            
            # Process transcript
            episode.transcript_status = 'processing'
            db.session.commit()
            process_episode_transcript(episode)
        
        show.last_updated = datetime.utcnow()
        db.session.commit()
        
    except Exception as e:
        logger.error(f"Error updating show {show.id}: {str(e)}")

def schedule_podcast_updates():
    """Schedule regular updates of podcast episodes and transcripts"""
    def update_all_shows():
        with scheduler.app.app_context():
            shows = Show.query.all()
            for show in shows:
                update_show_episodes(show)
    
    # Schedule updates based on configuration
    update_interval = current_app.config['UPDATE_SCHEDULE_HOURS']
    scheduler.add_job(
        id='update_podcasts',
        func=update_all_shows,
        trigger='interval',
        hours=update_interval,
        next_run_time=datetime.now()
    )
