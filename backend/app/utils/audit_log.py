import logging
from datetime import datetime
from backend.app.db import db_session

# Optionally, create an AuditLog model for DB logging. For now, log to file.
logger = logging.getLogger("audit")
handler = logging.FileHandler("audit.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def log_event(event_type: str, user_id: int = None, ip: str = None, details: str = None):
    msg = f"event={event_type} user_id={user_id} ip={ip} details={details}"
    logger.info(msg) 