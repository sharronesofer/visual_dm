from typing import Dict, Any
import firebase_admin
from firebase_admin import credentials, firestore
from app.core.utils.config_utils import get_config
from app.core.utils.error_handlers import ValidationError

class FirebaseService:
    """Firebase service for handling Firebase-related operations"""
    
    def __init__(self):
        cred_path = get_config('FIREBASE_CREDENTIALS_PATH')
        if not cred_path:
            raise ValidationError("Firebase credentials path not configured")
            
        try:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            raise ValidationError(f"Failed to initialize Firebase: {str(e)}")
    
    def get_document(self, collection: str, doc_id: str) -> Dict[str, Any]:
        """Get a document from Firestore"""
        doc = self.db.collection(collection).document(doc_id).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def set_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> None:
        """Set a document in Firestore"""
        self.db.collection(collection).document(doc_id).set(data)
    
    def update_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> None:
        """Update a document in Firestore"""
        self.db.collection(collection).document(doc_id).update(data)
    
    def delete_document(self, collection: str, doc_id: str) -> None:
        """Delete a document from Firestore"""
        self.db.collection(collection).document(doc_id).delete() 