class GameEngineError(Exception):
    """Base exception for game engine errors."""
    pass

class StorageError(GameEngineError):
    """Exception for storage-related errors."""
    pass

class ConfigError(GameEngineError):
    """Exception for configuration-related errors."""
    pass 