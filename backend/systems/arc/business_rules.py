"""
Arc System Business Rules

Comprehensive business rules and domain validation for Arc system.
Implements robust validation and progression logic as specified in Development Bible.
Now loads rules from JSON configuration for runtime flexibility.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from backend.systems.arc.models.arc import ArcType, ArcStatus, ArcPriority
from backend.systems.arc.models.arc_step import ArcStepStatus, ArcStepType

# Import JSON configuration utilities
try:
    from backend.systems.arc.utils import (
        load_business_rules, 
        get_arc_type_rules,
        get_system_limits,
        load_system_config
    )
    _CONFIG_AVAILABLE = True
except (ImportError, FileNotFoundError):
    _CONFIG_AVAILABLE = False
    # Fallback to hardcoded rules if JSON not available
    print("Warning: Arc system JSON configuration not found, using hardcoded fallback rules")

def _get_business_rules() -> Dict[str, Any]:
    """Get business rules from JSON config or fallback to hardcoded."""
    if _CONFIG_AVAILABLE:
        try:
            return load_business_rules()
        except FileNotFoundError:
            pass
    
    # Fallback hardcoded rules (original implementation)
    return {
        "arc_type_rules": {
            "GLOBAL": {"min_duration_hours": 20, "min_factions": 2},
            "CHARACTER": {"max_steps": 10},
            "REGIONAL": {"max_difficulty": 8},
            "NPC": {"max_steps": 6},
            "FACTION": {"min_factions": 2},
            "QUEST": {"max_objectives": 5}
        },
        "narrative_quality_rules": {
            "min_title_length": 5,
            "max_title_length": 100,
            "prohibited_content": ["placeholder", "test", "TODO", "FIXME"]
        },
        "system_limits": {
            "max_relationships_per_type": 10
        }
    }

def validate_arc_business_rules(arc_data: Dict[str, Any]) -> List[str]:
    """
    Validate comprehensive business rules for arc creation and updates.
    Now loads rules from JSON configuration.
    
    Args:
        arc_data: Arc data to validate
        
    Returns:
        List of business rule violations
    """
    violations = []
    rules = _get_business_rules()
    
    # Arc type specific rules
    arc_type = arc_data.get("arc_type")
    if isinstance(arc_type, str):
        try:
            arc_type = ArcType(arc_type)
        except ValueError:
            return violations  # Invalid type, will be caught by data validation
    
    if isinstance(arc_type, ArcType):
        violations.extend(_validate_arc_type_rules(arc_type, arc_data, rules))
    
    # Status progression rules
    violations.extend(_validate_status_progression_rules(arc_data, rules))
    
    # Temporal validation rules
    violations.extend(_validate_temporal_business_rules(arc_data, rules))
    
    # Difficulty and complexity rules
    violations.extend(_validate_difficulty_complexity_rules(arc_data, rules))
    
    # Narrative quality rules
    violations.extend(_validate_narrative_quality_rules(arc_data, rules))
    
    # Cross-system consistency rules
    violations.extend(_validate_cross_system_consistency(arc_data, rules))
    
    return violations

def _validate_arc_type_rules(arc_type: ArcType, arc_data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
    """Validate business rules specific to arc types using JSON configuration."""
    violations = []
    type_rules = rules.get("arc_type_rules", {}).get(arc_type.value, {})
    
    # Global arcs validation
    if arc_type == ArcType.GLOBAL:
        # Check minimum duration
        min_duration = type_rules.get("min_duration_hours", 20)
        estimated_duration = arc_data.get("estimated_duration_hours", 0)
        if estimated_duration > 0 and estimated_duration < min_duration:
            violations.append(f"Global arcs should have at least {min_duration} hours estimated duration")
        
        # Check minimum factions
        min_factions = type_rules.get("min_factions", 2)
        faction_ids = arc_data.get("faction_ids", [])
        if len(faction_ids) < min_factions:
            violations.append(f"Global arcs should involve at least {min_factions} factions")
        
        # Check priority
        priority = arc_data.get("priority", ArcPriority.MEDIUM)
        if isinstance(priority, str):
            try:
                priority = ArcPriority(priority)
            except ValueError:
                pass
        min_priority = type_rules.get("min_priority", "MEDIUM")
        if priority == ArcPriority.LOW and min_priority != "LOW":
            violations.append("Global arcs should not have low priority")
    
    # Character arcs validation
    elif arc_type == ArcType.CHARACTER:
        if not arc_data.get("character_id"):
            violations.append("Character arcs must have a character_id")
        
        max_steps = type_rules.get("max_steps", 10)
        total_steps = arc_data.get("total_steps", 0)
        if total_steps > max_steps:
            violations.append(f"Character arcs should not exceed {max_steps} steps for personal focus")
        
        # Check for personal themes
        themes = arc_data.get("themes", [])
        suggested_themes = type_rules.get("suggested_themes", [])
        if themes and suggested_themes:
            if not any(theme in " ".join(themes).lower() for theme in suggested_themes):
                violations.append("Character arcs should include personal development themes")
    
    # Regional arcs validation  
    elif arc_type == ArcType.REGIONAL:
        required_fields = type_rules.get("required_fields", [])
        if "region_id" in required_fields and not arc_data.get("region_id"):
            violations.append("Regional arcs must have a region_id")
        
        max_difficulty = type_rules.get("max_difficulty", 8)
        difficulty = arc_data.get("difficulty_level", 5)
        if difficulty > max_difficulty:
            violations.append(f"Regional arcs should not exceed difficulty {max_difficulty}")
    
    # NPC arcs validation
    elif arc_type == ArcType.NPC:
        required_fields = type_rules.get("required_fields", [])
        if "npc_id" in required_fields and not arc_data.get("npc_id"):
            violations.append("NPC arcs must have an npc_id")
        
        max_steps = type_rules.get("max_steps", 6)
        total_steps = arc_data.get("total_steps", 0)
        if total_steps > max_steps:
            violations.append(f"NPC arcs should not exceed {max_steps} steps to maintain supporting role")
    
    # Faction arcs validation
    elif arc_type == ArcType.FACTION:
        faction_ids = arc_data.get("faction_ids", [])
        if not faction_ids:
            violations.append("Faction arcs must have at least one faction_id")
        
        min_factions = type_rules.get("min_factions", 2)
        if len(faction_ids) < min_factions:
            violations.append(f"Faction arcs should involve at least {min_factions} factions for meaningful conflict")
        
        # Check for political themes
        themes = arc_data.get("themes", [])
        required_themes = type_rules.get("required_themes", [])
        if themes and required_themes:
            if not any(theme in " ".join(themes).lower() for theme in required_themes):
                violations.append("Faction arcs should include political or conflict themes")
    
    # Quest arcs validation
    elif arc_type == ArcType.QUEST:
        objectives = arc_data.get("objectives", [])
        required_fields = type_rules.get("required_fields", [])
        if "objectives" in required_fields and not objectives:
            violations.append("Quest arcs must have clear objectives")
        
        max_objectives = type_rules.get("max_objectives", 5)
        if len(objectives) > max_objectives:
            violations.append(f"Quest arcs should not exceed {max_objectives} objectives for clarity")
    
    return violations

def _validate_status_progression_rules(arc_data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
    """Validate business rules for arc status progression using JSON configuration."""
    violations = []
    status_rules = rules.get("status_progression_rules", {})
    
    status = arc_data.get("status")
    if isinstance(status, str):
        try:
            status = ArcStatus(status)
        except ValueError:
            return violations
    
    if isinstance(status, ArcStatus):
        current_rules = status_rules.get(status.value, {})
        completion_percentage = arc_data.get("progress_percentage", 0)
        completed_steps = arc_data.get("completed_steps", 0)
        total_steps = arc_data.get("total_steps", 0)
        
        # Completed arcs validation
        if status == ArcStatus.COMPLETED:
            if current_rules.get("required_progress_percentage") == 100 and completion_percentage < 100:
                violations.append("Completed arcs must have 100% completion")
            if current_rules.get("required_all_steps_completed") and total_steps > 0 and completed_steps < total_steps:
                violations.append("Completed arcs must have all steps completed")
            required_fields = current_rules.get("required_fields", [])
            if "end_date" in required_fields and not arc_data.get("end_date"):
                violations.append("Completed arcs must have an end_date")
        
        # Active arcs validation
        elif status == ArcStatus.ACTIVE:
            max_progress = current_rules.get("max_progress_percentage", 99)
            if completion_percentage >= 100:
                violations.append("Active arcs cannot have 100% completion")
            required_fields = current_rules.get("required_fields", [])
            if "start_date" in required_fields and not arc_data.get("start_date"):
                violations.append("Active arcs must have a start_date")
            min_progress = current_rules.get("min_progress_if_steps_completed", 1)
            if completed_steps > 0 and completion_percentage == 0:
                violations.append("Active arcs with completed steps should have > 0% completion")
        
        # Pending arcs validation
        elif status == ArcStatus.PENDING:
            max_progress = current_rules.get("max_progress_percentage", 0)
            max_steps = current_rules.get("max_completed_steps", 0)
            if completion_percentage > max_progress:
                violations.append(f"Pending arcs should not have progress > {max_progress}%")
            if completed_steps > max_steps:
                violations.append("Pending arcs should not have completed steps")
            prohibited_fields = current_rules.get("prohibited_fields", [])
            if "start_date" in prohibited_fields and arc_data.get("start_date"):
                violations.append("Pending arcs should not have a start_date")
        
        # Paused arcs validation
        elif status == ArcStatus.PAUSED:
            required_fields = current_rules.get("required_fields", [])
            if "start_date" in required_fields and not arc_data.get("start_date"):
                violations.append("Paused arcs must have been started (start_date required)")
            max_progress = current_rules.get("max_progress_percentage", 99)
            if completion_percentage >= 100:
                violations.append("Paused arcs cannot be 100% complete")
    
    return violations

def _validate_temporal_business_rules(arc_data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
    """Validate business rules related to time and duration using JSON configuration."""
    violations = []
    temporal_rules = rules.get("temporal_rules", {})
    
    start_date = arc_data.get("start_date")
    end_date = arc_data.get("end_date")
    estimated_duration = arc_data.get("estimated_duration_hours")
    actual_duration = arc_data.get("actual_duration_hours")
    
    # Date consistency rules
    if start_date and end_date:
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        if temporal_rules.get("date_consistency", {}).get("end_date_after_start_date", True):
            if end_date <= start_date:
                violations.append("Arc end_date must be after start_date")
    
    # Future date validation
    if start_date and temporal_rules.get("date_consistency", {}).get("start_date_not_future", True):
        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        if start_date > datetime.utcnow():
            violations.append("Arc start_date cannot be in the future")
    
    # Duration validation
    duration_rules = temporal_rules.get("duration_validation", {})
    if estimated_duration is not None:
        min_duration = duration_rules.get("min_estimated_duration_hours", 0.5)
        max_duration = duration_rules.get("max_estimated_duration_hours", 200)
        if estimated_duration < min_duration:
            violations.append(f"Estimated duration must be at least {min_duration} hours")
        if estimated_duration > max_duration:
            violations.append(f"Estimated duration should not exceed {max_duration} hours")
    
    # Actual vs estimated duration variance
    if estimated_duration and actual_duration:
        max_ratio = duration_rules.get("max_actual_vs_estimated_ratio", 3.0)
        if actual_duration > estimated_duration * max_ratio:
            violations.append(f"Actual duration significantly exceeds estimated (>{max_ratio}x)")
    
    return violations

def _validate_difficulty_complexity_rules(arc_data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
    """Validate business rules for difficulty and complexity using JSON configuration."""
    violations = []
    difficulty_rules = rules.get("difficulty_rules", {})
    
    difficulty = arc_data.get("difficulty_level", 5)
    arc_type = arc_data.get("arc_type")
    total_steps = arc_data.get("total_steps", 0)
    estimated_duration = arc_data.get("estimated_duration_hours", 0)
    
    # Global difficulty range
    global_range = difficulty_rules.get("global_range", [1, 10])
    if difficulty < global_range[0] or difficulty > global_range[1]:
        violations.append(f"Difficulty level must be between {global_range[0]} and {global_range[1]}")
    
    # Type-specific difficulty limits
    if arc_type:
        type_limits = difficulty_rules.get("type_specific_limits", {})
        if arc_type in type_limits:
            type_range = type_limits[arc_type]
            if difficulty < type_range[0] or difficulty > type_range[1]:
                violations.append(f"{arc_type} arcs should have difficulty between {type_range[0]} and {type_range[1]}")
    
    # Progression validation
    progression_rules = difficulty_rules.get("progression_validation", {})
    if total_steps > 0:
        expected_steps_ratio = progression_rules.get("difficulty_vs_steps_ratio", 1.5)
        expected_steps = difficulty * expected_steps_ratio
        if total_steps > expected_steps * 2:
            violations.append(f"Arc has too many steps ({total_steps}) for difficulty level {difficulty}")
    
    if estimated_duration > 0:
        expected_duration_ratio = progression_rules.get("difficulty_vs_duration_ratio", 0.8)
        expected_duration = difficulty * expected_duration_ratio * 10  # Base multiplier
        if estimated_duration > expected_duration * 3:
            violations.append(f"Arc duration ({estimated_duration}h) seems excessive for difficulty level {difficulty}")
    
    return violations

def _validate_narrative_quality_rules(arc_data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
    """Validate business rules for narrative quality and coherence using JSON configuration."""
    violations = []
    narrative_rules = rules.get("narrative_quality_rules", {})
    
    title = arc_data.get("title", "")
    description = arc_data.get("description", "")
    objectives = arc_data.get("objectives", [])
    themes = arc_data.get("themes", [])
    narrative_summary = arc_data.get("narrative_summary", "")
    
    # Title quality rules
    if title:
        min_length = narrative_rules.get("min_title_length", 5)
        max_length = narrative_rules.get("max_title_length", 100)
        prohibited_content = narrative_rules.get("prohibited_content", [])
        
        if len(title.strip()) < min_length:
            violations.append(f"Arc title should be at least {min_length} characters")
        elif len(title) > max_length:
            violations.append(f"Arc title should not exceed {max_length} characters for clarity")
        elif any(prohibited in title.lower() for prohibited in prohibited_content):
            violations.append("Arc title should be descriptive, not placeholder text")
    
    # Description quality rules
    if description:
        min_desc_length = narrative_rules.get("min_description_length", 20)
        max_desc_length = narrative_rules.get("max_description_length", 2000)
        prohibited_content = narrative_rules.get("prohibited_content", [])
        
        if len(description.strip()) < min_desc_length:
            violations.append(f"Arc description should be at least {min_desc_length} characters")
        elif len(description) > max_desc_length:
            violations.append(f"Arc description should not exceed {max_desc_length} characters")
        elif any(prohibited in description.lower() for prohibited in prohibited_content):
            violations.append("Arc description contains placeholder content")
    
    # Objectives validation
    min_objectives = narrative_rules.get("min_objectives", 1)
    max_objectives = narrative_rules.get("max_objectives", 10)
    if len(objectives) < min_objectives:
        violations.append(f"Arc should have at least {min_objectives} objective(s)")
    elif len(objectives) > max_objectives:
        violations.append(f"Arc should not exceed {max_objectives} objectives for clarity")
    
    # Themes validation
    max_themes = narrative_rules.get("max_themes", 8)
    if len(themes) > max_themes:
        violations.append(f"Arc should not exceed {max_themes} themes for focus")
    
    # Narrative summary quality
    content_quality = narrative_rules.get("required_content_quality", {})
    if narrative_summary:
        min_summary_length = content_quality.get("narrative_summary_min_length", 50)
        if len(narrative_summary.strip()) < min_summary_length:
            violations.append(f"Narrative summary should be at least {min_summary_length} characters")
    
    return violations

def _validate_cross_system_consistency(arc_data: Dict[str, Any], rules: Dict[str, Any]) -> List[str]:
    """Validate business rules for consistency with other game systems using JSON configuration."""
    violations = []
    
    # Faction system consistency
    faction_ids = arc_data.get("faction_ids", [])
    if faction_ids:
        # Validate faction ID format (simplified check)
        for faction_id in faction_ids:
            if not isinstance(faction_id, str) or len(faction_id.strip()) == 0:
                violations.append("All faction IDs must be non-empty strings")
    
    # Character system consistency
    character_id = arc_data.get("character_id")
    if character_id is not None:
        if not isinstance(character_id, str) or len(character_id.strip()) == 0:
            violations.append("Character ID must be a non-empty string")
    
    # Region system consistency
    region_id = arc_data.get("region_id")
    if region_id is not None:
        if not isinstance(region_id, str) or len(region_id.strip()) == 0:
            violations.append("Region ID must be a non-empty string")
    
    # NPC system consistency
    npc_id = arc_data.get("npc_id")
    if npc_id is not None:
        if not isinstance(npc_id, str) or len(npc_id.strip()) == 0:
            violations.append("NPC ID must be a non-empty string")
    
    return violations

def validate_narrative_text(text: str) -> List[str]:
    """
    Validate narrative text quality using JSON configuration.
    
    Args:
        text: Narrative text to validate
        
    Returns:
        List of validation errors
    """
    violations = []
    rules = _get_business_rules()
    narrative_rules = rules.get("narrative_quality_rules", {})
    prohibited_content = narrative_rules.get("prohibited_content", [])
    
    if not text or not text.strip():
        violations.append("Narrative text cannot be empty")
        return violations
    
    # Check for placeholder content
    text_lower = text.lower()
    for prohibited in prohibited_content:
        if prohibited in text_lower:
            violations.append(f"Narrative text contains placeholder content: '{prohibited}'")
    
    # Basic quality checks
    if len(text.strip()) < 10:
        violations.append("Narrative text should be more descriptive")
    
    if text.count('.') == 0 and text.count('!') == 0 and text.count('?') == 0:
        violations.append("Narrative text should contain complete sentences")
    
    return violations

def validate_arc_progression_rules(arc_data: Dict[str, Any]) -> List[str]:
    """
    Validate arc progression business rules using JSON configuration.
    
    Args:
        arc_data: Arc data including progression information
        
    Returns:
        List of validation errors
    """
    violations = []
    rules = _get_business_rules()
    
    total_steps = arc_data.get("total_steps", 0)
    completed_steps = arc_data.get("completed_steps", 0)
    progress_percentage = arc_data.get("progress_percentage", 0)
    status = arc_data.get("status", "PENDING")
    
    # Basic progression consistency
    if completed_steps > total_steps:
        violations.append("Completed steps cannot exceed total steps")
    
    if progress_percentage < 0 or progress_percentage > 100:
        violations.append("Progress percentage must be between 0 and 100")
    
    # Progression calculation consistency
    if total_steps > 0:
        expected_progress = (completed_steps / total_steps) * 100
        if abs(progress_percentage - expected_progress) > 5:  # 5% tolerance
            violations.append("Progress percentage should align with completed steps ratio")
    
    # Status-specific progression rules
    if status == "COMPLETED" and progress_percentage < 100:
        violations.append("Completed arcs must have 100% progress")
    elif status == "PENDING" and (completed_steps > 0 or progress_percentage > 0):
        violations.append("Pending arcs should not have any progress")
    
    return violations

def validate_step_completion_criteria(completion_criteria: Dict[str, Any]) -> List[str]:
    """
    Validate step completion criteria using JSON configuration.
    
    Args:
        completion_criteria: Step completion criteria data
        
    Returns:
        List of validation errors
    """
    violations = []
    
    if not completion_criteria:
        violations.append("Step completion criteria cannot be empty")
        return violations
    
    # Required fields validation
    required_fields = ["type", "description"]
    for field in required_fields:
        if field not in completion_criteria:
            violations.append(f"Step completion criteria must include '{field}'")
    
    # Type-specific validation
    criteria_type = completion_criteria.get("type")
    if criteria_type:
        valid_types = ["manual", "automatic", "condition_based", "time_based", "event_triggered"]
        if criteria_type not in valid_types:
            violations.append(f"Invalid completion criteria type: {criteria_type}")
        
        # Type-specific requirements
        if criteria_type == "condition_based" and "conditions" not in completion_criteria:
            violations.append("Condition-based criteria must specify conditions")
        elif criteria_type == "time_based" and "duration" not in completion_criteria:
            violations.append("Time-based criteria must specify duration")
        elif criteria_type == "event_triggered" and "event_type" not in completion_criteria:
            violations.append("Event-triggered criteria must specify event_type")
    
    return violations

def calculate_arc_complexity_score(arc_data: Dict[str, Any]) -> Tuple[int, List[str]]:
    """
    Calculate complexity score for an arc using JSON configuration.
    
    Args:
        arc_data: Arc data to analyze
        
    Returns:
        Tuple of (complexity_score, complexity_factors)
    """
    score = 0
    factors = []
    rules = _get_business_rules()
    
    # Base complexity factors
    difficulty = arc_data.get("difficulty_level", 5)
    score += difficulty
    factors.append(f"Difficulty: +{difficulty}")
    
    total_steps = arc_data.get("total_steps", 0)
    if total_steps > 5:
        step_score = min(total_steps - 5, 10)  # Cap at 10
        score += step_score
        factors.append(f"Steps: +{step_score} ({total_steps} steps)")
    
    # Duration complexity
    estimated_duration = arc_data.get("estimated_duration_hours", 0)
    if estimated_duration > 20:
        duration_score = min(int(estimated_duration / 10), 15)  # Cap at 15
        score += duration_score
        factors.append(f"Duration: +{duration_score} ({estimated_duration}h)")
    
    # Faction involvement complexity
    faction_ids = arc_data.get("faction_ids", [])
    if len(faction_ids) > 2:
        faction_score = min(len(faction_ids) - 2, 8)  # Cap at 8
        score += faction_score
        factors.append(f"Factions: +{faction_score} ({len(faction_ids)} factions)")
    
    # Arc type complexity
    arc_type = arc_data.get("arc_type", "REGIONAL")
    type_complexity = {
        "CHARACTER": 1,
        "NPC": 2,
        "QUEST": 3,
        "REGIONAL": 4,
        "FACTION": 6,
        "GLOBAL": 8
    }
    type_score = type_complexity.get(arc_type, 3)
    score += type_score
    factors.append(f"Type: +{type_score} ({arc_type})")
    
    # Relationship complexity (if supported)
    relationships = arc_data.get("predecessor_arcs", []) + arc_data.get("successor_arcs", []) + arc_data.get("related_arcs", [])
    if relationships:
        rel_score = min(len(relationships) * 2, 10)  # Cap at 10
        score += rel_score
        factors.append(f"Relationships: +{rel_score} ({len(relationships)} connections)")
    
    return score, factors

def should_arc_be_expanded(arc_data: Dict[str, Any]) -> Tuple[bool, str, int]:
    """
    Determine if an arc should be expanded into subtasks using JSON configuration.
    
    Args:
        arc_data: Arc data to analyze
        
    Returns:
        Tuple of (should_expand, reason, suggested_subtasks)
    """
    complexity_score, factors = calculate_arc_complexity_score(arc_data)
    rules = _get_business_rules()
    
    # Get expansion thresholds from config or use defaults
    expansion_threshold = 15  # Default threshold
    max_expansion_threshold = 25
    
    total_steps = arc_data.get("total_steps", 0)
    
    if complexity_score >= max_expansion_threshold:
        return True, f"High complexity score ({complexity_score})", min(8, max(4, complexity_score // 3))
    elif complexity_score >= expansion_threshold:
        return True, f"Moderate complexity score ({complexity_score})", min(6, max(3, complexity_score // 4))
    elif total_steps > 8:
        return True, f"Many steps ({total_steps})", min(total_steps, 8)
    elif arc_data.get("arc_type") == "GLOBAL":
        return True, "Global arcs should always be expanded", 6
    else:
        return False, f"Low complexity score ({complexity_score})", 0 