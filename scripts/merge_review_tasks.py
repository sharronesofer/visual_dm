#!/usr/bin/env python3
import json
import os
from glob import glob

def get_highest_task_id():
    """Find the highest task ID from existing task files"""
    task_files = glob('tasks/task_*.txt')
    if not task_files:
        return 0
    return max(int(f.split('task_')[1].split('.')[0]) for f in task_files)

def create_task_file(task, task_id):
    """Create a task file with the given task data"""
    filename = f'tasks/task_{task_id:03d}.txt'
    
    # Format dependencies
    deps = ','.join(str(d) for d in task.get('dependencies', []))
    if not deps:
        deps = 'None'
    
    # Create task content
    content = [
        f'# Task ID: {task_id}',
        f'# Title: {task["title"]}',
        f'# Status: {task["status"]}',
        f'# Dependencies: {deps}',
        f'# Priority: {task["priority"]}',
        f'# Description: {task["description"]}',
        '# Details:',
        task.get('details', ''),
    ]
    
    # Add test strategy if it exists
    if task.get('testStrategy'):
        content.extend(['', '# Test Strategy:', task['testStrategy']])
    
    # Add subtasks if they exist
    if task.get('subtasks'):
        content.extend(['', '# Subtasks:'])
        for subtask in task['subtasks']:
            # Format subtask dependencies
            subtask_deps = ','.join(str(d) for d in subtask.get('dependencies', []))
            if not subtask_deps:
                subtask_deps = 'None'
            
            content.extend([
                f'## {subtask["title"]} [{subtask["status"]}]',
                f'### Dependencies: {subtask_deps}',
                f'### Description: {subtask.get("description", "")}',
            ])
            if subtask.get('details'):
                content.extend(['### Details:', subtask['details']])
    
    # Write the task file
    with open(filename, 'w') as f:
        f.write('\n'.join(content))
    print(f'Created {filename}')

def main():
    print("Starting task merge process...")
    
    # Get the highest existing task ID
    highest_id = get_highest_task_id()
    print(f"Highest existing task ID: {highest_id}")
    
    # Read the current tasks.json
    with open('tasks/tasks.json', 'r') as f:
        tasks_data = json.load(f)
    
    # Get the review system tasks
    review_tasks = tasks_data['tasks']
    print(f"Found {len(review_tasks)} review system tasks")
    
    # Create task files for review system tasks
    next_id = highest_id + 1
    for task in review_tasks:
        # Update task ID and dependencies
        old_id = task['id']
        task['id'] = next_id
        
        # Adjust dependencies
        if task['dependencies']:
            task['dependencies'] = [d + highest_id for d in task['dependencies']]
        
        # Adjust subtask dependencies if they exist
        for subtask in task.get('subtasks', []):
            if subtask['dependencies']:
                subtask['dependencies'] = [d + highest_id if isinstance(d, int) else d for d in subtask['dependencies']]
        
        # Create the task file
        create_task_file(task, next_id)
        print(f"Processed task {old_id} -> {next_id}: {task['title']}")
        next_id += 1
    
    print("\nDone! Review system tasks have been appended to the existing tasks.")

if __name__ == "__main__":
    main() 