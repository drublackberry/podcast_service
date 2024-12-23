from app import create_app, db
from app.models import Show, Episode, Segment, APIToken

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Show': Show,
        'Episode': Episode,
        'Segment': Segment,
        'APIToken': APIToken
    }
