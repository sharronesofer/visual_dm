#!/usr/bin/env python3
"""
Task Similarity Analyzer

This script uses fuzzy logic to identify duplicate or near-duplicate tasks in a Task Master tasks.json file.
It compares task titles, descriptions, and details using string similarity algorithms and reports potential duplicates.

Usage:
    python task_similarity.py [--threshold=0.85] [--file=tasks/tasks.json]

Options:
    --threshold     Similarity threshold (0.0-1.0) for considering tasks as duplicates (default: 0.85)
    --file          Path to the tasks.json file (default: tasks/tasks.json)
    --include-done  Include done tasks in the analysis (default: exclude done tasks)
    --fields        Comma-separated list of fields to compare (default: title,description,details)
    --output        Output format: terminal, json, or csv (default: terminal)
"""

import argparse
import json
import sys
from collections import defaultdict
from typing import Dict, List, Tuple, Set
import difflib
from rapidfuzz import fuzz
import pandas as pd
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
    for i, task1 in enumerate(all_items):
        for task2 in all_items[i+1:]:
            similarity = calculate_similarity(task1, task2, fields, weights)
            if similarity >= threshold:
                similar_pairs.append((task1, task2, similarity))
    
    # Sort by similarity (descending)
    similar_pairs.sort(key=lambda x: x[2], reverse=True)
    return similar_pairs

def format_task_id(task: Dict) -> str:
    """Format the task ID for display, including parent info for subtasks."""
    if 'parent_id' in task:
        return f"{task['parent_id']}.{task['id']} (subtask)"
    return str(task['id'])

def print_results_terminal(similar_pairs: List[Tuple[Dict, Dict, float]]) -> None:
    """Print results to terminal in a readable format with color highlighting."""
    if not similar_pairs:
        print(f"{Fore.GREEN}No similar tasks found above the threshold.{Style.RESET_ALL}")
        return
    
    print(f"{Fore.CYAN}Found {len(similar_pairs)} potential duplicate task pairs:{Style.RESET_ALL}\n")
    
    for task1, task2, similarity in similar_pairs:
        similarity_color = Fore.RED if similarity > 0.95 else (Fore.YELLOW if similarity > 0.9 else Fore.WHITE)
        
        print(f"{similarity_color}Similarity: {similarity:.2f}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Task {format_task_id(task1)}{Style.RESET_ALL}: {Fore.WHITE}{task1.get('title')}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}Task {format_task_id(task2)}{Style.RESET_ALL}: {Fore.WHITE}{task2.get('title')}{Style.RESET_ALL}")
        
        # Show detailed differences for high similarity matches
        if similarity > 0.9:
            print(f"{Fore.CYAN}Description Diff:{Style.RESET_ALL}")
            desc1 = task1.get('description', '')
            desc2 = task2.get('description', '')
            diff = difflib.ndiff(desc1.splitlines(), desc2.splitlines())
            print('\n'.join(diff))
        
        print("-" * 80)

def export_results_json(similar_pairs: List[Tuple[Dict, Dict, float]], output_file: str = 'task_similarity_results.json') -> None:
    """Export results to a JSON file."""
    results = []
    
    for task1, task2, similarity in similar_pairs:
        result = {
            'similarity': similarity,
            'task1': {
                'id': format_task_id(task1),
                'title': task1.get('title'),
                'status': task1.get('status'),
                'description': task1.get('description', '')
            },
            'task2': {
                'id': format_task_id(task2),
                'title': task2.get('title'),
                'status': task2.get('status'),
                'description': task2.get('description', '')
            }
        }
        results.append(result)
    
    with open(output_file, 'w') as f:
        json.dump({'duplicate_candidates': results}, f, indent=2)
    
    print(f"Results exported to {output_file}")

def export_results_csv(similar_pairs: List[Tuple[Dict, Dict, float]], output_file: str = 'task_similarity_results.csv') -> None:
    """Export results to a CSV file."""
    data = []
    
    for task1, task2, similarity in similar_pairs:
        data.append({
            'similarity': similarity,
            'task1_id': format_task_id(task1),
            'task1_title': task1.get('title'),
            'task1_status': task1.get('status'),
            'task2_id': format_task_id(task2),
            'task2_title': task2.get('title'),
            'task2_status': task2.get('status')
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"Results exported to {output_file}")

def group_similar_tasks(similar_pairs: List[Tuple[Dict, Dict, float]]) -> List[List[Dict]]:
    """Group tasks into clusters of similar tasks."""
    # Create a graph of similar tasks
    graph = defaultdict(set)
    task_map = {}
    
    for task1, task2, _ in similar_pairs:
        task1_id = format_task_id(task1)
        task2_id = format_task_id(task2)
        
        task_map[task1_id] = task1
        task_map[task2_id] = task2
        
        graph[task1_id].add(task2_id)
        graph[task2_id].add(task1_id)
    
    # Find connected components (clusters)
    clusters = []
    visited = set()
    
    def dfs(node, cluster):
        visited.add(node)
        cluster.append(task_map[node])
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor, cluster)
    
    for node in graph:
        if node not in visited:
            cluster = []
            dfs(node, cluster)
            if len(cluster) > 1:  # Only include clusters with multiple tasks
                clusters.append(cluster)
    
    return clusters

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Find duplicate or similar tasks in tasks.json')
    parser.add_argument('--threshold', type=float, default=0.85, 
                        help='Similarity threshold (0.0-1.0) for considering tasks as duplicates')
    parser.add_argument('--file', type=str, default='tasks/tasks.json',
                        help='Path to the tasks.json file')
    parser.add_argument('--include-done', action='store_true',
                        help='Include done tasks in the analysis')
    parser.add_argument('--fields', type=str, default='title,description,details',
                        help='Comma-separated list of fields to compare')
    parser.add_argument('--output', type=str, default='terminal', choices=['terminal', 'json', 'csv'],
                        help='Output format: terminal, json, or csv')
    parser.add_argument('--cluster', action='store_true',
                        help='Group similar tasks into clusters')
    
    args = parser.parse_args()
    
    # Load tasks
    tasks = load_tasks(args.file)
    
    # Get subtasks
    subtasks = get_all_subtasks(tasks)
    
    # Parse fields to compare
    fields = [field.strip() for field in args.fields.split(',')]
    
    # Find similar tasks
    similar_pairs = find_similar_tasks(tasks, subtasks, args.threshold, args.include_done, fields)
    
    # Output results
    if args.output == 'terminal':
        print_results_terminal(similar_pairs)
        
        # Show clusters if requested
        if args.cluster and similar_pairs:
            clusters = group_similar_tasks(similar_pairs)
            print(f"\n{Fore.CYAN}Found {len(clusters)} clusters of similar tasks:{Style.RESET_ALL}\n")
            
            for i, cluster in enumerate(clusters, 1):
                print(f"{Fore.YELLOW}Cluster {i} ({len(cluster)} tasks):{Style.RESET_ALL}")
                for task in cluster:
                    print(f"  {Fore.BLUE}Task {format_task_id(task)}{Style.RESET_ALL}: {task.get('title')}")
                print()
            
    elif args.output == 'json':
        export_results_json(similar_pairs)
    elif args.output == 'csv':
        export_results_csv(similar_pairs)

if __name__ == "__main__":
    main() 