#!/usr/bin/env python3
import json

def verify_tasks():
    print("Reading tasks.json...")
    with open('tasks/tasks.json', 'r') as f:
        data = json.load(f)
    
    tasks = data.get('tasks', [])
    print(f"\nFound {len(tasks)} tasks")
    
    # Print first and last few tasks
    print("\nFirst 3 tasks:")
    for task in tasks[:3]:
        print(f"ID {task['id']}: {task['title']}")
    
    print("\nLast 3 tasks:")
    for task in tasks[-3:]:
        print(f"ID {task['id']}: {task['title']}")
    
    # Verify task IDs are sequential
    ids = [task['id'] for task in tasks]
    expected_ids = list(range(1, len(tasks) + 1))
    if ids == expected_ids:
        print("\nTask IDs are sequential")
    else:
        print("\nWarning: Task IDs are not sequential")
        print("First mismatch:", next(i for i, (a, b) in enumerate(zip(ids, expected_ids)) if a != b))
    
    # Check for duplicate IDs
    if len(ids) == len(set(ids)):
        print("No duplicate IDs found")
    else:
        print("Warning: Duplicate IDs found")
        from collections import Counter
        duplicates = [id for id, count in Counter(ids).items() if count > 1]
        print("Duplicate IDs:", duplicates)

if __name__ == "__main__":
    verify_tasks() 