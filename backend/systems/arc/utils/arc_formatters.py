"""
Arc System Formatters

Utilities for formatting Arc system data for display and output.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.systems.arc.models.arc import Arc, ArcType, ArcStatus, ArcPriority
from backend.systems.arc.models.arc_step import ArcStep, ArcStepType, ArcStepStatus
from backend.systems.arc.models.arc_progression import ArcProgression
from backend.systems.arc.models.arc_completion_record import ArcCompletionRecord

def format_arc_for_display(arc: Arc, include_steps: bool = False) -> Dict[str, Any]:
    """
    Format an arc for display with user-friendly formatting.
    
    Args:
        arc: Arc instance to format
        include_steps: Whether to include step details
        
    Returns:
        Formatted arc data
    """
    formatted = {
        "id": str(arc.id),
        "title": arc.title,
        "description": arc.description,
        "type": arc.arc_type.value.replace("_", " ").title(),
        "status": arc.status.value.replace("_", " ").title(),
        "priority": arc.priority.value.title(),
        "progress": f"{arc.completion_percentage:.1%}",
        "current_step": f"{arc.current_step}/{arc.total_steps}",
        "created": _format_datetime(arc.created_at),
        "updated": _format_datetime(arc.updated_at),
        "last_activity": _format_datetime(arc.last_activity) if arc.last_activity else "Never"
    }
    
    # Add context-specific fields
    if arc.region_id:
        formatted["region"] = arc.region_id
    if arc.character_id:
        formatted["character"] = arc.character_id
    if arc.npc_id:
        formatted["npc"] = arc.npc_id
    if arc.faction_ids:
        formatted["factions"] = ", ".join(arc.faction_ids)
    
    # Add system hooks
    if arc.system_hooks:
        formatted["integrations"] = ", ".join(arc.system_hooks)
    
    return formatted

def format_step_for_display(step: ArcStep) -> Dict[str, Any]:
    """
    Format an arc step for display.
    
    Args:
        step: ArcStep instance to format
        
    Returns:
        Formatted step data
    """
    formatted = {
        "id": str(step.id),
        "index": step.step_index,
        "title": step.title,
        "description": step.description,
        "type": step.step_type.value.replace("_", " ").title(),
        "status": step.status.value.replace("_", " ").title(),
        "attempts": step.attempts,
        "quest_chance": f"{step.quest_probability:.0%}" if step.quest_probability > 0 else "None",
        "created": _format_datetime(step.created_at),
        "completed": _format_datetime(step.completed_at) if step.completed_at else "Not completed"
    }
    
    # Add tags if present
    if step.tags:
        formatted["tags"] = ", ".join(step.tags)
    
    return formatted

def format_progression_summary(progression: ArcProgression) -> Dict[str, Any]:
    """
    Format arc progression for summary display.
    
    Args:
        progression: ArcProgression instance to format
        
    Returns:
        Formatted progression summary
    """
    formatted = {
        "id": str(progression.id),
        "arc_id": str(progression.arc_id),
        "current_step": progression.current_step_index,
        "progress": f"{progression.completion_percentage:.1%}",
        "active": "Yes" if progression.is_active else "No",
        "method": progression.progression_method.value.replace("_", " ").title(),
        "events": progression.total_events,
        "duration": _format_duration(progression.total_duration),
        "avg_step_time": _format_duration(progression.average_step_duration),
        "started": _format_datetime(progression.started_at) if progression.started_at else "Not started",
        "completed": _format_datetime(progression.completed_at) if progression.completed_at else "In progress"
    }
    
    # Add step statistics
    if progression.completed_steps:
        formatted["completed_steps"] = f"{len(progression.completed_steps)} steps"
    if progression.failed_steps:
        formatted["failed_steps"] = f"{len(progression.failed_steps)} steps"
    if progression.skipped_steps:
        formatted["skipped_steps"] = f"{len(progression.skipped_steps)} steps"
    
    return formatted

def format_completion_record(record: ArcCompletionRecord) -> Dict[str, Any]:
    """
    Format arc completion record for display.
    
    Args:
        record: ArcCompletionRecord instance to format
        
    Returns:
        Formatted completion record
    """
    formatted = {
        "id": str(record.id),
        "arc_id": str(record.arc_id),
        "result": record.result.value.replace("_", " ").title(),
        "completion": f"{record.final_completion_percentage:.1%}",
        "duration": _format_duration(record.total_duration_hours),
        "avg_step_time": _format_duration(record.average_step_duration_hours),
        "completed_at": _format_datetime(record.created_at)
    }
    
    # Add step statistics
    total_steps = record.total_steps_completed + record.total_steps_failed + record.total_steps_skipped
    if total_steps > 0:
        formatted["steps"] = {
            "completed": f"{record.total_steps_completed}/{total_steps}",
            "failed": f"{record.total_steps_failed}/{total_steps}",
            "skipped": f"{record.total_steps_skipped}/{total_steps}"
        }
    
    # Add outcomes summary
    if record.outcomes:
        formatted["outcomes"] = len(record.outcomes)
    if record.rewards_granted:
        formatted["rewards"] = len(record.rewards_granted)
    if record.consequences:
        formatted["consequences"] = len(record.consequences)
    
    return formatted

def format_arc_list_table(arcs: List[Arc]) -> List[Dict[str, str]]:
    """
    Format a list of arcs for table display.
    
    Args:
        arcs: List of Arc instances
        
    Returns:
        List of formatted rows for table display
    """
    rows = []
    
    for arc in arcs:
        row = {
            "ID": str(arc.id)[:8] + "...",  # Shortened ID
            "Title": arc.title[:30] + ("..." if len(arc.title) > 30 else ""),
            "Type": arc.arc_type.value.replace("_", " ").title(),
            "Status": arc.status.value.replace("_", " ").title(),
            "Priority": arc.priority.value.title(),
            "Progress": f"{arc.completion_percentage:.1%}",
            "Steps": f"{arc.current_step}/{arc.total_steps}",
            "Updated": _format_datetime_short(arc.updated_at)
        }
        rows.append(row)
    
    return rows

def format_step_list_table(steps: List[ArcStep]) -> List[Dict[str, str]]:
    """
    Format a list of steps for table display.
    
    Args:
        steps: List of ArcStep instances
        
    Returns:
        List of formatted rows for table display
    """
    rows = []
    
    for step in steps:
        row = {
            "Index": str(step.step_index),
            "Title": step.title[:25] + ("..." if len(step.title) > 25 else ""),
            "Type": step.step_type.value.replace("_", " ").title(),
            "Status": step.status.value.replace("_", " ").title(),
            "Attempts": str(step.attempts),
            "Quest": f"{step.quest_probability:.0%}" if step.quest_probability > 0 else "-",
            "Created": _format_datetime_short(step.created_at)
        }
        rows.append(row)
    
    return rows

def format_analytics_summary(analytics: Dict[str, Any]) -> Dict[str, str]:
    """
    Format analytics data for summary display.
    
    Args:
        analytics: Analytics data dictionary
        
    Returns:
        Formatted analytics summary
    """
    summary = analytics.get("summary", {})
    
    formatted = {
        "Total Arcs": str(summary.get("total_arcs", 0)),
        "Active Progressions": str(summary.get("active_progressions", 0)),
        "Completion Rate": f"{summary.get('completion_rate', 0):.1%}",
        "Avg Duration": _format_duration(summary.get("average_duration", 0)),
        "Analysis Period": analytics.get("timeframe", "Unknown").replace("_", " ").title()
    }
    
    return formatted

def format_status_badge(status: str) -> str:
    """
    Format status as a colored badge for terminal/HTML display.
    
    Args:
        status: Status string
        
    Returns:
        Formatted status badge
    """
    status_colors = {
        "pending": "🟡",
        "active": "🟢", 
        "completed": "✅",
        "failed": "❌",
        "cancelled": "⚫",
        "deferred": "🟠",
        "in_progress": "🔵",
        "review": "🟣"
    }
    
    status_lower = status.lower().replace(" ", "_")
    icon = status_colors.get(status_lower, "⚪")
    
    return f"{icon} {status.replace('_', ' ').title()}"

def format_priority_indicator(priority: str) -> str:
    """
    Format priority with visual indicators.
    
    Args:
        priority: Priority string
        
    Returns:
        Formatted priority with indicators
    """
    priority_indicators = {
        "low": "🔽 Low",
        "medium": "➡️ Medium", 
        "high": "🔺 High",
        "critical": "🚨 Critical"
    }
    
    priority_lower = priority.lower()
    return priority_indicators.get(priority_lower, f"📋 {priority.title()}")

def format_progress_bar(percentage: float, width: int = 20) -> str:
    """
    Format completion percentage as a text progress bar.
    
    Args:
        percentage: Progress percentage (0.0 to 1.0)
        width: Width of progress bar in characters
        
    Returns:
        Text progress bar
    """
    if percentage < 0:
        percentage = 0
    elif percentage > 1:
        percentage = 1
    
    filled = int(percentage * width)
    bar = "█" * filled + "░" * (width - filled)
    
    return f"[{bar}] {percentage:.1%}"

def _format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    if not dt:
        return "Never"
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 7:
        return dt.strftime("%Y-%m-%d")
    elif diff.days > 0:
        return f"{diff.days} days ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hours ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minutes ago"
    else:
        return "Just now"

def _format_datetime_short(dt: datetime) -> str:
    """Format datetime in short format."""
    if not dt:
        return "N/A"
    
    return dt.strftime("%m/%d %H:%M")

def _format_duration(hours: float) -> str:
    """Format duration in hours to human-readable format."""
    if hours < 1:
        minutes = int(hours * 60)
        return f"{minutes}m"
    elif hours < 24:
        return f"{hours:.1f}h"
    else:
        days = int(hours // 24)
        remaining_hours = hours % 24
        if remaining_hours > 0:
            return f"{days}d {remaining_hours:.1f}h"
        else:
            return f"{days}d" 