"""
Analytics Middleware
------------------
Middleware for capturing and storing events for analysis and LLM training.

This middleware integrates with the comprehensive Analytics System and
maintains backward compatibility with the existing analytics middleware.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from backend.infrastructure.events.core.event_base import EventBase
from backend.infrastructure.analytics.services.analytics_service import AnalyticsService as NewAnalyticsService, get_analytics_service

logger = logging.getLogger(__name__)

# Import the new comprehensive analytics service
try:
    from backend.infrastructure.analytics.services.analytics_service import AnalyticsService as NewAnalyticsService, get_analytics_service
    ANALYTICS_SERVICE_AVAILABLE = True
except ImportError:
    ANALYTICS_SERVICE_AVAILABLE = False
    logger.warning("New analytics service not available, using legacy implementation")

class AnalyticsService:
    """
    Legacy analytics service for backward compatibility.
    
    This service implements the Analytics System described in the Development Bible,
    capturing events for analysis and LLM training dataset generation.
    """
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'AnalyticsService':
        """Get the singleton instance of the analytics service."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the analytics service."""
        if AnalyticsService._instance is not None:
            raise RuntimeError("AnalyticsService is a singleton. Use get_instance() instead.")
        
        # Default output directory
        self.output_dir = os.environ.get('ANALYTICS_OUTPUT_DIR', 'data/analytics')
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Event categories mapping
        self.event_categories = {
            'memory': ['memory:created', 'memory:reinforced', 'memory:deleted', 'memory:accessed'],
            'rumor': ['rumor:created', 'rumor:spread', 'rumor:mutated'],
            'motif': ['motif:changed', 'motif:activated', 'motif:expired'],
            'population': ['population:changed', 'population:migrated', 'population:threshold'],
            'poi': ['poi:created', 'poi:state_changed', 'poi:discovered'],
            'faction': ['faction:created', 'faction:changed', 'faction:reputation_changed'],
            'quest': ['quest:created', 'quest:updated', 'quest:completed', 'quest:failed'],
            'combat': ['combat:started', 'combat:ended', 'combat:attack', 'combat:damage'],
            'time': ['time:advanced', 'time:day_changed', 'time:month_changed'],
            'storage': ['storage:saved', 'storage:loaded', 'storage:autosaved'],
            'relationship': ['relationship:created', 'relationship:changed', 'relationship:removed'],
            'world_state': ['world_state:created', 'world_state:updated', 'world_state:removed'],
            'system': ['system:startup', 'system:shutdown', 'system:error'],
            'game': ['game:started', 'game:ended', 'game:saved', 'game:loaded'],
            'custom': [],  # For user-defined events
        }
        
        logger.info("Analytics service initialized")
    
    def log_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Log an event to the appropriate analytics file.
        
        Args:
            event_data: Dictionary representation of the event
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get event type and determine category
            event_type = event_data.get('event_type', 'unknown')
            category = self._get_category(event_type)
            
            # Add metadata if not present
            if 'timestamp' not in event_data:
                event_data['timestamp'] = datetime.utcnow().isoformat()
            if 'category' not in event_data:
                event_data['category'] = category
                
            # Determine file path
            file_path = self._get_file_path(category)
            
            # Append event to file
            self._append_to_file(file_path, event_data)
            return True
            
        except Exception as e:
            logger.error(f"Error logging analytics event: {e}")
            return False
    
    async def log_event_async(self, event_data: Dict[str, Any]) -> bool:
        """
        Log an event asynchronously to avoid blocking.
        
        Args:
            event_data: Dictionary representation of the event
            
        Returns:
            bool: True if successful, False otherwise
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.log_event, event_data)
    
    def _get_category(self, event_type: str) -> str:
        """
        Determine the category for an event type.
        
        Args:
            event_type: The event type string
            
        Returns:
            str: Category name
        """
        for category, types in self.event_categories.items():
            if event_type in types or event_type.split(':')[0] == category:
                return category
        return 'misc'  # Default category for unclassified events
    
    def _get_file_path(self, category: str) -> str:
        """
        Generate the file path for a category.
        
        Args:
            category: The event category
            
        Returns:
            str: Path to the appropriate JSON file
        """
        # Use current date for organizing files
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        # Create category subdirectory if it doesn't exist
        category_dir = os.path.join(self.output_dir, category)
        Path(category_dir).mkdir(parents=True, exist_ok=True)
        
        # Return full path to JSON file
        return os.path.join(category_dir, f"{today}.json")
    
    def _append_to_file(self, file_path: str, event_data: Dict[str, Any]) -> None:
        """
        Append an event to a JSON file.
        
        Args:
            file_path: Path to the JSON file
            event_data: Event data to append
        """
        # Load existing data if file exists
        existing_data = []
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    existing_data = json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Could not parse existing JSON in {file_path}, creating new file")
        
        # Append new event
        existing_data.append(event_data)
        
        # Write updated data back to file
        with open(file_path, 'w') as f:
            json.dump(existing_data, f, indent=2)
    
    def generate_dataset(self, 
                         filter_criteria: Optional[Dict[str, Any]] = None,
                         date_range: Optional[List[str]] = None,
                         max_entries: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate a dataset from logged events based on criteria.
        
        Args:
            filter_criteria: Dictionary of field/value pairs to match
            date_range: List of two dates [start_date, end_date] in 'YYYY-MM-DD' format
            max_entries: Maximum number of entries to include
            
        Returns:
            List of matching event dictionaries
        """
        try:
            # Default filter criteria
            if filter_criteria is None:
                filter_criteria = {}
                
            dataset = []
            
            # Determine which files to search
            files_to_search = self._get_files_for_dataset(
                filter_criteria.get('category'),
                date_range
            )
            
            # Process each file
            for file_path in files_to_search:
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        try:
                            data = json.load(f)
                            for event in data:
                                if self._matches_criteria(event, filter_criteria):
                                    dataset.append(event)
                        except json.JSONDecodeError:
                            logger.warning(f"Could not parse JSON in {file_path}")
            
            # Apply max entries limit
            if max_entries is not None and max_entries > 0:
                dataset = dataset[:max_entries]
                
            return dataset
            
        except Exception as e:
            logger.error(f"Error generating dataset: {e}")
            return []
    
    def _get_files_for_dataset(self, 
                              category: Optional[str] = None,
                              date_range: Optional[List[str]] = None) -> List[str]:
        """
        Get list of files to search for dataset generation.
        
        Args:
            category: Optional category to filter by
            date_range: Optional date range [start_date, end_date]
            
        Returns:
            List of file paths to search
        """
        # Start with all categories
        categories = [category] if category else self.event_categories.keys()
        
        # Generate date list
        dates = []
        if date_range and len(date_range) == 2:
            # Parse date range
            try:
                start = datetime.strptime(date_range[0], '%Y-%m-%d')
                end = datetime.strptime(date_range[1], '%Y-%m-%d')
                
                # Generate all dates in range
                current = start
                while current <= end:
                    dates.append(current.strftime('%Y-%m-%d'))
                    current = current.replace(day=current.day + 1)
            except ValueError:
                # If date parsing fails, use all available dates
                dates = []
        
        # If no valid date range, find all existing date files
        if not dates:
            for category_dir in [os.path.join(self.output_dir, cat) for cat in categories]:
                if os.path.exists(category_dir):
                    for file_name in os.listdir(category_dir):
                        if file_name.endswith('.json'):
                            date = file_name[:-5]  # Remove .json extension
                            if date not in dates:
                                dates.append(date)
        
        # Generate full paths
        files = []
        for category in categories:
            for date in dates:
                files.append(os.path.join(self.output_dir, category, f"{date}.json"))
                
        return files
    
    def _matches_criteria(self, event: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """
        Check if an event matches the filter criteria.
        
        Args:
            event: Event dictionary
            criteria: Filter criteria dictionary
            
        Returns:
            bool: True if event matches criteria, False otherwise
        """
        for key, value in criteria.items():
            # Handle nested keys like 'data.user_id'
            if '.' in key:
                parts = key.split('.')
                event_value = event
                for part in parts:
                    if isinstance(event_value, dict) and part in event_value:
                        event_value = event_value[part]
                    else:
                        return False
                
                if event_value != value:
                    return False
            
            # Handle direct key match
            elif key not in event or event[key] != value:
                return False
                
        return True

async def analytics_middleware(event: EventBase, next_middleware: Callable) -> EventBase:
    """
    Middleware for capturing events for analytics and LLM training.
    
    This middleware logs all events to the analytics service for later
    analysis and dataset generation for LLM training. It uses the new
    comprehensive analytics service if available, falling back to legacy.
    
    Args:
        event: The event being processed
        next_middleware: The next middleware in the chain
        
    Returns:
        The processed event
    """
    try:
        # Try to use the new comprehensive analytics service first
        if ANALYTICS_SERVICE_AVAILABLE:
            analytics = get_analytics_service()
            
            # Convert event to dictionary for the new service
            if hasattr(event, 'dict'):
                event_dict = event.dict()
            elif hasattr(event, 'to_dict'):
                event_dict = event.to_dict()
            else:
                event_dict = {
                    'event_type': getattr(event, 'event_type', event.__class__.__name__),
                    'timestamp': getattr(event, 'timestamp', datetime.utcnow().isoformat())
                }
                # Add all public attributes
                for attr in dir(event):
                    if not attr.startswith('_') and not callable(getattr(event, attr)):
                        try:
                            event_dict[attr] = getattr(event, attr)
                        except Exception:
                            # Skip attributes that can't be serialized
                            pass
            
            # Log using the new service
            entity_id = event_dict.get('entity_id', event_dict.get('id', 'unknown'))
            event_type = event_dict.get('event_type', event.__class__.__name__)
            metadata = {k: v for k, v in event_dict.items() if k not in ['entity_id', 'event_type']}
            
            await analytics.log_event_async(event_type, entity_id, metadata)
        
        else:
            # Fall back to legacy analytics service
            analytics = AnalyticsService.get_instance()
            
            # Convert event to dictionary
            if hasattr(event, 'dict'):
                event_data = event.dict()
            else:
                event_data = {
                    'event_type': getattr(event, 'event_type', event.__class__.__name__),
                    'timestamp': getattr(event, 'timestamp', datetime.utcnow().isoformat())
                }
                # Add all public attributes
                for attr in dir(event):
                    if not attr.startswith('_') and not callable(getattr(event, attr)):
                        try:
                            event_data[attr] = getattr(event, attr)
                        except Exception:
                            # Skip attributes that can't be serialized
                            pass
            
            # Log the event asynchronously
            asyncio.create_task(analytics.log_event_async(event_data))
            
        # Continue middleware chain
        return await next_middleware(event)
        
    except Exception as e:
        logger.error(f"Error in analytics middleware: {e}")
        # Continue middleware chain even if analytics fails
        return await next_middleware(event)

# For backward compatibility
AnalyticsMiddleware = analytics_middleware 