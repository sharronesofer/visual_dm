"""
Privacy management system for GDPR/CCPA compliance.
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from .error_handler import handle_component_error, ErrorSeverity

logger = logging.getLogger(__name__)

@dataclass
class Consent:
    """User consent information."""
    user_id: str
    consent_type: str
    granted: bool
    timestamp: datetime
    expires: Optional[datetime] = None
    purpose: Optional[str] = None
    version: str = "1.0"

@dataclass
class DataSubject:
    """Data subject information."""
    user_id: str
    email: str
    created_at: datetime
    last_updated: datetime
    data_categories: List[str]
    retention_period: timedelta
    metadata: Optional[Dict[str, Any]] = None

class PrivacyManager:
    """Manages data privacy and GDPR/CCPA compliance."""
    
    def __init__(
        self,
        data_dir: str = "privacy_data",
        retention_period: timedelta = timedelta(days=365)
    ):
        """Initialize the privacy manager.
        
        Args:
            data_dir: Directory for privacy data
            retention_period: Default data retention period
        """
        try:
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)
            
            self.retention_period = retention_period
            
            # Initialize data storage
            self.consents: Dict[str, List[Consent]] = {}
            self.data_subjects: Dict[str, DataSubject] = {}
            
            # Load existing data
            self._load_data()
            
            logger.info("Privacy manager initialized")
            
        except Exception as e:
            handle_component_error(
                "PrivacyManager",
                "__init__",
                e,
                ErrorSeverity.CRITICAL
            )
            raise
            
    def _load_data(self) -> None:
        """Load privacy data from files."""
        try:
            # Load consents
            consents_path = self.data_dir / "consents.json"
            if consents_path.exists():
                with open(consents_path, "r") as f:
                    data = json.load(f)
                    for user_id, consents in data.items():
                        self.consents[user_id] = [
                            Consent(
                                user_id=c["user_id"],
                                consent_type=c["consent_type"],
                                granted=c["granted"],
                                timestamp=datetime.fromisoformat(c["timestamp"]),
                                expires=datetime.fromisoformat(c["expires"]) if c.get("expires") else None,
                                purpose=c.get("purpose"),
                                version=c.get("version", "1.0")
                            )
                            for c in consents
                        ]
                        
            # Load data subjects
            subjects_path = self.data_dir / "subjects.json"
            if subjects_path.exists():
                with open(subjects_path, "r") as f:
                    data = json.load(f)
                    for user_id, subject in data.items():
                        self.data_subjects[user_id] = DataSubject(
                            user_id=subject["user_id"],
                            email=subject["email"],
                            created_at=datetime.fromisoformat(subject["created_at"]),
                            last_updated=datetime.fromisoformat(subject["last_updated"]),
                            data_categories=subject["data_categories"],
                            retention_period=timedelta(days=subject["retention_period_days"]),
                            metadata=subject.get("metadata")
                        )
                        
        except Exception as e:
            handle_component_error(
                "PrivacyManager",
                "_load_data",
                e,
                ErrorSeverity.ERROR
            )
            
    def _save_data(self) -> None:
        """Save privacy data to files."""
        try:
            # Save consents
            consents_path = self.data_dir / "consents.json"
            with open(consents_path, "w") as f:
                json.dump(
                    {
                        user_id: [
                            {
                                "user_id": c.user_id,
                                "consent_type": c.consent_type,
                                "granted": c.granted,
                                "timestamp": c.timestamp.isoformat(),
                                "expires": c.expires.isoformat() if c.expires else None,
                                "purpose": c.purpose,
                                "version": c.version
                            }
                            for c in consents
                        ]
                        for user_id, consents in self.consents.items()
                    },
                    f,
                    indent=4
                )
                
            # Save data subjects
            subjects_path = self.data_dir / "subjects.json"
            with open(subjects_path, "w") as f:
                json.dump(
                    {
                        user_id: {
                            "user_id": subject.user_id,
                            "email": subject.email,
                            "created_at": subject.created_at.isoformat(),
                            "last_updated": subject.last_updated.isoformat(),
                            "data_categories": subject.data_categories,
                            "retention_period_days": subject.retention_period.days,
                            "metadata": subject.metadata
                        }
                        for user_id, subject in self.data_subjects.items()
                    },
                    f,
                    indent=4
                )
                
        except Exception as e:
            handle_component_error(
                "PrivacyManager",
                "_save_data",
                e,
                ErrorSeverity.ERROR
            )
            
    def register_data_subject(
        self,
        user_id: str,
        email: str,
        data_categories: List[str],
        retention_period: Optional[timedelta] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a new data subject.
        
        Args:
            user_id: User ID
            email: User email
            data_categories: Categories of data collected
            retention_period: Data retention period
            metadata: Additional metadata
        """
        try:
            now = datetime.now()
            
            subject = DataSubject(
                user_id=user_id,
                email=email,
                created_at=now,
                last_updated=now,
                data_categories=data_categories,
                retention_period=retention_period or self.retention_period,
                metadata=metadata
            )
            
            self.data_subjects[user_id] = subject
            self._save_data()
            
            logger.info(f"Registered data subject: {user_id}")
            
        except Exception as e:
            handle_component_error(
                "PrivacyManager",
                "register_data_subject",
                e,
                ErrorSeverity.ERROR
            )
            
    def update_data_subject(
        self,
        user_id: str,
        data_categories: Optional[List[str]] = None,
        retention_period: Optional[timedelta] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Update data subject information.
        
        Args:
            user_id: User ID
            data_categories: Updated data categories
            retention_period: Updated retention period
            metadata: Updated metadata
        """
        try:
            if user_id not in self.data_subjects:
                raise ValueError(f"Data subject not found: {user_id}")
                
            subject = self.data_subjects[user_id]
            
            if data_categories:
                subject.data_categories = data_categories
                
            if retention_period:
                subject.retention_period = retention_period
                
            if metadata:
                subject.metadata = metadata
                
            subject.last_updated = datetime.now()
            self._save_data()
            
            logger.info(f"Updated data subject: {user_id}")
            
        except Exception as e:
            handle_component_error(
                "PrivacyManager",
                "update_data_subject",
                e,
                ErrorSeverity.ERROR
            )
            
    def request_consent(
        self,
        user_id: str,
        consent_type: str,
        purpose: str,
        expires: Optional[datetime] = None
    ) -> bool:
        """Request user consent.
        
        Args:
            user_id: User ID
            consent_type: Type of consent
            purpose: Purpose of consent
            expires: Consent expiry date
            
        Returns:
            True if consent granted, False otherwise
        """
        try:
            if user_id not in self.data_subjects:
                raise ValueError(f"Data subject not found: {user_id}")
                
            # Check existing consent
            if user_id in self.consents:
                for consent in self.consents[user_id]:
                    if (
                        consent.consent_type == consent_type
                        and consent.granted
                        and (not consent.expires or consent.expires > datetime.now())
                    ):
                        return True
                        
            # Request new consent
            # TODO: Implement actual consent request UI/API
            granted = True  # Placeholder
            
            consent = Consent(
                user_id=user_id,
                consent_type=consent_type,
                granted=granted,
                timestamp=datetime.now(),
                expires=expires,
                purpose=purpose
            )
            
            if user_id not in self.consents:
                self.consents[user_id] = []
                
            self.consents[user_id].append(consent)
            self._save_data()
            
            logger.info(f"Consent {'granted' if granted else 'denied'} for {user_id}: {consent_type}")
            
            return granted
            
        except Exception as e:
            handle_component_error(
                "PrivacyManager",
                "request_consent",
                e,
                ErrorSeverity.ERROR
            )
            return False
            
    def revoke_consent(self, user_id: str, consent_type: str) -> None:
        """Revoke user consent.
        
        Args:
            user_id: User ID
            consent_type: Type of consent
        """
        try:
            if user_id in self.consents:
                self.consents[user_id] = [
                    consent for consent in self.consents[user_id]
                    if consent.consent_type != consent_type
                ]
                self._save_data()
                
            logger.info(f"Revoked consent for {user_id}: {consent_type}")
            
        except Exception as e:
            handle_component_error(
                "PrivacyManager",
                "revoke_consent",
                e,
                ErrorSeverity.ERROR
            )
            
    def get_data_subject(self, user_id: str) -> Optional[DataSubject]:
        """Get data subject information.
        
        Args:
            user_id: User ID
            
        Returns:
            Data subject information if found
        """
        try:
            return self.data_subjects.get(user_id)
            
        except Exception as e:
            handle_component_error(
                "PrivacyManager",
                "get_data_subject",
                e,
                ErrorSeverity.ERROR
            )
            return None
            
    def get_consents(self, user_id: str) -> List[Consent]:
        """Get user consents.
        
        Args:
            user_id: User ID
            
        Returns:
            List of user consents
        """
        try:
            return self.consents.get(user_id, [])
            
        except Exception as e:
            handle_component_error(
                "PrivacyManager",
                "get_consents",
                e,
                ErrorSeverity.ERROR
            )
            return []
            
    def delete_data_subject(self, user_id: str) -> None:
        """Delete data subject and associated data.
        
        Args:
            user_id: User ID
        """
        try:
            if user_id in self.data_subjects:
                del self.data_subjects[user_id]
                
            if user_id in self.consents:
                del self.consents[user_id]
                
            self._save_data()
            
            logger.info(f"Deleted data subject: {user_id}")
            
        except Exception as e:
            handle_component_error(
                "PrivacyManager",
                "delete_data_subject",
                e,
                ErrorSeverity.ERROR
            )
            
    def cleanup(self) -> None:
        """Clean up privacy resources."""
        try:
            # Save any pending changes
            self._save_data()
            
            # Clear data
            self.consents.clear()
            self.data_subjects.clear()
            
            logger.info("Privacy manager cleaned up")
            
        except Exception as e:
            handle_component_error(
                "PrivacyManager",
                "cleanup",
                e,
                ErrorSeverity.ERROR
            ) 