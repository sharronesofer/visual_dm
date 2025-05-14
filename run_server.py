"""
Run the Visual DM server with WebSocket support.
"""

import os
import sys
import logging
import eventlet
import eventlet.wsgi
from app import create_app
from app.extensions import socketio
from app.websockets.events import register_socketio_events

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the server."""
    try:
        # Create the Flask application
        app = create_app('development')

        # Register WebSocket events
        register_socketio_events(socketio)

        # Run the server with SocketIO (eventlet async mode)
        logger.info("Starting server with WebSocket support on port 5050...")
        socketio.run(app, host='0.0.0.0', port=5050, debug=True)

    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 