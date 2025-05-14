from app import create_app, socketio
from app.websockets.events import register_socketio_events

app = create_app()
register_socketio_events(socketio)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True) 