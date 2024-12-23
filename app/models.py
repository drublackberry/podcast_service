from datetime import datetime
from app import db
import numpy as np
import json

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listennotes_id = db.Column(db.String(64), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    publisher = db.Column(db.String(200))
    website = db.Column(db.String(500))
    rss_feed = db.Column(db.String(500))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    episodes = db.relationship('Episode', backref='show', lazy='dynamic')

    def __repr__(self):
        return f'<Show {self.title}>'

class Episode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    listennotes_id = db.Column(db.String(64), unique=True, nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    audio_url = db.Column(db.String(500))
    published_at = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # in seconds
    transcript_status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    segments = db.relationship('Segment', backref='episode', lazy='dynamic')

    def __repr__(self):
        return f'<Episode {self.title}>'

class Segment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    episode_id = db.Column(db.Integer, db.ForeignKey('episode.id'), nullable=False)
    start_time = db.Column(db.Integer)  # in seconds
    end_time = db.Column(db.Integer)    # in seconds
    text = db.Column(db.Text, nullable=False)
    embedding = db.Column(db.Text)  # JSON string of embedding vector
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_embedding(self, embedding_array):
        """Store numpy array as JSON string"""
        if embedding_array is not None:
            self.embedding = json.dumps(embedding_array.tolist())

    def get_embedding(self):
        """Retrieve embedding as numpy array"""
        if self.embedding:
            return np.array(json.loads(self.embedding))
        return None

    def __repr__(self):
        return f'<Segment {self.id} ({self.start_time}s - {self.end_time}s)>'

class APIToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    requests_count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<APIToken {self.name}>'
