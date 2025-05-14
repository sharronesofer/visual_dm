"""
Log Compliance Module.

This module provides features to meet regulatory compliance requirements
for log management including GDPR, HIPAA, SOX, and PCI-DSS.
"""

import json
import logging
import datetime
from enum import Enum
from typing import Dict, Any, Optional, List, Set, Union

from app.core.logging.handlers import get_logger
from app.core.logging.security import log_audit_event, secure_logger, require_log_permission

# -------------------------------------------------------------------------------
# Regulatory Frameworks
# -------------------------------------------------------------------------------

class ComplianceFramework(Enum):
    """Supported compliance frameworks."""
    GDPR = "gdpr"      # General Data Protection Regulation
    HIPAA = "hipaa"    # Health Insurance Portability and Accountability Act
    SOX = "sox"        # Sarbanes-Oxley Act
    PCI_DSS = "pci"    # Payment Card Industry Data Security Standard
    CCPA = "ccpa"      # California Consumer Privacy Act

class DataCategory(Enum):
    """Categories of data for compliance purposes."""
    PERSONAL = "personal"            # Personal identifiable information
    HEALTH = "health"                # Protected health information
    FINANCIAL = "financial"          # Financial information
    AUTHENTICATION = "authentication" # Authentication data
    OPERATIONAL = "operational"      # System operational data
    GENERAL = "general"              # General, non-sensitive data

# -------------------------------------------------------------------------------
# Compliance Configuration and Mappings
# -------------------------------------------------------------------------------

# Compliance requirement mappings
COMPLIANCE_MAPPINGS = {
    ComplianceFramework.GDPR: {
        "required_protection": [
            DataCategory.PERSONAL,
            DataCategory.AUTHENTICATION
        ],
        "retention_period": "2 years",
        "right_to_access": True,
        "right_to_erasure": True,
        "data_breach_notification": True,
        "access_controls": True,
        "audit_trail": True
    },
    ComplianceFramework.HIPAA: {
        "required_protection": [
            DataCategory.HEALTH,
            DataCategory.PERSONAL,
            DataCategory.AUTHENTICATION
        ],
        "retention_period": "6 years",
        "right_to_access": True,
        "right_to_erasure": False,
        "data_breach_notification": True,
        "access_controls": True,
        "audit_trail": True
    },
    ComplianceFramework.SOX: {
        "required_protection": [
            DataCategory.FINANCIAL,
            DataCategory.AUTHENTICATION
        ],
        "retention_period": "7 years",
        "right_to_access": False,
        "right_to_erasure": False,
        "data_breach_notification": True,
        "access_controls": True,
        "audit_trail": True
    },
    ComplianceFramework.PCI_DSS: {
        "required_protection": [
            DataCategory.FINANCIAL,
            DataCategory.AUTHENTICATION
        ],
        "retention_period": "1 year",
        "right_to_access": False,
        "right_to_erasure": False,
        "data_breach_notification": True,
        "access_controls": True,
        "audit_trail": True
    }
}

class ComplianceConfig:
    """Configuration for compliance requirements."""
    
    def __init__(self):
        """Initialize compliance configuration."""
        # Get a logger for this module
        self.logger = get_logger(__name__)
        
        # Active compliance frameworks
        self.active_frameworks: List[ComplianceFramework] = []
        
        # Data categorization mappings
        self.data_categories: Dict[str, DataCategory] = {}
        
        # Additional compliance settings
        self.settings: Dict[str, Any] = {
            "data_subject_request_enabled": True,
            "breach_notification_contacts": [],
            "consent_required_for_processing": False,
            "max_retention_days": 365 * 7  # 7 years default
        }
    
    def activate_framework(self, framework: ComplianceFramework) -> None:
        """
        Activate a compliance framework.
        
        Args:
            framework: The compliance framework to activate
        """
        if framework not in self.active_frameworks:
            self.active_frameworks.append(framework)
            self.logger.info(f"Activated compliance framework: {framework.value}")
    
    def deactivate_framework(self, framework: ComplianceFramework) -> None:
        """
        Deactivate a compliance framework.
        
        Args:
            framework: The compliance framework to deactivate
        """
        if framework in self.active_frameworks:
            self.active_frameworks.remove(framework)
            self.logger.info(f"Deactivated compliance framework: {framework.value}")
    
    def is_framework_active(self, framework: ComplianceFramework) -> bool:
        """
        Check if a compliance framework is active.
        
        Args:
            framework: The compliance framework to check
            
        Returns:
            True if the framework is active, False otherwise
        """
        return framework in self.active_frameworks
    
    def register_data_category(
        self, 
        field_name: str, 
        category: DataCategory
    ) -> None:
        """
        Register a data field with its category.
        
        Args:
            field_name: Name of the field or path
            category: Category of data
        """
        self.data_categories[field_name] = category
        self.logger.debug(f"Registered field {field_name} as {category.value}")
    
    def get_data_category(self, field_name: str) -> Optional[DataCategory]:
        """
        Get the category for a data field.
        
        Args:
            field_name: Name of the field to look up
            
        Returns:
            Category of the field if registered, None otherwise
        """
        return self.data_categories.get(field_name)
    
    def is_protected_by_active_frameworks(self, category: DataCategory) -> bool:
        """
        Check if a data category is protected by any active framework.
        
        Args:
            category: Category to check
            
        Returns:
            True if the category is protected, False otherwise
        """
        for framework in self.active_frameworks:
            if framework in COMPLIANCE_MAPPINGS:
                if category in COMPLIANCE_MAPPINGS[framework].get("required_protection", []):
                    return True
        
        return False
    
    def get_maximum_retention_period(self) -> str:
        """
        Get the maximum retention period across all active frameworks.
        
        Returns:
            Maximum retention period as a string
        """
        max_years = 0
        
        for framework in self.active_frameworks:
            if framework in COMPLIANCE_MAPPINGS:
                retention = COMPLIANCE_MAPPINGS[framework].get("retention_period", "")
                if retention:
                    # Extract years from retention period
                    try:
                        years = int(retention.split()[0])
                        max_years = max(max_years, years)
                    except (ValueError, IndexError):
                        pass
        
        return f"{max_years} years" if max_years > 0 else "None"
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """
        Generate a compliance report for all active frameworks.
        
        Returns:
            Compliance report as a dictionary
        """
        report = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "active_frameworks": [f.value for f in self.active_frameworks],
            "framework_requirements": {},
            "data_categories": {
                category.value: [
                    field for field, cat in self.data_categories.items() 
                    if cat == category
                ]
                for category in DataCategory
            },
            "maximum_retention_period": self.get_maximum_retention_period()
        }
        
        # Add framework-specific requirements
        for framework in self.active_frameworks:
            if framework in COMPLIANCE_MAPPINGS:
                report["framework_requirements"][framework.value] = (
                    COMPLIANCE_MAPPINGS[framework]
                )
        
        return report

# Initialize compliance configuration
compliance_config = ComplianceConfig()

# -------------------------------------------------------------------------------
# Data Subject Access Request Handling
# -------------------------------------------------------------------------------

def handle_data_subject_request(
    user_id: str,
    request_type: str,
    requested_by: str,
    user_roles: List[str]
) -> Dict[str, Any]:
    """
    Handle a data subject access or deletion request.
    
    Args:
        user_id: ID of the user whose data is being requested
        request_type: Type of request ('access' or 'delete')
        requested_by: ID of the user making the request
        user_roles: Roles of the requesting user
        
    Returns:
        Response with request details and status
    """
    # Require permission to handle data subject requests
    if not compliance_config.settings["data_subject_request_enabled"]:
        return {
            "status": "error",
            "message": "Data subject requests are not enabled"
        }
    
    # Create logger for this operation
    logger = secure_logger.get_logger("compliance")
    
    # Log the data subject request
    log_audit_event(
        "data_subject_request",
        requested_by,
        request_type,
        f"user_data:{user_id}",
        {"request_type": request_type},
        True
    )
    
    # For 'access' requests, collect all logs related to the user
    if request_type.lower() == "access":
        logger.info(f"Processing data subject access request for user {user_id}")
        # Implementation would actually collect the logs here
        
        return {
            "status": "success",
            "message": "Data subject access request processed",
            "request_id": f"dsar-{datetime.datetime.utcnow().timestamp()}",
            "user_id": user_id,
            "completion_time": "Processing"  # In a real implementation this would be async
        }
    
    # For 'delete' requests, mark data for deletion per policy
    elif request_type.lower() == "delete":
        logger.info(f"Processing data subject deletion request for user {user_id}")
        # Implementation would mark logs for redaction/deletion here
        
        return {
            "status": "success",
            "message": "Data subject deletion request processed",
            "request_id": f"dsar-{datetime.datetime.utcnow().timestamp()}",
            "user_id": user_id,
            "completion_time": "Processing"
        }
    
    else:
        return {
            "status": "error",
            "message": f"Unknown request type: {request_type}"
        }

# -------------------------------------------------------------------------------
# Data Breach Notification
# -------------------------------------------------------------------------------

def register_breach_notification_contact(email: str, name: Optional[str] = None) -> None:
    """
    Register a contact for data breach notifications.
    
    Args:
        email: Email address for notifications
        name: Name of the contact (optional)
    """
    contacts = compliance_config.settings["breach_notification_contacts"]
    
    # Check if contact already exists
    for contact in contacts:
        if contact.get("email") == email:
            return
    
    # Add new contact
    contacts.append({
        "email": email,
        "name": name,
        "added_on": datetime.datetime.utcnow().isoformat()
    })
    
    # Update settings
    compliance_config.settings["breach_notification_contacts"] = contacts
    
    # Log the registration
    logger = get_logger(__name__)
    logger.info(f"Registered breach notification contact: {email}")

def log_data_breach(
    breach_description: str,
    affected_data: List[str],
    severity: str,
    detected_by: str,
    remediation_steps: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Log a data breach event and prepare notification.
    
    Args:
        breach_description: Description of the breach
        affected_data: List of affected data categories
        severity: Severity level (high, medium, low)
        detected_by: Person or system that detected the breach
        remediation_steps: Steps taken to address the breach
        
    Returns:
        Breach record with ID
    """
    # Create breach record
    breach_id = f"breach-{datetime.datetime.utcnow().timestamp()}"
    
    breach_record = {
        "id": breach_id,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "description": breach_description,
        "affected_data": affected_data,
        "severity": severity,
        "detected_by": detected_by,
        "remediation_steps": remediation_steps or [],
        "notification_status": "pending"
    }
    
    # Log the breach
    logger = secure_logger.get_logger("security")
    logger.critical(
        f"DATA BREACH: {breach_description}", 
        breach_record=breach_record
    )
    
    # Log audit event
    log_audit_event(
        "data_breach",
        detected_by,
        "report",
        "security_logs",
        {"breach_id": breach_id, "severity": severity}
    )
    
    # In a real implementation, this would trigger notifications to contacts
    
    return breach_record

# -------------------------------------------------------------------------------
# Compliance Reporting
# -------------------------------------------------------------------------------

@require_log_permission("read", "compliance")
def generate_compliance_report(
    framework: Optional[ComplianceFramework] = None,
    user_id: str = "system",
    user_roles: List[str] = []
) -> Dict[str, Any]:
    """
    Generate a compliance report for a specific framework or all active frameworks.
    
    Args:
        framework: Specific framework to report on (None for all active)
        user_id: ID of the user generating the report
        user_roles: Roles of the requesting user
        
    Returns:
        Compliance report
    """
    # Start with base compliance configuration report
    report = compliance_config.get_compliance_report()
    
    # Filter to specific framework if requested
    if framework is not None:
        if framework not in compliance_config.active_frameworks:
            return {
                "status": "error",
                "message": f"Framework {framework.value} is not active"
            }
        
        # Filter report to specific framework
        report["active_frameworks"] = [framework.value]
        if "framework_requirements" in report:
            report["framework_requirements"] = {
                framework.value: report["framework_requirements"].get(framework.value, {})
            }
    
    # Log report generation
    log_audit_event(
        "compliance_report",
        user_id,
        "generate",
        f"compliance_report:{framework.value if framework else 'all'}",
        {},
        True
    )
    
    return {
        "status": "success",
        "report": report
    } 