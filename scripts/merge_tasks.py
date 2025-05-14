#!/usr/bin/env python3
import json
import os

def parse_dependency(dep_str):
    """Parse a dependency string into either an int or a string (for subtask refs)"""
    dep_str = dep_str.strip()
    if not dep_str or dep_str == 'None':
        return None
    if '.' in dep_str:  # It's a subtask reference
        return dep_str
    return int(dep_str)

print("Starting task merge process...")

# First backup the current tasks.json
if os.path.exists('tasks/tasks.json'):
    print("Backing up current tasks.json to tasks.json.review")
    os.rename('tasks/tasks.json', 'tasks/tasks.json.review')

# Create a new tasks object starting with the game dev tasks
tasks = {"tasks": []}

# Read all task files from task_001.txt to task_082.txt
print("\nProcessing game dev task files...")
for i in range(1, 83):
    filename = f'tasks/task_{i:03d}.txt'
    if not os.path.exists(filename):
        continue
        
    print(f"Processing {filename}...")
    with open(filename, 'r') as f:
        content = f.read()
        
    # Parse the task file
    lines = content.split('\n')
    task = {
        "id": int(next(line.split(': ')[1] for line in lines if line.startswith('# Task ID:'))),
        "title": next(line.split(': ')[1] for line in lines if line.startswith('# Title:')),
        "status": next(line.split(': ')[1] for line in lines if line.startswith('# Status:')),
        "priority": next(line.split(': ')[1] for line in lines if line.startswith('# Priority:')),
        "description": next(line.split(': ')[1] for line in lines if line.startswith('# Description:')),
        "details": "",
        "testStrategy": "",
        "subtasks": []
    }
    
    # Handle dependencies
    deps_line = next(line.split(': ')[1] for line in lines if line.startswith('# Dependencies:'))
    task['dependencies'] = [x for x in [parse_dependency(d) for d in deps_line.split(',')] if x is not None]
    
    # Get details and test strategy
    if '# Details:' in content:
        details_section = content.split('# Details:\n')[1]
        if '# Test Strategy:' in details_section:
            task['details'] = details_section.split('# Test Strategy:')[0].strip()
            test_section = details_section.split('# Test Strategy:\n')[1]
            if '# Subtasks:' in test_section:
                task['testStrategy'] = test_section.split('# Subtasks:')[0].strip()
            else:
                task['testStrategy'] = test_section.strip()
        else:
            if '# Subtasks:' in details_section:
                task['details'] = details_section.split('# Subtasks:')[0].strip()
            else:
                task['details'] = details_section.strip()
    
    # Parse subtasks if they exist
    if '# Subtasks:' in content:
        print(f"  Found subtasks in {filename}")
        subtasks_section = content.split('# Subtasks:\n')[1]
        current_subtask = None
        details_lines = []
        
        for line in subtasks_section.split('\n'):
            if line.startswith('## '):
                if current_subtask:
                    if details_lines:
                        current_subtask['details'] = '\n'.join(details_lines).strip()
                        details_lines = []
                    task['subtasks'].append(current_subtask)
                
                # Start new subtask
                subtask_title = line[3:].split('[')[0].strip()
                subtask_status = line.split('[')[1].split(']')[0] if '[' in line else 'pending'
                current_subtask = {
                    "id": len(task['subtasks']) + 1,
                    "title": subtask_title,
                    "status": subtask_status,
                    "dependencies": [],
                    "description": "",
                    "details": ""
                }
            elif line.startswith('### Dependencies:'):
                if current_subtask:
                    deps = line.split(': ')[1]
                    current_subtask['dependencies'] = [x for x in [parse_dependency(d) for d in deps.split(',')] if x is not None]
            elif line.startswith('### Description:'):
                if current_subtask:
                    current_subtask['description'] = line.split(': ')[1]
            elif line.startswith('### Details:'):
                if current_subtask:
                    details_lines = []
            elif current_subtask and not line.startswith('###'):
                details_lines.append(line)
        
        if current_subtask:
            if details_lines:
                current_subtask['details'] = '\n'.join(details_lines).strip()
            task['subtasks'].append(current_subtask)
    
    tasks['tasks'].append(task)
    print(f"  Added task {task['id']}: {task['title']}")

print(f"\nProcessed {len(tasks['tasks'])} game dev tasks")

print("\nLoading review system tasks...")
# Load the review system tasks
with open('tasks/tasks.json.review', 'r') as f:
    review_tasks = json.load(f)

print(f"Found {len(review_tasks['tasks'])} review system tasks")

# Add the review system tasks, adjusting their IDs to continue from where game dev tasks left off
next_id = max(task['id'] for task in tasks['tasks']) + 1
print(f"\nAdjusting review system task IDs starting from {next_id}")

for review_task in review_tasks['tasks']:
    old_id = review_task['id']
    review_task['id'] = next_id
    # Adjust dependencies if they exist
    if review_task['dependencies']:
        review_task['dependencies'] = [d + 82 for d in review_task['dependencies']]
    # Adjust subtask dependencies if they exist
    for subtask in review_task.get('subtasks', []):
        if subtask['dependencies']:
            subtask['dependencies'] = [d + 82 if isinstance(d, int) else d for d in subtask['dependencies']]
    print(f"  Adjusted task {old_id} -> {next_id}: {review_task['title']}")
    next_id += 1
    tasks['tasks'].append(review_task)

print(f"\nTotal tasks after merge: {len(tasks['tasks'])}")

# Save the merged tasks
print("\nSaving merged tasks to tasks.json...")
with open('tasks/tasks.json', 'w') as f:
    json.dump(tasks, f, indent=2)

# Backup the review system tasks just in case
print("Backing up review system tasks to tasks.json.review.bak")
os.rename('tasks/tasks.json.review', 'tasks/tasks.json.review.bak')

print("\nDone!") 