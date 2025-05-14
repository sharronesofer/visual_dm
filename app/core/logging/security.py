"""
Secure Log Management Module.

This module provides field-level redaction for sensitive information, role-based access
controls, comprehensive audit trails, and compliance features to meet regulatory
requirements like GDPR and HIPAA.
"""

import os
import re
import copy
import json
import hashlib
import logging
import functools
from enum import Enum, auto
from datetime import datetime
from typing import Dict, Any, Optional, List, Set, Callable, Pattern, Union, TypeVar, cast

from app.core.logging.config import LoggingConfig, logging_config
from app.core.logging.handlers import get_logger, log_with_context

# Type variables for function decorator
F = TypeVar('F', bound=Callable[..., Any])

# -------------------------------------------------------------------------------
# Data Protection
# -------------------------------------------------------------------------------

class MaskingTechnique(Enum):
    """Techniques for masking sensitive data."""
    COMPLETE_REDACTION = "complete_redaction"  # Replace with [REDACTED]
    PARTIAL_MASKING = "partial_masking"        # Show only first/last few chars
    HASHING = "hashing"                        # Replace with SHA-256 hash
    TOKENIZATION = "tokenization"              # Replace with a token

class SensitiveDataType(Enum):
    """Common types of sensitive data."""
    CREDIT_CARD = "credit_card"
    SSN = "ssn"
    EMAIL = "email"
    PASSWORD = "password"
    API_KEY = "api_key"
    PHONE_NUMBER = "phone_number"
    ADDRESS = "address"
    NAME = "name"
    IP_ADDRESS = "ip_address"
    CUSTOM = "custom"  # For custom patterns

# Default patterns for detecting sensitive data
DEFAULT_PATTERNS = {
    SensitiveDataType.CREDIT_CARD: r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    SensitiveDataType.SSN: r'\b\d{3}-\d{2}-\d{4}\b',
    SensitiveDataType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    SensitiveDataType.PASSWORD: r'password["\s:=]+["\s]*[^"\s]+["\s]*',
    SensitiveDataType.API_KEY: r'(?:api|auth|token|secret|key)[_-]?(?:key|token|secret)?["\s:=]+["\s]*[A-Za-z0-9_\-\.]+["\s]*',
    SensitiveDataType.PHONE_NUMBER: r'\b(?:\+\d{1,3}[-\s]?)?\(?\d{3}\)?[-\s]?\d{3}[-\s]?\d{4}\b',
    SensitiveDataType.IP_ADDRESS: r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
}

class DataProtectionConfig:
    """Configuration for data protection in logs."""
    
    def __init__(self, env_prefix: str = "LOG_PROTECTION_"):
        """
        Initialize data protection configuration from environment variables.
        
        Args:
            env_prefix: Prefix for environment variables used for configuration
        """
        self.env_prefix = env_prefix
        self._config = {}
        self._load_from_env()
        self._compiled_patterns = {}
        self._compile_patterns()
        
    def _load_from_env(self) -> None:
        """Load data protection configuration from environment variables."""
        # Enable/disable protection
        self._config["enabled"] = self._parse_bool(
            self._get_env("ENABLED", "true")
        )
        
        # Default masking technique
        self._config["default_technique"] = self._get_env(
            "DEFAULT_TECHNIQUE", MaskingTechnique.COMPLETE_REDACTION.value
        )
        
        # Sensitive data types to protect
        sensitive_types = self._get_env("SENSITIVE_TYPES", "")
        if sensitive_types:
            self._config["sensitive_types"] = [
                t.strip() for t in sensitive_types.split(",")
            ]
        else:
            # Default to protecting common sensitive data
            self._config["sensitive_types"] = [
                SensitiveDataType.CREDIT_CARD.value,
                SensitiveDataType.SSN.value,
                SensitiveDataType.EMAIL.value,
                SensitiveDataType.PASSWORD.value,
                SensitiveDataType.API_KEY.value
            ]
            
        # Custom patterns
        custom_patterns = self._get_env("CUSTOM_PATTERNS", "")
        self._config["custom_patterns"] = {}
        if custom_patterns:
            for pattern_def in custom_patterns.split(";"):
                if ":" in pattern_def:
                    name, pattern = pattern_def.split(":", 1)
                    self._config["custom_patterns"][name.strip()] = pattern.strip()
                    
        # Field-specific protection
        field_protection = self._get_env("FIELD_PROTECTION", "")
        self._config["field_protection"] = {}
        if field_protection:
            for field_def in field_protection.split(";"):
                if ":" in field_def:
                    field, technique = field_def.split(":", 1)
                    self._config["field_protection"][field.strip()] = technique.strip()
        
    def _get_env(self, name: str, default: str) -> str:
        """Get environment variable with prefix."""
        return os.environ.get(f"{self.env_prefix}{name}", default)
    
    def _parse_bool(self, value: str) -> bool:
        """Parse string boolean value from environment variable."""
        return value.lower() in ("true", "yes", "1", "y", "t")
    
    def _compile_patterns(self) -> None:
        """Compile regex patterns for better performance."""
        # Compile default patterns for enabled sensitive data types
        for data_type in self._config["sensitive_types"]:
            try:
                enum_type = SensitiveDataType(data_type)
                if enum_type in DEFAULT_PATTERNS:
                    pattern = DEFAULT_PATTERNS[enum_type]
                    self._compiled_patterns[data_type] = re.compile(pattern)
            except ValueError:
                pass
                
        # Compile custom patterns
        for name, pattern in self._config["custom_patterns"].items():
            try:
                self._compiled_patterns[name] = re.compile(pattern)
            except re.error:
                # Log compilation error but continue
                logger = get_logger(__name__)
                logger.error(f"Invalid regex pattern for {name}: {pattern}")
    
    @property
    def enabled(self) -> bool:
        """Check if data protection is enabled."""
        return self._config["enabled"]
    
    @property
    def default_technique(self) -> MaskingTechnique:
        """Get the default masking technique."""
        try:
            return MaskingTechnique(self._config["default_technique"])
        except ValueError:
            return MaskingTechnique.COMPLETE_REDACTION
    
    @property
    def sensitive_types(self) -> List[str]:
        """Get the list of sensitive data types to protect."""
        return self._config["sensitive_types"]
    
    @property
    def custom_patterns(self) -> Dict[str, str]:
        """Get custom regex patterns for sensitive data."""
        return self._config["custom_patterns"]
    
    @property
    def field_protection(self) -> Dict[str, str]:
        """Get field-specific protection techniques."""
        return self._config["field_protection"]
    
    @property
    def compiled_patterns(self) -> Dict[str, Pattern]:
        """Get compiled regex patterns for better performance."""
        return self._compiled_patterns
    
    def as_dict(self) -> Dict[str, Any]:
        """Get the configuration as a dictionary."""
        # Return a safe copy without compiled patterns
        config = self._config.copy()
        return config

# Initialize data protection configuration
data_protection_config = DataProtectionConfig()

# -------------------------------------------------------------------------------
# Data Masking Implementation
# -------------------------------------------------------------------------------

def apply_masking(
    data: Any, 
    technique: MaskingTechnique = MaskingTechnique.COMPLETE_REDACTION,
    field_path: str = ""
) -> Any:
    """
    Apply the specified masking technique to data.
    
    Args:
        data: Data to mask
        technique: Masking technique to apply
        field_path: Path to the current field (for field-specific techniques)
        
    Returns:
        Masked data
    """
    # Skip masking for None values
    if data is None:
        return None
        
    # Check for field-specific technique override
    if field_path in data_protection_config.field_protection:
        try:
            technique = MaskingTechnique(data_protection_config.field_protection[field_path])
        except ValueError:
            pass
    
    # Apply technique based on data type
    if isinstance(data, str):
        if technique == MaskingTechnique.COMPLETE_REDACTION:
            return "[REDACTED]"
        elif technique == MaskingTechnique.PARTIAL_MASKING:
            if len(data) <= 6:
                return "***" 
            else:
                return f"{data[:2]}{'*' * (len(data) - 4)}{data[-2:]}"
        elif technique == MaskingTechnique.HASHING:
            return hashlib.sha256(data.encode()).hexdigest()
        elif technique == MaskingTechnique.TOKENIZATION:
            # Simple tokenization by hashing and taking first 8 chars
            return f"TOK_{hashlib.md5(data.encode()).hexdigest()[:8]}"
    elif isinstance(data, (int, float)):
        if technique == MaskingTechnique.COMPLETE_REDACTION:
            return 0
        elif technique == MaskingTechnique.PARTIAL_MASKING:
            # Return order of magnitude for numbers
            return 10 ** (len(str(int(data))) - 1)
        else:
            # Other techniques don't make sense for numbers
            return "[REDACTED]"
    
    # Default behavior for unsupported types
    return "[REDACTED]"

def mask_sensitive_data(
    data: Any, 
    field_path: str = "",
    config: Optional[DataProtectionConfig] = None
) -> Any:
    """
    Recursively mask sensitive data in a complex data structure.
    
    Args:
        data: Data structure to process
        field_path: Current field path for nested structures
        config: Data protection configuration
        
    Returns:
        A copy of the data with sensitive information masked
    """
    config = config or data_protection_config
    
    # Skip processing if protection is disabled
    if not config.enabled:
        return data
    
    # Make a deep copy to avoid modifying the original
    result = copy.deepcopy(data)
    
    # Process based on data type
    if isinstance(result, dict):
        for key, value in list(result.items()):
            # Build the field path
            current_path = f"{field_path}.{key}" if field_path else key
            
            # Check if this field should be masked based on its name
            should_mask = any(
                sensitive_key in key.lower() 
                for sensitive_key in ["password", "secret", "token", "key", "auth", "credit", "ssn", "social"]
            )
            
            if should_mask:
                result[key] = apply_masking(value, config.default_technique, current_path)
            else:
                # Recursively process nested data
                result[key] = mask_sensitive_data(value, current_path, config)
                
    elif isinstance(result, list):
        for i, item in enumerate(result):
            current_path = f"{field_path}[{i}]"
            result[i] = mask_sensitive_data(item, current_path, config)
            
    elif isinstance(result, str):
        # Process strings for pattern matching
        for data_type, pattern in config.compiled_patterns.items():
            if pattern.search(result):
                technique = config.default_technique
                if field_path in config.field_protection:
                    try:
                        technique = MaskingTechnique(config.field_protection[field_path])
                    except ValueError:
                        pass
                return apply_masking(result, technique, field_path)
    
    return result

# -------------------------------------------------------------------------------
# Access Control
# -------------------------------------------------------------------------------

class LogAccessRole(Enum):
    """Standard roles for log access control."""
    ADMIN = "admin"                # Full access to all logs
    SECURITY_AUDIT = "security"    # Access to security and audit logs
    OPERATIONS = "operations"      # Access to operational logs
    DEVELOPER = "developer"        # Access to development and debug logs
    READ_ONLY = "read_only"        # Read-only access to non-sensitive logs
    COMPLIANCE = "compliance"      # Access focused on compliance-related logs

class LogAccessControl:
    """Access control for the logging system."""
    
    def __init__(self):
        """Initialize the access control system."""
        # Role to permissions mapping
        self.role_permissions: Dict[str, Set[str]] = {
            LogAccessRole.ADMIN.value: {"read:*", "write:*", "export:*", "configure:*"},
            LogAccessRole.SECURITY_AUDIT.value: {"read:security", "read:audit", "read:error", "export:security", "export:audit"},
            LogAccessRole.OPERATIONS.value: {"read:performance", "read:system", "read:application", "export:performance"},
            LogAccessRole.DEVELOPER.value: {"read:debug", "read:error", "read:application"},
            LogAccessRole.READ_ONLY.value: {"read:application", "read:system"},
            LogAccessRole.COMPLIANCE.value: {"read:audit", "read:compliance", "export:compliance", "export:audit"}
        }
        
        # Log type to category mapping
        self.log_categories: Dict[str, str] = {
            "auth": "security",
            "login": "security",
            "user": "application",
            "api": "application",
            "performance": "performance",
            "error": "error",
            "exception": "error",
            "audit": "audit",
            "compliance": "compliance",
            "gdpr": "compliance",
            "hipaa": "compliance",
            "debug": "debug",
            "system": "system"
        }
    
    def has_permission(
        self, 
        user_roles: List[str], 
        permission: str, 
        log_type: Optional[str] = None
    ) -> bool:
        """
        Check if user has the specified permission.
        
        Args:
            user_roles: List of user roles
            permission: Permission to check (e.g., 'read', 'export')
            log_type: Optional log type to check permission for
            
        Returns:
            True if user has permission, False otherwise
        """
        if not user_roles or not permission:
            return False
            
        # Determine category from log type
        category = "*"
        if log_type:
            category = self.log_categories.get(log_type.lower(), "application")
            
        # Check for exact permission match
        permission_check = f"{permission}:{category}"
        wildcard_check = f"{permission}:*"
        
        for role in user_roles:
            role_perms = self.role_permissions.get(role, set())
            if permission_check in role_perms or wildcard_check in role_perms:
                return True
                
        return False
    
    def filter_logs(
        self,
        logs: List[Dict[str, Any]],
        user_roles: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Filter logs based on user's roles and permissions.
        
        Args:
            logs: List of log entries
            user_roles: List of user roles
            
        Returns:
            Filtered list of logs the user has permission to view
        """
        if not logs:
            return []
            
        filtered_logs = []
        for log in logs:
            # Determine log type from category field or default to application
            log_type = log.get("category", "application")
            
            # Check if user has read permission for this log type
            if self.has_permission(user_roles, "read", log_type):
                filtered_logs.append(log)
                
        return filtered_logs

# Initialize access control
log_access_control = LogAccessControl()

# -------------------------------------------------------------------------------
# Audit Trail
# -------------------------------------------------------------------------------

def log_audit_event(
    event_type: str,
    user_id: str,
    action: str,
    resource: str,
    details: Optional[Dict[str, Any]] = None,
    success: bool = True,
    ip_address: Optional[str] = None,
    logger: Optional[logging.Logger] = None
) -> None:
    """
    Log an audit event for log system access and access control events.
    This function is used by the unified access control service for auditing all permission checks.
    
    Args:
        event_type: Type of event (e.g., 'access', 'export', 'query')
        user_id: ID of the user performing the action
        action: Action performed (e.g., 'read', 'download', 'filter')
        resource: Resource being accessed (e.g., 'error_logs', 'security_logs')
        details: Additional details about the event
        success: Whether the action was successful
        ip_address: Optional IP address of the user
        logger: Logger to use (gets an audit logger if None)
    """
    logger = logger or get_logger("audit")
    
    # Create audit log entry
    log_with_context(
        logging.INFO if success else logging.WARNING,
        f"Audit: {action} {resource} by {user_id} - {'Success' if success else 'Failed'}",
        logger,
        event_type=event_type,
        user_id=user_id,
        action=action,
        resource=resource,
        timestamp=datetime.utcnow().isoformat(),
        success=success,
        ip_address=ip_address,
        **details or {}
    )

# -------------------------------------------------------------------------------
# Secure Logger Implementation
# -------------------------------------------------------------------------------

class SecureLogger:
    """
    Enhanced logger with security features.
    
    Provides data protection, access control, and audit trail capabilities.
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize a secure logger.
        
        Args:
            name: Logger name
        """
        self.logger = get_logger(name)
        self.data_protection = data_protection_config
        self.access_control = log_access_control
        
    def debug(self, message: str, **kwargs) -> None:
        """Log at debug level with sensitive data protection."""
        if self.data_protection.enabled:
            kwargs = mask_sensitive_data(kwargs)
        self.logger.debug(message, extra={"extra": kwargs})
        
    def info(self, message: str, **kwargs) -> None:
        """Log at info level with sensitive data protection."""
        if self.data_protection.enabled:
            kwargs = mask_sensitive_data(kwargs)
        self.logger.info(message, extra={"extra": kwargs})
        
    def warning(self, message: str, **kwargs) -> None:
        """Log at warning level with sensitive data protection."""
        if self.data_protection.enabled:
            kwargs = mask_sensitive_data(kwargs)
        self.logger.warning(message, extra={"extra": kwargs})
        
    def error(self, message: str, **kwargs) -> None:
        """Log at error level with sensitive data protection."""
        if self.data_protection.enabled:
            kwargs = mask_sensitive_data(kwargs)
        self.logger.error(message, extra={"extra": kwargs})
        
    def critical(self, message: str, **kwargs) -> None:
        """Log at critical level with sensitive data protection."""
        if self.data_protection.enabled:
            kwargs = mask_sensitive_data(kwargs)
        self.logger.critical(message, extra={"extra": kwargs})
        
    @staticmethod
    def get_logger(name: Optional[str] = None) -> 'SecureLogger':
        """Get a secure logger instance."""
        return SecureLogger(name)

# -------------------------------------------------------------------------------
# Decorators and Utilities
# -------------------------------------------------------------------------------

def require_log_permission(permission: str, log_type: Optional[str] = None) -> Callable[[F], F]:
    """
    Decorator to enforce log access permissions.
    
    Args:
        permission: Permission required (e.g., 'read', 'export')
        log_type: Optional log type to check permission for
        
    Returns:
        Decorated function that checks permissions
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract user roles from kwargs or context
            user_roles = kwargs.get('user_roles', [])
            
            # Check permission
            if not log_access_control.has_permission(user_roles, permission, log_type):
                # Log failed access attempt
                user_id = kwargs.get('user_id', 'unknown')
                ip_address = kwargs.get('ip_address', None)
                log_audit_event(
                    'access',
                    user_id,
                    permission,
                    log_type or 'logs',
                    {'attempted_operation': func.__name__},
                    False,
                    ip_address
                )
                raise PermissionError(f"User lacks {permission} permission for {log_type or 'logs'}")
                
            # Log successful access
            user_id = kwargs.get('user_id', 'unknown')
            ip_address = kwargs.get('ip_address', None)
            log_audit_event(
                'access',
                user_id,
                permission,
                log_type or 'logs',
                {'operation': func.__name__},
                True,
                ip_address
            )
            
            # Call the function
            return func(*args, **kwargs)
        
        return cast(F, wrapper)
    
    return decorator

# Create a secure logger instance
secure_logger = SecureLogger.get_logger() 