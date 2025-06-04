"""
Arc System Validators

Technical validation utilities for Arc system data structures.
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.systems.arc.models.arc import ArcType, ArcStatus, ArcPriority
from backend.systems.arc.models.arc_step import ArcStepType, ArcStepStatus
from backend.systems.arc.models.arc_progression import ProgressionMethod
from backend.systems.arc.models.arc_completion_record import ArcCompletionResult


class ArcValidationError(Exception):
    """Custom exception for Arc validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, code: Optional[str] = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)


def validate_arc_data(arc_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate arc data structure and technical requirements.
    
    Args:
        arc_data: Dictionary containing arc data
        
    Returns:
        Dictionary with validation errors (empty if valid)
    """
    errors = {}
    
    # Required fields
    required_fields = ["title", "description", "arc_type", "starting_point", "preferred_ending"]
    for field in required_fields:
        if field not in arc_data or not arc_data[field]:
            if "required" not in errors:
                errors["required"] = []
            errors["required"].append(f"Field '{field}' is required")
    
    # Title validation
    if "title" in arc_data:
        title = arc_data["title"]
        if not isinstance(title, str):
            if "title" not in errors:
                errors["title"] = []
            errors["title"].append("Title must be a string")
        elif len(title) < 3:
            if "title" not in errors:
                errors["title"] = []
            errors["title"].append("Title must be at least 3 characters long")
        elif len(title) > 255:
            if "title" not in errors:
                errors["title"] = []
            errors["title"].append("Title must be 255 characters or less")
    
    # Description validation
    if "description" in arc_data:
        description = arc_data["description"]
        if not isinstance(description, str):
            if "description" not in errors:
                errors["description"] = []
            errors["description"].append("Description must be a string")
        elif len(description) < 10:
            if "description" not in errors:
                errors["description"] = []
            errors["description"].append("Description must be at least 10 characters long")
    
    # Arc type validation
    if "arc_type" in arc_data:
        arc_type = arc_data["arc_type"]
        if isinstance(arc_type, str):
            try:
                ArcType(arc_type)
            except ValueError:
                if "arc_type" not in errors:
                    errors["arc_type"] = []
                errors["arc_type"].append(f"Invalid arc type: {arc_type}")
        elif not isinstance(arc_type, ArcType):
            if "arc_type" not in errors:
                errors["arc_type"] = []
            errors["arc_type"].append("Arc type must be a valid ArcType enum")
    
    # Status validation (if provided)
    if "status" in arc_data:
        status = arc_data["status"]
        if isinstance(status, str):
            try:
                ArcStatus(status)
            except ValueError:
                if "status" not in errors:
                    errors["status"] = []
                errors["status"].append(f"Invalid arc status: {status}")
        elif not isinstance(status, ArcStatus):
            if "status" not in errors:
                errors["status"] = []
            errors["status"].append("Status must be a valid ArcStatus enum")
    
    # Priority validation (if provided)
    if "priority" in arc_data:
        priority = arc_data["priority"]
        if isinstance(priority, str):
            try:
                ArcPriority(priority)
            except ValueError:
                if "priority" not in errors:
                    errors["priority"] = []
                errors["priority"].append(f"Invalid arc priority: {priority}")
        elif not isinstance(priority, ArcPriority):
            if "priority" not in errors:
                errors["priority"] = []
            errors["priority"].append("Priority must be a valid ArcPriority enum")
    
    # Completion percentage validation
    if "completion_percentage" in arc_data:
        completion = arc_data["completion_percentage"]
        if not isinstance(completion, (int, float)):
            if "completion_percentage" not in errors:
                errors["completion_percentage"] = []
            errors["completion_percentage"].append("Completion percentage must be a number")
        elif completion < 0 or completion > 1:
            if "completion_percentage" not in errors:
                errors["completion_percentage"] = []
            errors["completion_percentage"].append("Completion percentage must be between 0 and 1")
    
    # Total steps validation
    if "total_steps" in arc_data:
        total_steps = arc_data["total_steps"]
        if not isinstance(total_steps, int):
            if "total_steps" not in errors:
                errors["total_steps"] = []
            errors["total_steps"].append("Total steps must be an integer")
        elif total_steps < 0:
            if "total_steps" not in errors:
                errors["total_steps"] = []
            errors["total_steps"].append("Total steps cannot be negative")
    
    # Current step validation
    if "current_step" in arc_data:
        current_step = arc_data["current_step"]
        if not isinstance(current_step, int):
            if "current_step" not in errors:
                errors["current_step"] = []
            errors["current_step"].append("Current step must be an integer")
        elif current_step < 0:
            if "current_step" not in errors:
                errors["current_step"] = []
            errors["current_step"].append("Current step cannot be negative")
    
    # Faction IDs validation
    if "faction_ids" in arc_data:
        faction_ids = arc_data["faction_ids"]
        if not isinstance(faction_ids, list):
            if "faction_ids" not in errors:
                errors["faction_ids"] = []
            errors["faction_ids"].append("Faction IDs must be a list")
        else:
            for i, faction_id in enumerate(faction_ids):
                if not isinstance(faction_id, str):
                    if "faction_ids" not in errors:
                        errors["faction_ids"] = []
                    errors["faction_ids"].append(f"Faction ID at index {i} must be a string")
    
    # System hooks validation
    if "system_hooks" in arc_data:
        system_hooks = arc_data["system_hooks"]
        if not isinstance(system_hooks, list):
            if "system_hooks" not in errors:
                errors["system_hooks"] = []
            errors["system_hooks"].append("System hooks must be a list")
        else:
            valid_hooks = ["quest_system", "faction_system", "diplomacy_system", 
                          "region_system", "population_system", "world_state_system"]
            for i, hook in enumerate(system_hooks):
                if not isinstance(hook, str):
                    if "system_hooks" not in errors:
                        errors["system_hooks"] = []
                    errors["system_hooks"].append(f"System hook at index {i} must be a string")
                elif hook not in valid_hooks:
                    if "system_hooks" not in errors:
                        errors["system_hooks"] = []
                    errors["system_hooks"].append(f"Invalid system hook: {hook}")
    
    return errors


def validate_step_data(step_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate step data structure and technical requirements.
    
    Args:
        step_data: Dictionary containing step data
        
    Returns:
        Dictionary with validation errors (empty if valid)
    """
    errors = {}
    
    # Required fields
    required_fields = ["title", "description", "step_type"]
    for field in required_fields:
        if field not in step_data or not step_data[field]:
            if "required" not in errors:
                errors["required"] = []
            errors["required"].append(f"Field '{field}' is required")
    
    # Title validation
    if "title" in step_data:
        title = step_data["title"]
        if not isinstance(title, str):
            if "title" not in errors:
                errors["title"] = []
            errors["title"].append("Title must be a string")
        elif len(title) < 3:
            if "title" not in errors:
                errors["title"] = []
            errors["title"].append("Title must be at least 3 characters long")
        elif len(title) > 255:
            if "title" not in errors:
                errors["title"] = []
            errors["title"].append("Title must be 255 characters or less")
    
    # Description validation
    if "description" in step_data:
        description = step_data["description"]
        if not isinstance(description, str):
            if "description" not in errors:
                errors["description"] = []
            errors["description"].append("Description must be a string")
        elif len(description) < 10:
            if "description" not in errors:
                errors["description"] = []
            errors["description"].append("Description must be at least 10 characters long")
    
    # Step type validation
    if "step_type" in step_data:
        step_type = step_data["step_type"]
        if isinstance(step_type, str):
            try:
                ArcStepType(step_type)
            except ValueError:
                if "step_type" not in errors:
                    errors["step_type"] = []
                errors["step_type"].append(f"Invalid step type: {step_type}")
        elif not isinstance(step_type, ArcStepType):
            if "step_type" not in errors:
                errors["step_type"] = []
            errors["step_type"].append("Step type must be a valid ArcStepType enum")
    
    # Status validation (if provided)
    if "status" in step_data:
        status = step_data["status"]
        if isinstance(status, str):
            try:
                ArcStepStatus(status)
            except ValueError:
                if "status" not in errors:
                    errors["status"] = []
                errors["status"].append(f"Invalid step status: {status}")
        elif not isinstance(status, ArcStepStatus):
            if "status" not in errors:
                errors["status"] = []
            errors["status"].append("Status must be a valid ArcStepStatus enum")
    
    # Step index validation
    if "step_index" in step_data:
        step_index = step_data["step_index"]
        if not isinstance(step_index, int):
            if "step_index" not in errors:
                errors["step_index"] = []
            errors["step_index"].append("Step index must be an integer")
        elif step_index < 0:
            if "step_index" not in errors:
                errors["step_index"] = []
            errors["step_index"].append("Step index cannot be negative")
    
    # Attempts validation
    if "attempts" in step_data:
        attempts = step_data["attempts"]
        if not isinstance(attempts, int):
            if "attempts" not in errors:
                errors["attempts"] = []
            errors["attempts"].append("Attempts must be an integer")
        elif attempts < 0:
            if "attempts" not in errors:
                errors["attempts"] = []
            errors["attempts"].append("Attempts cannot be negative")
    
    # Quest probability validation
    if "quest_probability" in step_data:
        quest_prob = step_data["quest_probability"]
        if not isinstance(quest_prob, (int, float)):
            if "quest_probability" not in errors:
                errors["quest_probability"] = []
            errors["quest_probability"].append("Quest probability must be a number")
        elif quest_prob < 0 or quest_prob > 1:
            if "quest_probability" not in errors:
                errors["quest_probability"] = []
            errors["quest_probability"].append("Quest probability must be between 0 and 1")
    
    # Tags validation
    if "tags" in step_data:
        tags = step_data["tags"]
        if not isinstance(tags, list):
            if "tags" not in errors:
                errors["tags"] = []
            errors["tags"].append("Tags must be a list")
        else:
            for i, tag in enumerate(tags):
                if not isinstance(tag, str):
                    if "tags" not in errors:
                        errors["tags"] = []
                    errors["tags"].append(f"Tag at index {i} must be a string")
    
    return errors


def validate_progression_data(progression_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Validate progression data structure and technical requirements.
    
    Args:
        progression_data: Dictionary containing progression data
        
    Returns:
        Dictionary with validation errors (empty if valid)
    """
    errors = {}
    
    # Required fields
    required_fields = ["arc_id", "current_step_index"]
    for field in required_fields:
        if field not in progression_data or progression_data[field] is None:
            if "required" not in errors:
                errors["required"] = []
            errors["required"].append(f"Field '{field}' is required")
    
    # Current step index validation
    if "current_step_index" in progression_data:
        current_index = progression_data["current_step_index"]
        if not isinstance(current_index, int):
            if "current_step_index" not in errors:
                errors["current_step_index"] = []
            errors["current_step_index"].append("Current step index must be an integer")
        elif current_index < 0:
            if "current_step_index" not in errors:
                errors["current_step_index"] = []
            errors["current_step_index"].append("Current step index cannot be negative")
    
    # Completion percentage validation
    if "completion_percentage" in progression_data:
        completion = progression_data["completion_percentage"]
        if not isinstance(completion, (int, float)):
            if "completion_percentage" not in errors:
                errors["completion_percentage"] = []
            errors["completion_percentage"].append("Completion percentage must be a number")
        elif completion < 0 or completion > 1:
            if "completion_percentage" not in errors:
                errors["completion_percentage"] = []
            errors["completion_percentage"].append("Completion percentage must be between 0 and 1")
    
    # Progression method validation
    if "progression_method" in progression_data:
        method = progression_data["progression_method"]
        if isinstance(method, str):
            try:
                ProgressionMethod(method)
            except ValueError:
                if "progression_method" not in errors:
                    errors["progression_method"] = []
                errors["progression_method"].append(f"Invalid progression method: {method}")
        elif not isinstance(method, ProgressionMethod):
            if "progression_method" not in errors:
                errors["progression_method"] = []
            errors["progression_method"].append("Progression method must be a valid ProgressionMethod enum")
    
    # Step lists validation
    for list_field in ["completed_steps", "failed_steps", "skipped_steps"]:
        if list_field in progression_data:
            step_list = progression_data[list_field]
            if not isinstance(step_list, list):
                if list_field not in errors:
                    errors[list_field] = []
                errors[list_field].append(f"{list_field} must be a list")
            else:
                for i, step_index in enumerate(step_list):
                    if not isinstance(step_index, int):
                        if list_field not in errors:
                            errors[list_field] = []
                        errors[list_field].append(f"Step index at position {i} must be an integer")
                    elif step_index < 0:
                        if list_field not in errors:
                            errors[list_field] = []
                        errors[list_field].append(f"Step index at position {i} cannot be negative")
    
    # Duration validations
    for duration_field in ["average_step_duration", "total_duration"]:
        if duration_field in progression_data:
            duration = progression_data[duration_field]
            if not isinstance(duration, (int, float)):
                if duration_field not in errors:
                    errors[duration_field] = []
                errors[duration_field].append(f"{duration_field} must be a number")
            elif duration < 0:
                if duration_field not in errors:
                    errors[duration_field] = []
                errors[duration_field].append(f"{duration_field} cannot be negative")
    
    # Boolean field validation
    if "is_active" in progression_data:
        is_active = progression_data["is_active"]
        if not isinstance(is_active, bool):
            if "is_active" not in errors:
                errors["is_active"] = []
            errors["is_active"].append("is_active must be a boolean")
    
    return errors 