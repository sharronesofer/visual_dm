from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Union, Dict, Any
from datetime import datetime, timedelta

from backend.systems.time import (
    TimeManager, GameTime, TimeEvent, TimeUnit, 
    Season, Calendar, WorldTime, CalendarEvent, EventType
)

router = APIRouter(prefix="/time", tags=["time"])
time_manager = TimeManager()

@router.get("/current", response_model=GameTime)
async def get_current_time():
    """Get the current game time."""
    return time_manager.get_time()

@router.post("/advance")
async def advance_time(
    amount: int = Query(..., description="Amount of time to advance"),
    unit: TimeUnit = Query(..., description="Time unit to advance by (tick, second, minute, hour, day, month, year)")
):
    """Advance the game time by the specified amount and unit."""
    time_manager.advance_time(amount, unit)
    return {"status": "success", "game_time": time_manager.get_time()}

@router.get("/events", response_model=List[TimeEvent])
async def get_events(
    upcoming_only: bool = Query(False, description="Only show upcoming events")
):
    """Get all scheduled time events or only upcoming ones."""
    events = time_manager.get_events(upcoming_only=upcoming_only)
    return events

@router.post("/events")
async def schedule_event(
    event_type: EventType,
    callback_name: str,
    callback_data: Optional[Dict[str, Any]] = None,
    trigger_time: Optional[datetime] = None,
    time_offset: Optional[timedelta] = None,
    recurrence_interval: Optional[timedelta] = None,
    priority: int = 0
):
    """Schedule a new time event."""
    event_id = time_manager.schedule_event(
        event_type=event_type,
        callback_name=callback_name,
        callback_data=callback_data,
        trigger_time=trigger_time,
        time_offset=time_offset,
        recurrence_interval=recurrence_interval,
        priority=priority
    )
    return {"status": "success", "event_id": event_id, "event": time_manager.get_event(event_id)}

@router.delete("/events/{event_id}")
async def cancel_event(event_id: str):
    """Cancel a scheduled time event."""
    success = time_manager.cancel_event(event_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    return {"status": "success", "message": f"Event {event_id} cancelled"}

@router.get("/calendar", response_model=Calendar)
async def get_calendar():
    """Get the game calendar configuration."""
    return time_manager.get_calendar()

@router.get("/season", response_model=str)
async def get_current_season():
    """Get the current season in the game world."""
    return time_manager.get_current_season().value

@router.get("/weather", response_model=Dict[str, Any])
async def get_current_weather():
    """Get the current weather conditions."""
    return {
        "current_condition": time_manager.get_current_weather(),
        "temperature": time_manager.get_current_temperature(),
        "last_changed": time_manager.get_weather_last_changed().isoformat() if time_manager.get_weather_last_changed() else None
    }

@router.post("/calendar/dates")
async def add_important_date(
    name: str,
    month: int,
    day: int,
    year: Optional[int] = None
):
    """Add an important date to the calendar."""
    time_manager.add_important_date(name, month, day, year)
    return {"status": "success", "message": f"Added important date: {name}"}

@router.delete("/calendar/dates/{name}")
async def remove_important_date(name: str):
    """Remove an important date from the calendar."""
    success = time_manager.remove_important_date(name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Important date '{name}' not found")
    return {"status": "success", "message": f"Removed important date: {name}"}

@router.post("/progression/start")
async def start_time_progression():
    """Start automatic time progression."""
    time_manager.start_time_progression()
    return {"status": "success", "message": "Time progression started"}

@router.post("/progression/stop")
async def stop_time_progression():
    """Stop automatic time progression."""
    time_manager.stop_time_progression()
    return {"status": "success", "message": "Time progression stopped"}

@router.post("/progression/pause")
async def pause_time():
    """Pause time progression."""
    time_manager.pause()
    return {"status": "success", "message": "Time progression paused"}

@router.post("/progression/resume")
async def resume_time():
    """Resume time progression."""
    time_manager.resume()
    return {"status": "success", "message": "Time progression resumed"}

@router.post("/scale")
async def set_time_scale(scale: float = Query(..., description="Time scale factor (1.0 = real-time, 2.0 = 2x speed, etc.)")):
    """Set the time scale for automatic progression."""
    time_manager.set_time_scale(scale)
    return {"status": "success", "message": f"Time scale set to {scale}"}

@router.post("/reset")
async def reset_time():
    """Reset the game time to initial default state (admin use only)."""
    time_manager.reset()
    return {"status": "success", "message": "Time system reset to defaults"}

@router.post("/save")
async def save_time_state():
    """Save the current time system state to persistent storage."""
    time_manager.save_state()
    return {"status": "success", "message": "Time system state saved"} 