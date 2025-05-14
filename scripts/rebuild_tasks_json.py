#!/usr/bin/env python3
import json
import os
import re
from glob import glob
from collections import defaultdict

def is_review_task(title):
    """Identify if a task is part of the review system"""
    review_keywords = [
        'review', 'template', 'question', 'response', 'feedback',
        'assessment', 'evaluation', 'rating', 'survey'
    ]
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in review_keywords)

def parse_task_file(filename):
    """Parse a task file and return the task data"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Extract basic task info using regex
    task_id = int(re.search(r'# Task ID: (\d+)', content).group(1))
    title = re.search(r'# Title: (.+)', content).group(1)
    status = re.search(r'# Status: (.+)', content).group(1)
    deps_match = re.search(r'# Dependencies: (.+)', content)
    deps = deps_match.group(1) if deps_match else 'None'
    priority = re.search(r'# Priority: (.+)', content).group(1)
    desc_match = re.search(r'# Description: (.+)', content)
    description = desc_match.group(1) if desc_match else ''
    details_match = re.search(r'# Implementation Details:\s*\n(.*?)(?=\n#|\Z)', content, re.DOTALL)
    details = details_match.group(1).strip() if details_match else ''
    test_match = re.search(r'# Test Strategy:\s*\n(.*?)(?=\n#|\Z)', content, re.DOTALL)
    test_strategy = test_match.group(1).strip() if test_match else ''
    
    # Parse dependencies
    if deps and deps != 'None':
        dependencies = [int(d.strip()) for d in deps.split(',') if d.strip().isdigit()]
    else:
        dependencies = []
    
    return {
        'id': task_id,
        'title': title,
        'status': status,
        'dependencies': dependencies,
        'priority': priority,
        'description': description,
        'details': details,
        'testStrategy': test_strategy
    }

def write_task_file(task, output_dir='tasks'):
    """Write a task to its individual file"""
    filename = f"{output_dir}/task_{task['id']:03d}.txt"
    content = [
        f"# Task ID: {task['id']}",
        f"# Title: {task['title']}",
        f"# Status: {task['status']}",
        f"# Dependencies: {','.join(map(str, task['dependencies'])) if task['dependencies'] else 'None'}",
        f"# Priority: {task['priority']}",
        f"# Description: {task['description']}",
        "\n# Implementation Details:",
        task['details'],
        "\n# Test Strategy:",
        task['testStrategy']
    ]
    
    with open(filename, 'w') as f:
        f.write('\n'.join(content))

def main():
    # Create tasks directory if it doesn't exist
    os.makedirs('tasks', exist_ok=True)
    
    # Backup existing tasks.json if it exists
    if os.path.exists('tasks/tasks.json'):
        os.rename('tasks/tasks.json', 'tasks/tasks.json.bak')
    
    # Get all task files
    task_files = glob('tasks/task_*.txt')
    
    # Group tasks by title to handle duplicates
    tasks_by_title = defaultdict(list)
    for file in task_files:
        task = parse_task_file(file)
        tasks_by_title[task['title']].append(task)
    
    # Keep only the most recent version of each task
    unique_tasks = []
    for title, tasks in tasks_by_title.items():
        # Sort by task ID (higher ID means more recent)
        tasks.sort(key=lambda x: x['id'])
        unique_tasks.append(tasks[-1])
    
    # Separate review and non-review tasks
    review_tasks = []
    non_review_tasks = []
    
    for task in unique_tasks:
        if is_review_task(task['title']):
            review_tasks.append(task)
        else:
            non_review_tasks.append(task)
    
    # Combine tasks with non-review tasks first, then review tasks
    all_tasks = non_review_tasks + review_tasks
    
    # Renumber tasks sequentially
    for i, task in enumerate(all_tasks, 1):
        old_id = task['id']
        task['id'] = i
        # Update dependencies to match new IDs
        new_deps = []
        for dep in task['dependencies']:
            # Find the new ID for this dependency
            for t in all_tasks:
                if t['id'] == dep:
                    new_deps.append(t['id'])
                    break
        task['dependencies'] = new_deps
    
    # Write individual task files
    for task in all_tasks:
        write_task_file(task)
    
    # Write tasks.json
    with open('tasks/tasks.json', 'w') as f:
        json.dump({'tasks': all_tasks}, f, indent=2)
    
    print(f"Successfully processed {len(all_tasks)} tasks")
    print(f"Non-review tasks: {len(non_review_tasks)}")
    print(f"Review tasks: {len(review_tasks)}")

if __name__ == '__main__':
    main() 