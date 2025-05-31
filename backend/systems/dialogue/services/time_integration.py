"""
Time System integration for the dialogue system.

This module provides functionality for connecting dialogue with the Calendar and Time systems,
allowing dialogue to reference and be influenced by time-based factors like seasons,
festivals, recurring events, and time progression.
"""

from typing import Dict, Any, List, Optional, Set
import logging
from datetime import datetime, timedelta

# Import time system components
from backend.systems.calendar.calendar_manager import CalendarManager
from backend.systems.calendar.time_manager import TimeManager

# Configure logger
logger = logging.getLogger(__name__)

class DialogueTimeIntegration:
    """
    Integration between dialogue and time/calendar systems.
    
    Allows dialogue to reference time-related information, upcoming events,
    seasons, festivals, and time progression.
    """
    
    def __init__(self, calendar_manager=None, time_manager=None):
        """
        Initialize the dialogue time integration.
        
        Args:
            calendar_manager: Optional calendar manager instance
            time_manager: Optional time manager instance
        """
        self.calendar_manager = calendar_manager or CalendarManager.get_instance()
        self.time_manager = time_manager or TimeManager.get_instance()
    
    def add_time_context_to_dialogue(
        self,
        context: Dict[str, Any],
        location_id: Optional[str] = None,
        include_events: bool = True,
        events_lookahead_days: int = 7,
        include_season: bool = True
    ) -> Dict[str, Any]:
        """
        Add time-related information to dialogue context.
        
        Args:
            context: The existing dialogue context
            location_id: Optional location ID for localized time/events
            include_events: Whether to include upcoming events
            events_lookahead_days: How many days ahead to look for events
            include_season: Whether to include seasonal information
            
        Returns:
            Updated context with time-based information added
        """
        # Create a copy of the context
        updated_context = dict(context)
        
        # Create time context if it doesn't exist
        if "time" not in updated_context:
            updated_context["time"] = {}
            
        # Add current time information
        current_time = self._get_current_time_info()
        updated_context["time"].update(current_time)
        
        # Add season information if requested
        if include_season:
            season_info = self._get_season_info()
            updated_context["time"]["season"] = season_info
        
        # Add upcoming events if requested
        if include_events:
            events = self._get_upcoming_events(
                location_id=location_id,
                days_ahead=events_lookahead_days
            )
            
            if events:
                updated_context["time"]["upcoming_events"] = events
                
        return updated_context
    
    def get_time_references_for_dialogue(
        self,
        reference_type: str,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get time-based references for use in dialogue.
        
        Args:
            reference_type: Type of time reference to get (e.g., 'season', 'festival', 'day_period')
            location_id: Optional location ID for localized time references
            
        Returns:
            Dictionary of time references
        """
        references = {}
        
        try:
            if reference_type == "season":
                references = self._get_season_info()
            elif reference_type == "festival":
                references = self._get_current_festival_info(location_id)
            elif reference_type == "day_period":
                references = self._get_day_period_info()
            elif reference_type == "weather":
                references = self._get_weather_info(location_id)
            else:
                logger.warning(f"Unknown time reference type: {reference_type}")
            
            return references
            
        except Exception as e:
            logger.error(f"Error getting time references of type '{reference_type}': {e}")
            return {}
    
    def get_event_dialogue_context(
        self,
        event_id: str,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get dialogue context for a specific calendar event.
        
        Args:
            event_id: ID of the calendar event
            location_id: Optional location ID for localized event
            
        Returns:
            Event context for dialogue
        """
        try:
            # Get the event from calendar
            event = self.calendar_manager.get_event(
                event_id=event_id,
                location_id=location_id
            )
            
            if not event:
                logger.warning(f"Event not found: {event_id}")
                return {}
                
            # Format for dialogue
            event_context = {
                "id": event.get("id"),
                "name": event.get("name"),
                "description": event.get("description"),
                "start_time": event.get("start_time"),
                "end_time": event.get("end_time"),
                "location": event.get("location"),
                "recurring": event.get("recurring", False),
                "importance": event.get("importance", "normal"),
                "tags": event.get("tags", []),
                "participants": event.get("participants", [])
            }
            
            return event_context
            
        except Exception as e:
            logger.error(f"Error getting event dialogue context for '{event_id}': {e}")
            return {}
    
    def get_time_sensitive_dialogue_options(
        self,
        character_id: str,
        location_id: Optional[str] = None,
        dialogue_type: str = "greeting"
    ) -> List[Dict[str, Any]]:
        """
        Get time-appropriate dialogue options based on current world time.
        
        Args:
            character_id: ID of the character for dialogue
            location_id: Optional location ID
            dialogue_type: Type of dialogue to get options for
            
        Returns:
            List of time-sensitive dialogue options
        """
        try:
            # Get current time info
            time_info = self._get_current_time_info()
            
            # Time-appropriate dialogue options would depend on:
            # - Time of day (morning, afternoon, evening, night)
            # - Current season
            # - Current weather
            # - Ongoing or upcoming festivals/events
            
            # This is a simplified implementation
            # In a real system, you'd pull from a dialogue database with tags
            # for time appropriateness
            
            time_of_day = time_info.get("time_of_day", "")
            
            options = []
            
            # Sample time-sensitive greetings
            if dialogue_type == "greeting":
                if time_of_day == "morning":
                    options.append({
                        "text": f"Good morning! It's a fresh {time_info.get('day_name', 'day')}.",
                        "time_relevance": "morning"
                    })
                elif time_of_day == "afternoon":
                    options.append({
                        "text": f"Good afternoon on this {time_info.get('day_name', 'day')}.",
                        "time_relevance": "afternoon"
                    })
                elif time_of_day == "evening":
                    options.append({
                        "text": f"Good evening. The day is winding down.",
                        "time_relevance": "evening"
                    })
                elif time_of_day == "night":
                    options.append({
                        "text": f"You're up late tonight.",
                        "time_relevance": "night"
                    })
            
            # Add season-specific options
            season = time_info.get("season", {}).get("name", "")
            if season:
                options.append({
                    "text": f"How are you finding this {season} weather?",
                    "time_relevance": f"season_{season}"
                })
            
            return options
            
        except Exception as e:
            logger.error(f"Error getting time-sensitive dialogue options: {e}")
            return []
    
    def _get_current_time_info(self) -> Dict[str, Any]:
        """
        Get information about the current world time.
        
        Returns:
            Dictionary with current time information
        """
        try:
            current_time = self.time_manager.get_current_time()
            
            # Format for dialogue context
            time_info = {
                "current_date": current_time.get("date"),
                "day_number": current_time.get("day_number"),
                "day_name": current_time.get("day_name"),
                "month_number": current_time.get("month_number"),
                "month_name": current_time.get("month_name"),
                "year": current_time.get("year"),
                "hour": current_time.get("hour"),
                "minute": current_time.get("minute"),
                "time_of_day": self._get_time_of_day(current_time.get("hour", 0)),
                "is_day": self._is_daytime(current_time.get("hour", 0))
            }
            
            return time_info
            
        except Exception as e:
            logger.error(f"Error getting current time info: {e}")
            # Return minimal fallback information
            return {
                "current_date": "Unknown",
                "time_of_day": "unknown",
                "is_day": True
            }
    
    def _get_season_info(self) -> Dict[str, Any]:
        """
        Get information about the current season.
        
        Returns:
            Dictionary with current season information
        """
        try:
            current_time = self.time_manager.get_current_time()
            season = self.calendar_manager.get_current_season(current_time)
            
            # Format for dialogue context
            season_info = {
                "name": season.get("name"),
                "description": season.get("description"),
                "progress": season.get("progress", 0.0),  # 0.0 to 1.0 through season
                "weather_tendencies": season.get("weather_tendencies", []),
                "typical_activities": season.get("typical_activities", []),
                "seasonal_foods": season.get("seasonal_foods", [])
            }
            
            return season_info
            
        except Exception as e:
            logger.error(f"Error getting season info: {e}")
            return {"name": "unknown", "description": "The current season"}
    
    def _get_upcoming_events(
        self,
        location_id: Optional[str] = None,
        days_ahead: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get upcoming events for dialogue context.
        
        Args:
            location_id: Optional location ID for localized events
            days_ahead: How many days ahead to look for events
            
        Returns:
            List of upcoming events
        """
        try:
            # Get current time
            current_time = self.time_manager.get_current_time()
            
            # Calculate end date for events query
            end_date = self.time_manager.add_days(
                time_dict=current_time,
                days=days_ahead
            )
            
            # Get events
            events = self.calendar_manager.get_events_in_range(
                start_time=current_time,
                end_time=end_date,
                location_id=location_id
            )
            
            # Format for dialogue context
            formatted_events = []
            for event in events:
                formatted_event = {
                    "id": event.get("id"),
                    "name": event.get("name"),
                    "description": event.get("description"),
                    "start_time": event.get("start_time"),
                    "location": event.get("location"),
                    "importance": event.get("importance", "normal")
                }
                
                # Calculate days until event
                days_until = self.time_manager.get_days_between(
                    time1=current_time,
                    time2=event.get("start_time")
                )
                
                formatted_event["days_until"] = days_until
                formatted_events.append(formatted_event)
            
            # Sort by days until
            formatted_events.sort(key=lambda e: e.get("days_until", 0))
            
            return formatted_events
            
        except Exception as e:
            logger.error(f"Error getting upcoming events: {e}")
            return []
    
    def _get_current_festival_info(
        self,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get information about currently ongoing festivals.
        
        Args:
            location_id: Optional location ID for localized festivals
            
        Returns:
            Dictionary with current festival information
        """
        try:
            # Get current time
            current_time = self.time_manager.get_current_time()
            
            # Get events happening now with festival tag
            events = self.calendar_manager.get_current_events(
                current_time=current_time,
                location_id=location_id,
                tags=["festival"]
            )
            
            if not events:
                return {}
            
            # Use the most important festival if multiple
            festival = events[0]
            for event in events:
                if event.get("importance", 0) > festival.get("importance", 0):
                    festival = event
            
            # Format for dialogue
            festival_info = {
                "id": festival.get("id"),
                "name": festival.get("name"),
                "description": festival.get("description"),
                "end_time": festival.get("end_time"),
                "location": festival.get("location"),
                "activities": festival.get("activities", []),
                "significance": festival.get("significance", "")
            }
            
            return festival_info
            
        except Exception as e:
            logger.error(f"Error getting current festival info: {e}")
            return {}
    
    def _get_day_period_info(self) -> Dict[str, Any]:
        """
        Get information about the current period of the day.
        
        Returns:
            Dictionary with day period information
        """
        try:
            # Get current time
            current_time = self.time_manager.get_current_time()
            hour = current_time.get("hour", 0)
            
            # Determine time of day
            time_of_day = self._get_time_of_day(hour)
            
            # Get lighting conditions
            lighting = "bright" if 10 <= hour <= 14 else (
                "dim" if 5 <= hour < 7 or 18 <= hour < 20 else (
                    "normal" if 7 <= hour < 18 else "dark"
                )
            )
            
            # Format for dialogue
            day_period = {
                "name": time_of_day,
                "description": f"It is {time_of_day}time",
                "lighting": lighting,
                "is_day": self._is_daytime(hour),
                "typical_activities": self._get_typical_activities_for_time(time_of_day)
            }
            
            return day_period
            
        except Exception as e:
            logger.error(f"Error getting day period info: {e}")
            return {"name": "unknown", "is_day": True}
    
    def _get_weather_info(
        self,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get current weather information for the location.
        
        Args:
            location_id: Optional location ID for localized weather
            
        Returns:
            Dictionary with weather information
        """
        try:
            # In a real implementation, this would connect to a weather system
            # For now, we'll return placeholder data
            weather = {
                "condition": "clear",
                "temperature": "mild",
                "precipitation": "none",
                "wind": "light",
                "affects_visibility": False,
                "affects_travel": False,
                "description": "The weather is pleasant"
            }
            
            return weather
            
        except Exception as e:
            logger.error(f"Error getting weather info: {e}")
            return {"condition": "unknown"}
    
    def _get_time_of_day(self, hour: int) -> str:
        """
        Determine the time of day based on hour.
        
        Args:
            hour: Hour of the day (0-23)
            
        Returns:
            String representing time of day
        """
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def _is_daytime(self, hour: int) -> bool:
        """
        Determine if it's daytime based on hour.
        
        Args:
            hour: Hour of the day (0-23)
            
        Returns:
            True if daytime, False otherwise
        """
        return 6 <= hour <= 19
    
    def _get_typical_activities_for_time(self, time_of_day: str) -> List[str]:
        """
        Get typical activities for a given time of day.
        
        Args:
            time_of_day: String representing time of day
            
        Returns:
            List of typical activities
        """
        activities = {
            "morning": ["breakfast", "commuting", "opening shops", "morning chores"],
            "afternoon": ["lunch", "working", "shopping", "traveling"],
            "evening": ["dinner", "returning home", "socializing", "entertainment"],
            "night": ["sleeping", "guarding", "night work", "stargazing"]
        }
        
        return activities.get(time_of_day, []) 