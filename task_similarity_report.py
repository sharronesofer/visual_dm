#!/usr/bin/env python3
"""
Task Similarity Report

A simplified version of the task similarity analyzer that just lists task similarities
above a specified threshold without interactive deduplication.

Usage:
    python task_similarity_report.py [options]

Options:
    --threshold     Similarity threshold (0.0-1.0) for reporting (default: 0.70)
    --file          Path to the tasks.json file (default: tasks/tasks.json)
    --include-done  Include done tasks in the analysis (default: exclude done tasks)
    --format        Output format: basic, detailed (default: detailed)
"""

import argparse
import json
import sys
from typing import Dict, List, Tuple
import difflib
from rapidfuzz import fuzz
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored terminal output
init()

def load_tasks(file_path: str) -> List[Dict]:
    """Load tasks from a tasks.json file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'tasks' in data:
                return data['tasks']
            elif isinstance(data, list):
                return data
            else:
                print(f"Error: Unexpected JSON structure in {file_path}")
                sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file")
        sys.exit(1)

def get_all_subtasks(tasks: List[Dict]) -> List[Dict]:
    """Extract all subtasks from the tasks list."""
    all_subtasks = []
    
    for task in tasks:
        if 'subtasks' in task and task['subtasks']:
            for subtask in task['subtasks']:
                # Add parent task reference for context
                subtask['parent_id'] = task.get('id')
                subtask['parent_title'] = task.get('title')
                all_subtasks.append(subtask)
    
    return all_subtasks

def compare_task_fields(task1: Dict, task2: Dict, field: str, weight: float = 1.0) -> float:
    """Compare a specific field between two tasks using fuzzy string matching."""
    val1 = task1.get(field, "")
    val2 = task2.get(field, "")
    
    # Skip empty fields
    if not val1 or not val2:
        return 0.0
    
    # Convert non-string values to strings
    if not isinstance(val1, str):
        val1 = str(val1)
    if not isinstance(val2, str):
        val2 = str(val2)
    
    # Calculate similarity ratio
    ratio = fuzz.token_sort_ratio(val1, val2) / 100.0
    return ratio * weight

def calculate_similarity(task1: Dict, task2: Dict, fields: List[str], weights: Dict[str, float]) -> float:
    """Calculate overall similarity between two tasks across multiple fields."""
    if task1.get('id') == task2.get('id'):
        return 0.0  # Same task
    
    # Don't compare tasks with their own subtasks
    if (task1.get('id') == task2.get('parent_id') or 
        task2.get('id') == task1.get('parent_id')):
        return 0.0
    
    total_weight = sum(weights.get(field, 1.0) for field in fields)
    similarity = sum(compare_task_fields(task1, task2, field, weights.get(field, 1.0)) 
                     for field in fields)
    
    # Normalize by total weight
    if total_weight > 0:
        similarity /= total_weight
    
    return similarity

def find_similar_tasks(tasks: List[Dict], subtasks: List[Dict], threshold: float, 
                       include_done: bool, fields: List[str]) -> List[Tuple[Dict, Dict, float]]:
    """Find similar tasks based on the given threshold."""
    similar_pairs = []
    all_items = tasks + subtasks
    
    # Define field weights - adjust based on importance
    weights = {
        'title': 2.0,        # Title is most important
        'description': 1.5,  # Description is important
        'details': 1.0,      # Details are good indicators but may have more variance
        'testStrategy': 0.5  # Test strategy is less important for similarity
    }
    
    # Remove done tasks if not included
    if not include_done:
        all_items = [task for task in all_items if task.get('status') != 'done']
    
    # Compare each task with every other task
    print(f"{Fore.CYAN}Analyzing {len(all_items)} tasks. This may take a moment...{Style.RESET_ALL}")
    
    # Keep track of analysis progress
    total_comparisons = (len(all_items) * (len(all_items) - 1)) // 2
    comparisons_done = 0
    last_percentage = -1
    
    for i, task1 in enumerate(all_items):
        for j, task2 in enumerate(all_items[i+1:], i+1):
            similarity = calculate_similarity(task1, task2, fields, weights)
            if similarity >= threshold:
                similar_pairs.append((task1, task2, similarity))
            
            # Update progress
            comparisons_done += 1
            percentage = (comparisons_done * 100) // total_comparisons
            if percentage > last_percentage and percentage % 10 == 0:
                print(f"{Fore.CYAN}Analysis progress: {percentage}%{Style.RESET_ALL}")
                last_percentage = percentage
    
    # Sort by similarity (descending)
    similar_pairs.sort(key=lambda x: x[2], reverse=True)
    return similar_pairs

def format_task_id(task: Dict) -> str:
    """Format the task ID for display, including parent info for subtasks."""
    if 'parent_id' in task:
        return f"{task['parent_id']}.{task['id']} (subtask)"
    return str(task['id'])

def print_basic_report(similar_pairs: List[Tuple[Dict, Dict, float]]) -> None:
    """Print a basic report of similar tasks."""
    if not similar_pairs:
        print(f"{Fore.GREEN}No similar tasks found above the threshold.{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}Found {len(similar_pairs)} task pairs with similarity above threshold:{Style.RESET_ALL}\n")
    
    for task1, task2, similarity in similar_pairs:
        similarity_color = Fore.RED if similarity > 0.95 else (Fore.YELLOW if similarity > 0.85 else Fore.WHITE)
        
        print(f"{similarity_color}Similarity: {similarity:.2f}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Task {format_task_id(task1)}{Style.RESET_ALL}: {task1.get('title')}")
        print(f"{Fore.BLUE}Task {format_task_id(task2)}{Style.RESET_ALL}: {task2.get('title')}")
        print("-" * 80)

def print_detailed_report(similar_pairs: List[Tuple[Dict, Dict, float]]) -> None:
    """Print a detailed report of similar tasks with descriptions and diff views."""
    if not similar_pairs:
        print(f"{Fore.GREEN}No similar tasks found above the threshold.{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}Found {len(similar_pairs)} task pairs with similarity above threshold:{Style.RESET_ALL}\n")
    
    for i, (task1, task2, similarity) in enumerate(similar_pairs):
        similarity_color = Fore.RED if similarity > 0.95 else (Fore.YELLOW if similarity > 0.85 else Fore.WHITE)
        
        print(f"{similarity_color}Similarity Pair {i+1}: {similarity:.2f}{Style.RESET_ALL}")
        
        # Task 1 details
        print(f"{Fore.BLUE}Task {format_task_id(task1)}: {task1.get('title')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Status: {task1.get('status', 'unknown')}, Priority: {task1.get('priority', 'unknown')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Description: {task1.get('description', 'No description')}{Style.RESET_ALL}")
        
        # Task 2 details
        print(f"\n{Fore.BLUE}Task {format_task_id(task2)}: {task2.get('title')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Status: {task2.get('status', 'unknown')}, Priority: {task2.get('priority', 'unknown')}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Description: {task2.get('description', 'No description')}{Style.RESET_ALL}")
        
        # Show diff of descriptions
        print(f"\n{Fore.CYAN}Description Differences:{Style.RESET_ALL}")
        desc1 = task1.get('description', '')
        desc2 = task2.get('description', '')
        diff = list(difflib.ndiff(desc1.splitlines(), desc2.splitlines()))
        # Only show diff if there are actually differences
        if any(line.startswith('+ ') or line.startswith('- ') for line in diff):
            for line in diff:
                if line.startswith('+ '):
                    print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
                elif line.startswith('- '):
                    print(f"{Fore.RED}{line}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.WHITE}{line}{Style.RESET_ALL}")
        else:
            print(f"{Fore.WHITE}No significant differences in description{Style.RESET_ALL}")
        
        # Add separator between task pairs
        print("\n" + "=" * 100 + "\n")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='List task similarities above a specified threshold')
    parser.add_argument('--threshold', type=float, default=0.70, 
                        help='Similarity threshold (0.0-1.0) for reporting (default: 0.70)')
    parser.add_argument('--file', type=str, default='tasks/tasks.json',
                        help='Path to the tasks.json file')
    parser.add_argument('--include-done', action='store_true',
                        help='Include done tasks in the analysis')
    parser.add_argument('--format', type=str, default='detailed', choices=['basic', 'detailed'],
                        help='Output format: basic or detailed (default: detailed)')
    
    args = parser.parse_args()
    
    # Validate threshold
    if args.threshold < 0 or args.threshold > 1:
        print(f"{Fore.RED}Error: Threshold must be between 0.0 and 1.0{Style.RESET_ALL}")
        sys.exit(1)
    
    # Load tasks
    tasks = load_tasks(args.file)
    print(f"{Fore.GREEN}Loaded {len(tasks)} tasks from {args.file}{Style.RESET_ALL}")
    
    # Get subtasks
    subtasks = get_all_subtasks(tasks)
    print(f"{Fore.GREEN}Found {len(subtasks)} subtasks{Style.RESET_ALL}")
    
    # Fields to compare (keeping it simple for this version)
    fields = ['title', 'description', 'details']
    
    # Find similar tasks
    similar_pairs = find_similar_tasks(tasks, subtasks, args.threshold, args.include_done, fields)
    
    # Print report based on format
    if args.format == 'basic':
        print_basic_report(similar_pairs)
    else:  # detailed
        print_detailed_report(similar_pairs)
    
    # Summary
    print(f"\n{Fore.CYAN}Summary:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Analyzed {len(tasks)} top-level tasks and {len(subtasks)} subtasks{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Found {len(similar_pairs)} task pairs with similarity above {args.threshold:.2f}{Style.RESET_ALL}")
    
    if similar_pairs:
        similarity_ranges = {
            (0.95, 1.0): "Very High (>95%)",
            (0.85, 0.95): "High (85-95%)",
            (0.75, 0.85): "Medium (75-85%)",
            (0.0, 0.75): "Low (<75%)"
        }
        
        # Count tasks in each similarity range
        counts = {range_name: 0 for range_name in [r[1] for r in similarity_ranges.items()]}
        for _, _, similarity in similar_pairs:
            for (lower, upper), range_name in similarity_ranges.items():
                if lower <= similarity < upper or (upper == 1.0 and similarity == 1.0):
                    counts[range_name] += 1
                    break
        
        # Print breakdown
        print(f"\n{Fore.CYAN}Similarity breakdown:{Style.RESET_ALL}")
        for range_name, count in counts.items():
            if count > 0:
                print(f"{Fore.WHITE}{range_name}: {count} pairs{Style.RESET_ALL}")

if __name__ == "__main__":
    main() 