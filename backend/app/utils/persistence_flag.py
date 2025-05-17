import os

def use_db_persistence() -> bool:
    """
    Returns True if MARKET_USE_DB_PERSISTENCE environment variable is set to '1', 'true', or 'yes'.
    Usage:
        if use_db_persistence():
            # Use database repositories
        else:
            # Use in-memory storage
    """
    return os.getenv("MARKET_USE_DB_PERSISTENCE", "0").lower() in ("1", "true", "yes") 