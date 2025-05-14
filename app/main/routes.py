"""
Main routes.
"""

from datetime import datetime
from flask import render_template
from flask_login import current_user
from app.main import bp

@bp.route('/')
@bp.route('/index')
def index():
    """Render the index page."""
    return render_template('index.html', now=datetime.utcnow()) 