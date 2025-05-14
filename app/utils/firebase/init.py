"""
Centralized Firebase initialization module.
"""

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials
from google.cloud import firestore
from flask import current_app

logger = logging.getLogger(__name__)

def initialize_firebase(testing=False):
    """
    Initialize Firebase with the appropriate configuration.
    
    Args:
        testing (bool): Whether to use test configuration
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        if not firebase_admin._apps:
            if testing:
                # Use test configuration
                cred = credentials.Certificate(current_app.config['FIREBASE_CREDENTIALS'])
            else:
                # Use production configuration
                if 'FIREBASE_CREDENTIALS' in os.environ:
                    cred_json = json.loads(os.environ['FIREBASE_CREDENTIALS'])
                    cred = credentials.Certificate(cred_json)
                else:
                    cred_path = os.path.join(os.path.dirname(__file__), '..', '..', 'firebase-credentials.json')
                    cred = credentials.Certificate(cred_path)
            
            # Initialize app with database URL
            firebase_admin.initialize_app(cred, {
                'databaseURL': current_app.config.get('FIREBASE_DATABASE_URL', 
                                                   'https://visual-dm-default-rtdb.firebaseio.com')
            })
            
            # Initialize Firestore client
            db = firestore.Client()
            current_app.extensions['firestore'] = db
            
            logger.info("Firebase initialized successfully")
            return True
        logger.info("Firebase already initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        if testing:
            # In test mode, create mock clients
            from unittest.mock import MagicMock
            current_app.extensions['firestore'] = MagicMock()
            return True
        return False 