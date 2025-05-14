"""
Centralized Logging Package.

This package provides a standardized logging system with configurable formatters,
log levels, and consistent metadata across the application. It also includes
retention and rotation policies for managing log files.
"""

from app.core.logging.config import (
    LoggingConfig, 
    LogLevel, 
    LogFormat, 
    logging_config,
    get_formatter,
    configure_logger,
    update_configuration
)

from app.core.logging.handlers import (
    get_logger,
    log_with_context,
    log_request,
    log_performance,
    log_error,
    log_security_event,
    log_database_operation
)

# Import from the new retention module
from app.core.logging.retention import (
    RetentionConfig,
    RetentionPeriod,
    RotationTrigger,
    retention_config,
    setup_retention,
    enforce_retention_policy,
    place_on_legal_hold,
    remove_from_legal_hold,
    update_retention_configuration
)

# Import from the new security module
from app.core.logging.security import (
    MaskingTechnique,
    SensitiveDataType,
    DataProtectionConfig,
    LogAccessRole,
    LogAccessControl,
    SecureLogger,
    data_protection_config,
    log_access_control,
    secure_logger,
    mask_sensitive_data,
    log_audit_event,
    require_log_permission
)

# Import from the compliance module
from app.core.logging.compliance import (
    ComplianceFramework,
    DataCategory,
    ComplianceConfig,
    compliance_config,
    handle_data_subject_request,
    register_breach_notification_contact,
    log_data_breach,
    generate_compliance_report
)

# Configure the standard logging by default
logging_config = LoggingConfig()

# Create a global retention configuration
retention_config = RetentionConfig()

# Export all important names
__all__ = [
    # From config
    'LoggingConfig',
    'LogLevel',
    'LogFormat',
    'logging_config',
    'get_formatter',
    'configure_logger',
    'update_configuration',
    
    # From handlers
    'get_logger',
    'log_with_context',
    'log_request',
    'log_performance',
    'log_error',
    'log_security_event',
    'log_database_operation',
    
    # From retention
    'RetentionConfig',
    'RetentionPeriod',
    'RotationTrigger',
    'retention_config',
    'setup_retention',
    'enforce_retention_policy',
    'place_on_legal_hold',
    'remove_from_legal_hold',
    'update_retention_configuration',
    
    # From security
    'MaskingTechnique',
    'SensitiveDataType',
    'DataProtectionConfig',
    'LogAccessRole',
    'LogAccessControl',
    'SecureLogger',
    'data_protection_config',
    'log_access_control',
    'secure_logger',
    'mask_sensitive_data',
    'log_audit_event',
    'require_log_permission',
    
    # From compliance
    'ComplianceFramework',
    'DataCategory',
    'ComplianceConfig',
    'compliance_config',
    'handle_data_subject_request',
    'register_breach_notification_contact',
    'log_data_breach',
    'generate_compliance_report'
] 