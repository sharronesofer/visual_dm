#!/usr/bin/env python3
"""
Task Deduplication Tool

This script works with the task_similarity.py analyzer to help merge or deduplicate 
similar tasks identified by the analysis.

Usage:
    python deduplicate_tasks.py [options]

Options:
    --file          Path to the tasks.json file (default: tasks/tasks.json)
    --similarity    Path to similarity results JSON file (default: task_similarity_results.json)
    --dry-run       Show what would be done without making changes (default: False)
    --output        Where to write the deduplicated tasks file (default: tasks/tasks_deduplicated.json)
"""

import argparse
import json
import sys
import os
from typing import Dict, List, Tuple, Any
import datetime
import shutil
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored terminal output
init()

def load_tasks(file_path: str) -> Tuple[List[Dict], Dict]:
    """Load tasks from a tasks.json file and create a task lookup dictionary."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'tasks' in data:
                tasks = data['tasks']
                # Create metadata dictionary for any additional fields
                metadata = {k: v for k, v in data.items() if k != 'tasks'}
            elif isinstance(data, list):
                tasks = data
                metadata = {}
            else:
                print(f"{Fore.RED}Error: Unexpected JSON structure in {file_path}{Style.RESET_ALL}")
                sys.exit(1)
                
            # Create task lookup dictionary
            task_lookup = {str(task.get('id')): task for task in tasks}
            
            return tasks, metadata, task_lookup
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File {file_path} not found{Style.RESET_ALL}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: {file_path} is not a valid JSON file{Style.RESET_ALL}")
        sys.exit(1)

def load_similarity_results(file_path: str) -> List[Dict]:
    """Load similarity analysis results from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'duplicate_candidates' in data:
                return data['duplicate_candidates']
            else:
                print(f"{Fore.RED}Error: Unexpected JSON structure in {file_path}{Style.RESET_ALL}")
                sys.exit(1)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: Similarity results file {file_path} not found. Run task_similarity.py first with --output=json{Style.RESET_ALL}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: {file_path} is not a valid JSON file{Style.RESET_ALL}")
        sys.exit(1)

def extract_task_id(id_str: str) -> str:
    """Extract the numeric task ID from formatted strings like '123 (subtask)' or '123.4 (subtask)'"""
    # Remove subtask label if present
    if " (subtask)" in id_str:
        id_str = id_str.replace(" (subtask)", "")
    
    # For parent.child formats, keep only the parent ID
    if "." in id_str:
        id_str = id_str.split(".")[0]
        
    return id_str

def merge_tasks(task1: Dict, task2: Dict) -> Dict:
    """Merge two similar tasks, combining their information intelligently."""
    # Create a new task with the properties of the first task
    merged_task = task1.copy()
    
    # Choose the most descriptive title (usually the longer one)
    if len(task2.get('title', '')) > len(task1.get('title', '')):
        merged_task['title'] = task2.get('title')
    
    # Combine descriptions if they're different
    desc1 = task1.get('description', '')
    desc2 = task2.get('description', '')
    if desc1 != desc2:
        merged_task['description'] = f"{desc1}\n\nAdditional info: {desc2}"
    
    # Combine details if they're different
    details1 = task1.get('details', '')
    details2 = task2.get('details', '')
    if details1 != details2:
        merged_task['details'] = f"{details1}\n\n--- Additional Implementation Details ---\n\n{details2}"
    
    # Combine test strategies if they're different
    test1 = task1.get('testStrategy', '')
    test2 = task2.get('testStrategy', '')
    if test1 != test2:
        merged_task['testStrategy'] = f"{test1}\n\n--- Additional Test Strategies ---\n\n{test2}"
    
    # Combine dependencies (unique set)
    deps1 = task1.get('dependencies', [])
    deps2 = task2.get('dependencies', [])
    if deps1 or deps2:
        merged_task['dependencies'] = list(set(deps1 + deps2))
    
    # Keep the highest priority
    priority_values = {'low': 0, 'medium': 1, 'high': 2}
    prio1 = priority_values.get(task1.get('priority', 'medium'), 1)
    prio2 = priority_values.get(task2.get('priority', 'medium'), 1)
    
    priority_reverse = {0: 'low', 1: 'medium', 2: 'high'}
    merged_task['priority'] = priority_reverse.get(max(prio1, prio2), 'medium')
    
    # Combine subtasks if any
    subtasks1 = task1.get('subtasks', [])
    subtasks2 = task2.get('subtasks', [])
    if subtasks1 or subtasks2:
        # This is a simplistic approach - in a real implementation, you'd want to 
        # deduplicate subtasks as well using similar logic
        merged_task['subtasks'] = subtasks1 + subtasks2
    
    # Add a note about the merge
    merged_task['notes'] = f"This task was created by merging tasks {task1.get('id')} and {task2.get('id')} on {datetime.datetime.now().strftime('%Y-%m-%d')}"
    
    return merged_task

def interactive_deduplication(
    tasks: List[Dict], 
    similarity_results: List[Dict], 
    task_lookup: Dict, 
    dry_run: bool = False
) -> List[Dict]:
    """Interactive process to deduplicate tasks based on similarity results."""
    if not similarity_results:
        print(f"{Fore.GREEN}No duplicate candidates found. No action needed.{Style.RESET_ALL}")
        return tasks
    
    # Track tasks to remove
    tasks_to_remove = set()
    tasks_to_add = []
    
    print(f"{Fore.CYAN}Found {len(similarity_results)} potential duplicate task pairs.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}For each pair, you can choose an action:{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}[k] Keep both tasks (no action){Style.RESET_ALL}")
    print(f"  {Fore.WHITE}[1] Keep task 1 and remove task 2{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}[2] Keep task 2 and remove task 1{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}[m] Merge tasks into a new combined task{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}[s] Skip this pair{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}[q] Quit deduplication process{Style.RESET_ALL}")
    print()
    
    for i, result in enumerate(similarity_results):
        similarity = result.get('similarity', 0)
        task1_id = extract_task_id(result.get('task1', {}).get('id', ''))
        task2_id = extract_task_id(result.get('task2', {}).get('id', ''))
        
        # Skip if either task has already been processed
        if task1_id in tasks_to_remove or task2_id in tasks_to_remove:
            continue
        
        # Get the full task objects
        task1 = task_lookup.get(task1_id)
        task2 = task_lookup.get(task2_id)
        
        if not task1 or not task2:
            print(f"{Fore.RED}Warning: Could not find tasks with IDs {task1_id} and/or {task2_id}. Skipping.{Style.RESET_ALL}")
            continue
        
        # Display the task details
        print(f"{Fore.CYAN}Pair {i+1}/{len(similarity_results)} - Similarity: {similarity:.2f}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Task 1 (ID: {task1_id}):{Style.RESET_ALL} {task1.get('title')}")
        print(f"{Fore.WHITE}Status: {task1.get('status')}, Priority: {task1.get('priority')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Description: {task1.get('description')}{Style.RESET_ALL}")
        print()
        print(f"{Fore.BLUE}Task 2 (ID: {task2_id}):{Style.RESET_ALL} {task2.get('title')}")
        print(f"{Fore.WHITE}Status: {task2.get('status')}, Priority: {task2.get('priority')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Description: {task2.get('description')}{Style.RESET_ALL}")
        print()
        
        # Get user decision
        while True:
            choice = input(f"{Fore.YELLOW}Action for this pair [k/1/2/m/s/q]: {Style.RESET_ALL}").lower()
            
            if choice in ['k', '1', '2', 'm', 's', 'q']:
                break
            else:
                print(f"{Fore.RED}Invalid choice. Please select k, 1, 2, m, s, or q.{Style.RESET_ALL}")
        
        if choice == 'q':
            print(f"{Fore.YELLOW}Quitting deduplication process.{Style.RESET_ALL}")
            break
        
        if choice == 's':
            print(f"{Fore.YELLOW}Skipping this pair.{Style.RESET_ALL}")
            continue
            
        if choice == 'k':
            print(f"{Fore.GREEN}Keeping both tasks.{Style.RESET_ALL}")
            continue
            
        if choice == '1':
            if not dry_run:
                tasks_to_remove.add(task2_id)
                print(f"{Fore.GREEN}Task {task2_id} will be removed, keeping task {task1_id}.{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}[DRY RUN] Would remove task {task2_id}, keeping task {task1_id}.{Style.RESET_ALL}")
        
        elif choice == '2':
            if not dry_run:
                tasks_to_remove.add(task1_id)
                print(f"{Fore.GREEN}Task {task1_id} will be removed, keeping task {task2_id}.{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}[DRY RUN] Would remove task {task1_id}, keeping task {task2_id}.{Style.RESET_ALL}")
        
        elif choice == 'm':
            if not dry_run:
                merged_task = merge_tasks(task1, task2)
                # Keep the ID of the first task for the merged task
                merged_task['id'] = task1_id
                tasks_to_add.append(merged_task)
                tasks_to_remove.add(task1_id)
                tasks_to_remove.add(task2_id)
                print(f"{Fore.GREEN}Tasks {task1_id} and {task2_id} will be merged into a new task.{Style.RESET_ALL}")
            else:
                print(f"{Fore.GREEN}[DRY RUN] Would merge tasks {task1_id} and {task2_id} into a new task.{Style.RESET_ALL}")
        
        print("-" * 80)
    
    if not dry_run and (tasks_to_remove or tasks_to_add):
        # Create new task list with removed tasks filtered out
        new_tasks = [task for task in tasks if str(task.get('id')) not in tasks_to_remove]
        
        # Add merged tasks
        new_tasks.extend(tasks_to_add)
        
        print(f"{Fore.GREEN}Deduplication complete. Removed {len(tasks_to_remove)} tasks, added {len(tasks_to_add)} merged tasks.{Style.RESET_ALL}")
        return new_tasks
    else:
        return tasks

def save_tasks(tasks: List[Dict], metadata: Dict, output_file: str):
    """Save the deduplicated tasks back to a JSON file."""
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # If the original had metadata, preserve it
    if metadata:
        output_data = metadata.copy()
        output_data['tasks'] = tasks
    else:
        output_data = tasks
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"{Fore.GREEN}Saved deduplicated tasks to {output_file}{Style.RESET_ALL}")

def create_backup(file_path: str):
    """Create a backup of the original tasks file."""
    backup_path = f"{file_path}.bak.{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.copy2(file_path, backup_path)
        print(f"{Fore.GREEN}Created backup of original file at {backup_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Warning: Could not create backup: {str(e)}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description='Deduplicate similar tasks in tasks.json')
    parser.add_argument('--file', type=str, default='tasks/tasks.json',
                        help='Path to the tasks.json file')
    parser.add_argument('--similarity', type=str, default='task_similarity_results.json',
                        help='Path to the similarity results JSON file')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')
    parser.add_argument('--output', type=str, default=None,
                        help='Where to write the deduplicated tasks file (default: replaces original)')
                        
    args = parser.parse_args()
    
    # Set default output to be the same as input if not specified
    if args.output is None:
        args.output = args.file
    
    # Load tasks and similarity results
    tasks, metadata, task_lookup = load_tasks(args.file)
    similarity_results = load_similarity_results(args.similarity)
    
    # Create backup of original file if we're not doing a dry run and output is same as input
    if not args.dry_run and args.output == args.file:
        create_backup(args.file)
    
    # Perform interactive deduplication
    new_tasks = interactive_deduplication(tasks, similarity_results, task_lookup, args.dry_run)
    
    # Save result if not dry run
    if not args.dry_run and new_tasks != tasks:
        save_tasks(new_tasks, metadata, args.output)

if __name__ == "__main__":
    main() 