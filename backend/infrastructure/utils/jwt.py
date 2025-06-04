import jwt
import os
import secrets
from datetime import datetime, timedelta

# Secure secret key management
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

if not SECRET_KEY:
    if os.environ.get("ENVIRONMENT") == "production":
        raise ValueError("JWT_SECRET_KEY must be set in production environment")
    else:
        # Generate a secure random key for development (not persistent)
        SECRET_KEY = secrets.token_urlsafe(32)
        print("WARNING: Using generated JWT secret key for development. Set JWT_SECRET_KEY environment variable.")

# Validate secret key strength
if len(SECRET_KEY) < 32:
    raise ValueError("JWT_SECRET_KEY must be at least 32 characters long")

ALGORITHM = "HS256"
# Secure token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))  # Shorter-lived access tokens
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7"))     # Longer-lived refresh tokens

# Session management
MAX_CONCURRENT_SESSIONS = int(os.environ.get("MAX_CONCURRENT_SESSIONS", "5"))

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validate token type if present
        token_type = payload.get("type")
        if token_type not in ["access", "refresh", None]:  # None for backward compatibility
            return None
            
        # Check token hasn't expired
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            return None
            
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None 