"""
Firebase utilities for managing Firebase operations.
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth, storage, db
from typing import Dict, Any, List, Optional
import os
import logging

logger = logging.getLogger(__name__)

_app = None
_db = None
_auth = None
_storage = None
_firestore = None

def initialize_firebase(credential_path: str = None) -> None:
    """Initialize Firebase with the given credentials."""
    global _app, _db, _auth, _storage, _firestore
    
    if _app is not None:
        return  # Already initialized
        
    try:
        if credential_path is None:
            credential_path = os.getenv('FIREBASE_CREDENTIALS', 'firebase_credentials.json')
            
        cred = credentials.Certificate(credential_path)
        _app = firebase_admin.initialize_app(cred, {
            'databaseURL': os.getenv('FIREBASE_DATABASE_URL', ''),
            'storageBucket': os.getenv('FIREBASE_STORAGE_BUCKET', '')
        })
        
        _db = db
        _auth = auth
        _storage = storage
        _firestore = firestore.client()
        
    except Exception as e:
        raise Exception(f"Failed to initialize Firebase: {str(e)}")

def get_firebase_app():
    """Get the Firebase app instance."""
    if _app is None:
        initialize_firebase()
    return _app

def get_firebase_db():
    """Get the Firebase Realtime Database instance."""
    if _db is None:
        initialize_firebase()
    return _db

def get_firebase_auth():
    """Get the Firebase Auth instance."""
    if _auth is None:
        initialize_firebase()
    return _auth

def get_firebase_storage():
    """Get the Firebase Storage instance."""
    if _storage is None:
        initialize_firebase()
    return _storage

def get_firestore_client():
    """Get the Firestore client instance."""
    if _firestore is None:
        initialize_firebase()
    return _firestore

def get_document(*args, **kwargs):
    """Stub for get_document (Firestore not required for core Flask app)."""
    return None

def set_document(*args, **kwargs):
    """Stub for set_document (Firestore not required for core Flask app)."""
    return None

def update_document(*args, **kwargs):
    """Stub for update_document (Firestore not required for core Flask app)."""
    return None

def get_collection(*args, **kwargs):
    """Stub for get_collection (Firestore not required for core Flask app)."""
    return []

class FirebaseManager:
    """Manager class for Firebase operations."""
    
    def __init__(self, credential_path: str):
        """Initialize Firebase manager."""
        try:
            cred = credentials.Certificate(credential_path)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            self.auth = auth
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise
    
    def create_user(
        self,
        email: str,
        password: str,
        display_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new Firebase user."""
        try:
            user = self.auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name
            }
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            user = self.auth.get_user(user_id)
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name
            }
        except Exception as e:
            logger.error(f"Failed to get user: {str(e)}")
            return None
    
    def update_user(
        self,
        user_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user data."""
        try:
            self.auth.update_user(user_id, **data)
            return self.get_user(user_id)
        except Exception as e:
            logger.error(f"Failed to update user: {str(e)}")
            raise
    
    def delete_user(self, user_id: str) -> None:
        """Delete a user."""
        try:
            self.auth.delete_user(user_id)
        except Exception as e:
            logger.error(f"Failed to delete user: {str(e)}")
            raise
    
    def create_document(
        self,
        collection: str,
        document_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new document in Firestore."""
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.set(data)
            return {
                'id': document_id,
                'data': data
            }
        except Exception as e:
            logger.error(f"Failed to create document: {str(e)}")
            raise
    
    def get_document(
        self,
        collection: str,
        document_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a document from Firestore."""
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                return {
                    'id': doc.id,
                    'data': doc.to_dict()
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get document: {str(e)}")
            raise
    
    def update_document(
        self,
        collection: str,
        document_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a document in Firestore."""
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.update(data)
            return self.get_document(collection, document_id)
        except Exception as e:
            logger.error(f"Failed to update document: {str(e)}")
            raise
    
    def delete_document(self, collection: str, document_id: str) -> None:
        """Delete a document from Firestore."""
        try:
            doc_ref = self.db.collection(collection).document(document_id)
            doc_ref.delete()
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            raise
    
    def query_documents(
        self,
        collection: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query documents in Firestore."""
        try:
            query = self.db.collection(collection)
            if filters:
                for key, value in filters.items():
                    query = query.where(key, '==', value)
            
            docs = query.get()
            return [
                {
                    'id': doc.id,
                    'data': doc.to_dict()
                }
                for doc in docs
            ]
        except Exception as e:
            logger.error(f"Failed to query documents: {str(e)}")
            raise
