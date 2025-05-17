#!/usr/bin/env python3
"""
Consolidate Tasks Script

This script consolidates tasks 659 and 660 into a single task with combined details.

Usage:
    python consolidate_tasks.py
"""

import json
import os
import sys
from datetime import datetime
import copy
import argparse

# File paths
TASKS_FILE = "tasks/tasks.json"
BACKUP_SUFFIX = f".bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file")
        sys.exit(1)

def save_json_file(file_path, data):
    """Save data to a JSON file with pretty formatting."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def create_backup(file_path):
    """Create a backup of the original file."""
    backup_path = f"{file_path}{BACKUP_SUFFIX}"
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        print(f"Created backup of {file_path} at {backup_path}")
    except Exception as e:
        print(f"Warning: Could not create backup: {str(e)}")

def consolidate_tasks_659_660(tasks_data):
    """Consolidate tasks 659 and 660 into a single task."""
    tasks = tasks_data.get('tasks', [])
    task_659 = None
    task_660 = None
    
    # Find the tasks to consolidate
    for task in tasks:
        if task.get('id') == 659:
            task_659 = task
        elif task.get('id') == 660:
            task_660 = task
    
    if not task_659 or not task_660:
        print("Error: Could not find both tasks 659 and 660")
        sys.exit(1)
    
    # Create consolidated task
    consolidated_task = copy.deepcopy(task_659)
    
    # Create combined description
    consolidated_task['description'] = (
        "Design and implement the fundamental data models and relationship management functionality for the "
        "Nemesis/Rival System, including relationship types, grudge tracking, memory integration, profile models, "
        "triggering system, state progression mechanisms, and persistence layer that integrates with the existing RelationshipManager."
    )
    
    # Create combined details
    consolidated_task['details'] = (
        "This task involves creating the core data architecture for the Nemesis/Rival System:\n\n"
        "1. Data Models:\n"
        "   - Create a `RivalRelationship` class that extends the base relationship model with rivalry-specific attributes\n"
        "   - Create a `NemesisRelationship` class with more intense antagonistic properties\n"
        "   - Add relationship type enums (NemesisRelationship and RivalRelationship) to the existing system\n"
        "   - Implement a `GrudgePoint` tracking system with accumulation and decay mechanisms\n"
        "   - Design a `RelationshipMemory` class to store significant interactions and events\n"
        "   - Define `RelationshipState` enums (e.g., Neutral, Annoyed, Rival, Nemesis) with transition rules\n\n"
        
        "2. Profile Models:\n"
        "   - Create NemesisProfile model with power level scaling and vendetta status\n"
        "   - Implement RivalProfile model with rivalry intensity tracking and competition focus\n"
        "   - Design special abilities collection with activation conditions\n"
        "   - Include profile-specific attributes for different relationship types\n\n"
        
        "3. RelationshipManager Extension:\n"
        "   - Extend the existing RelationshipManager to handle rival/nemesis relationships\n"
        "   - Implement methods for calculating relationship intensity based on interaction history\n"
        "   - Create transition logic between relationship states based on thresholds and triggers\n"
        "   - Develop persistence mechanisms to maintain relationships across game sessions\n"
        "   - Add methods for querying and filtering nemesis/rival relationships\n\n"
        
        "4. Triggering System:\n"
        "   - Create event-based triggers for NPC → rival conversion\n"
        "   - Implement threshold-based triggers for rival → nemesis promotion\n"
        "   - Add cooldown mechanisms to prevent rapid state changes\n"
        "   - Design notification system for significant relationship changes\n\n"
        
        "5. Integration Points:\n"
        "   - Connect the relationship system with the existing character memory system\n"
        "   - Ensure compatibility with the Arcs System for narrative integration\n"
        "   - Implement hooks for gameplay systems to influence relationship dynamics\n"
        "   - Create event listeners for significant game events that affect rivalries\n\n"
        
        "6. Technical Considerations:\n"
        "   - Ensure efficient data storage for potentially numerous relationships\n"
        "   - Implement proper serialization/deserialization for save game compatibility\n"
        "   - Design with extensibility in mind for future relationship types\n"
        "   - Document the API thoroughly for other team members\n"
        "   - Add versioning support for future model extensions\n\n"
        
        "The implementation should follow the project's existing patterns for relationship modeling while introducing "
        "the specialized functionality needed for dynamic rivalries and nemesis relationships. It must ensure that "
        "relationship changes persist across game sessions and influence NPC behavior appropriately."
    )
    
    # Create combined test strategy
    consolidated_task['testStrategy'] = (
        "Testing for this task should be comprehensive and cover both unit tests and integration scenarios:\n\n"
        "1. Unit Tests:\n"
        "   - Test creation and initialization of RivalRelationship and NemesisRelationship objects\n"
        "   - Verify grudge point accumulation and decay functions with various inputs\n"
        "   - Test state transition logic for all possible relationship states\n"
        "   - Validate memory record integration with mock memory objects\n"
        "   - Ensure relationship intensity calculations produce expected results\n"
        "   - Test serialization/deserialization of relationship objects\n"
        "   - Test profile model creation and attributes for both rival and nemesis types\n"
        "   - Verify thread safety for concurrent relationship updates\n\n"
        
        "2. Integration Tests:\n"
        "   - Verify RelationshipManager properly handles rival and nemesis relationships\n"
        "   - Test persistence across simulated game sessions\n"
        "   - Validate interaction with the memory system using test fixtures\n"
        "   - Ensure compatibility with the Arcs System through integration tests\n"
        "   - Test performance with large numbers of relationships (100+)\n"
        "   - Verify trigger system correctly promotes/demotes relationships\n"
        "   - Test that relationship changes trigger appropriate game events\n\n"
        
        "3. Scenario Tests:\n"
        "   - Create test scenarios that simulate real gameplay situations:\n"
        "     - Character becoming a rival through multiple negative interactions\n"
        "     - Rival escalating to nemesis status\n"
        "     - Relationship de-escalation through positive actions\n"
        "     - Persistence of relationships across game restarts\n"
        "     - Testing the triggering system with various conditions\n\n"
        
        "4. Performance Tests:\n"
        "   - Benchmark relationship queries with varying numbers of NPCs (100, 1000, 10000)\n"
        "   - Measure memory usage for games with many rival/nemesis relationships\n"
        "   - Test serialization/deserialization performance with large relationship datasets\n\n"
        
        "5. Edge Cases:\n"
        "   - Test behavior when relationships reach minimum/maximum intensity values\n"
        "   - Verify handling of deleted characters with active rivalries\n"
        "   - Test concurrent modifications to the same relationship\n"
        "   - Validate system behavior during save/load operations\n\n"
        
        "6. Validation Criteria:\n"
        "   - All unit and integration tests must pass\n"
        "   - Performance benchmarks must meet specified thresholds\n"
        "   - Data models must correctly serialize/deserialize without data loss\n"
        "   - Relationship transitions must occur predictably based on defined triggers\n"
        "   - System must integrate seamlessly with existing relationship and memory systems\n\n"
        
        "The test suite should be automated where possible and include appropriate fixtures and mock objects "
        "to simulate the game environment. Documentation of test results should include coverage metrics and "
        "performance benchmarks for future reference."
    )
    
    # Find the indices of the tasks to be removed and the one to be kept
    task_indices = []
    for i, task in enumerate(tasks):
        if task.get('id') in [659, 660]:
            task_indices.append(i)
    
    # Remove the tasks that are being consolidated
    for index in sorted(task_indices, reverse=True):
        tasks.pop(index)
    
    # Add the consolidated task
    tasks.append(consolidated_task)
    
    # Update the tasks data
    tasks_data['tasks'] = tasks
    
    return tasks_data

def move_done_tasks(tasks_file, done_tasks_file):
    """Move all tasks with status 'done' from tasks_file to done_tasks_file."""
    tasks_data = load_json_file(tasks_file)
    all_tasks = tasks_data.get('tasks', [])
    done_tasks = [t for t in all_tasks if t.get('status') == 'done']
    remaining_tasks = [t for t in all_tasks if t.get('status') != 'done']

    # Load or initialize done_tasks_file
    if os.path.exists(done_tasks_file):
        done_data = load_json_file(done_tasks_file)
        done_list = done_data.get('tasks', [])
    else:
        done_list = []

    # Append new done tasks
    done_list.extend(done_tasks)
    save_json_file(done_tasks_file, {'tasks': done_list})

    # Save remaining tasks back to original file
    tasks_data['tasks'] = remaining_tasks
    save_json_file(tasks_file, tasks_data)
    print(f"Moved {len(done_tasks)} done tasks to {done_tasks_file}.")

def main():
    parser = argparse.ArgumentParser(description='Consolidate or move done tasks in tasks.json')
    parser.add_argument('--move-done', action='store_true', help='Move all done tasks to done_tasks.json')
    args = parser.parse_args()

    if args.move_done:
        create_backup(TASKS_FILE)
        move_done_tasks(TASKS_FILE, 'tasks/done_tasks.json')
    else:
        # Default: consolidate tasks 659 and 660
        create_backup(TASKS_FILE)
        tasks_data = load_json_file(TASKS_FILE)
        updated_tasks_data = consolidate_tasks_659_660(tasks_data)
        save_json_file(TASKS_FILE, updated_tasks_data)
        print("Successfully consolidated tasks 659 and 660")

if __name__ == "__main__":
    main() 