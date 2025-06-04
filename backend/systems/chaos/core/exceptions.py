"""
Chaos System Exceptions

Custom exceptions for the chaos system.
"""


class ChaosSystemError(Exception):
    """Base exception for chaos system errors"""
    
    def __init__(self, message: str, error_code: str = None, component: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.component = component


class ChaosConfigurationError(ChaosSystemError):
    """Exception raised for configuration errors"""
    
    def __init__(self, message: str, config_key: str = None):
        super().__init__(message, error_code="CONFIG_ERROR", component="configuration")
        self.config_key = config_key


class ChaosEngineError(ChaosSystemError):
    """Exception raised for chaos engine errors"""
    
    def __init__(self, message: str, error_code: str = "ENGINE_ERROR"):
        super().__init__(message, error_code=error_code, component="chaos_engine")


class WarningSystemError(ChaosSystemError):
    """Exception raised for warning system errors"""
    
    def __init__(self, message: str, warning_id: str = None):
        super().__init__(message, error_code="WARNING_ERROR", component="warning_system")
        self.warning_id = warning_id


class NarrativeModeratorError(ChaosSystemError):
    """Exception raised for narrative moderator errors"""
    
    def __init__(self, message: str, theme_id: str = None):
        super().__init__(message, error_code="NARRATIVE_ERROR", component="narrative_moderator")
        self.theme_id = theme_id


class CascadeEngineError(ChaosSystemError):
    """Exception raised for cascade engine errors"""
    
    def __init__(self, message: str, cascade_id: str = None):
        super().__init__(message, error_code="CASCADE_ERROR", component="cascade_engine")
        self.cascade_id = cascade_id


class PressureMonitorError(ChaosSystemError):
    """Exception raised for pressure monitor errors"""
    
    def __init__(self, message: str, pressure_type: str = None):
        super().__init__(message, error_code="PRESSURE_ERROR", component="pressure_monitor")
        self.pressure_type = pressure_type


class EventTriggerError(ChaosSystemError):
    """Exception raised for event trigger errors"""
    
    def __init__(self, message: str, trigger_id: str = None):
        super().__init__(message, error_code="TRIGGER_ERROR", component="event_triggers")
        self.trigger_id = trigger_id


class ChaosRepositoryError(ChaosSystemError):
    """Exception raised for repository/persistence errors"""
    
    def __init__(self, message: str, operation: str = None):
        super().__init__(message, error_code="REPOSITORY_ERROR", component="repository")
        self.operation = operation


class ChaosValidationError(ChaosSystemError):
    """Exception raised for validation errors"""
    
    def __init__(self, message: str, field: str = None, value: str = None):
        super().__init__(message, error_code="VALIDATION_ERROR", component="validation")
        self.field = field
        self.value = value


class ChaosIntegrationError(ChaosSystemError):
    """Exception raised for integration errors with other systems"""
    
    def __init__(self, message: str, system: str = None):
        super().__init__(message, error_code="INTEGRATION_ERROR", component="integration")
        self.system = system


class ChaosTimeoutError(ChaosSystemError):
    """Exception raised for timeout errors"""
    
    def __init__(self, message: str, timeout_seconds: float = None):
        super().__init__(message, error_code="TIMEOUT_ERROR", component="timeout")
        self.timeout_seconds = timeout_seconds


class ChaosResourceError(ChaosSystemError):
    """Exception raised for resource errors (memory, disk, etc.)"""
    
    def __init__(self, message: str, resource_type: str = None):
        super().__init__(message, error_code="RESOURCE_ERROR", component="resources")
        self.resource_type = resource_type 