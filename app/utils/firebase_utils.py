import logging
from firebase_admin import db
from datetime import datetime

# Firebase I/O Helper Functions

def firebase_get(path, default=None):
    """Retrieve data from Firebase at the specified path."""
    try:
        ref = db.reference(path)
        return ref.get() or default
    except Exception as e:
        logging.error(f"Firebase GET error at {path}: {e}")
        return default

def firebase_set(path, data):
    """Set data in Firebase at the specified path."""
    try:
        ref = db.reference(path)
        ref.set(data)
        logging.info(f"Firebase SET successful at {path}")
        return True
    except Exception as e:
        logging.error(f"Firebase SET error at {path}: {e}")
        return False

def firebase_update(path, data):
    """Update data at a given Firebase path."""
    try:
        ref = db.reference(path)
        ref.update(data)
        logging.info(f"Firebase UPDATE successful at {path}")
        return True
    except Exception as e:
        logging.error(f"Firebase UPDATE error at {path}: {e}")
        return False

def firebase_delete(path):
    """Delete data from Firebase at the specified path."""
    try:
        ref = db.reference(path)
        ref.delete()
        logging.info(f"Firebase DELETE successful at {path}")
        return True
    except Exception as e:
        logging.error(f"Firebase DELETE error at {path}: {e}")
        return False

# Structured Logging Utility

def log_event(event_name, details=None, level="info"):
    """
    Logs structured events with a consistent format.
    
    Args:
        event_name (str): Name of the event to log.
        details (dict, optional): Additional information about the event.
        level (str): Logging level ('info', 'warning', 'error').
    """
    log_message = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_name,
        "details": details or {}
    }

    if level == "info":
        logging.info(log_message)
    elif level == "warning":
        logging.warning(log_message)
    elif level == "error":
        logging.error(log_message)
    else:
        logging.debug(log_message)

# Example usage:
# log_event("CharacterCreated", {"character_id": "1234"}, level="info")
