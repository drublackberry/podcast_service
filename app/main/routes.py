from flask import render_template, flash, redirect, url_for, request
from app import db
from app.main import bp
from app.models import Show, Episode, APIToken
from app.services.podcast_service import ListenNotesAPI, update_show_episodes
import secrets
from datetime import datetime

@bp.route('/')
def index():
    """Show dashboard with shows and API tokens"""
    shows = Show.query.all()
    tokens = APIToken.query.all()
    return render_template('index.html', shows=shows, tokens=tokens)

@bp.route('/shows/add', methods=['GET', 'POST'])
def add_show():
    """Add a new show"""
    if request.method == 'POST':
        listennotes_id = request.form.get('listennotes_id')
        if not listennotes_id:
            flash('Listen Notes ID is required', 'error')
            return redirect(url_for('main.add_show'))
        
        # Check if show already exists
        existing_show = Show.query.filter_by(listennotes_id=listennotes_id).first()
        if existing_show:
            flash('Show already exists', 'error')
            return redirect(url_for('main.index'))
        
        try:
            # Get show details from Listen Notes API
            api = ListenNotesAPI()
            show_data = api.get_episode_details(listennotes_id)  # Using episode details endpoint as example
            
            if show_data:
                show = Show(
                    listennotes_id=listennotes_id,
                    title=show_data.get('podcast', {}).get('title', 'Unknown Show'),
                    description=show_data.get('podcast', {}).get('description'),
                    publisher=show_data.get('podcast', {}).get('publisher'),
                    website=show_data.get('podcast', {}).get('website'),
                    rss_feed=show_data.get('podcast', {}).get('rss')
                )
                db.session.add(show)
                db.session.commit()
                
                # Start processing episodes
                update_show_episodes(show)
                
                flash('Show added successfully', 'success')
                return redirect(url_for('main.index'))
            else:
                flash('Could not fetch show details', 'error')
        
        except Exception as e:
            flash(f'Error adding show: {str(e)}', 'error')
    
    return render_template('add_show.html')

@bp.route('/shows/<show_id>')
def show_details(show_id):
    """Show details for a specific show"""
    show = Show.query.filter_by(listennotes_id=show_id).first_or_404()
    episodes = Episode.query.filter_by(show_id=show.id).order_by(Episode.published_at.desc()).all()
    return render_template('show_details.html', show=show, episodes=episodes)

@bp.route('/tokens/create', methods=['GET', 'POST'])
def create_token():
    """Create a new API token"""
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Token name is required', 'error')
            return redirect(url_for('main.create_token'))
        
        token = APIToken(
            token=secrets.token_urlsafe(32),
            name=name
        )
        db.session.add(token)
        db.session.commit()
        
        flash('API token created successfully', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('create_token.html')

@bp.route('/tokens/<token_id>/toggle')
def toggle_token(token_id):
    """Toggle API token active status"""
    token = APIToken.query.get_or_404(token_id)
    token.is_active = not token.is_active
    db.session.commit()
    
    status = 'activated' if token.is_active else 'deactivated'
    flash(f'Token {status} successfully', 'success')
    return redirect(url_for('main.index'))
