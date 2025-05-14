"""
Firebase initialization and configuration module.
"""

import os
import json
import logging
from typing import Optional
import firebase_admin
from firebase_admin import credentials, db, firestore

logger = logging.getLogger(__name__)

# Global Firebase instances
firebase_app: Optional[firebase_admin.App] = None
firestore_client = None
realtime_db = None

def init_firebase(app=None) -> None:
    """Initialize Firebase with credentials."""
    global firebase_app, firestore_client, realtime_db
    
    try:
        # Check if already initialized
        if firebase_app:
            logger.warning("Firebase already initialized")
            return
            
        # Look for credentials file
        cred_path = os.environ.get('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
        if not os.path.exists(cred_path):
            logger.warning(f"Firebase credentials not found at {cred_path}")
            return
            
        # Initialize Firebase app
        cred = credentials.Certificate(cred_path)
        firebase_app = firebase_admin.initialize_app(cred, {
            'databaseURL': app.config.get('FIREBASE_DATABASE_URL', 'https://visual-dm-default-rtdb.firebaseio.com')
        })
        
        # Initialize Firestore and Realtime Database clients
        firestore_client = firestore.client()
        realtime_db = db
        
        logger.info("Firebase initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        raise

def get_firestore() -> firestore.Client:
    """Get the Firestore client instance."""
    if not firestore_client:
        raise RuntimeError("Firebase not initialized")
    return firestore_client

def get_realtime_db():
    """Get the Realtime Database instance."""
    if not realtime_db:
        raise RuntimeError("Firebase not initialized")
    return realtime_db 