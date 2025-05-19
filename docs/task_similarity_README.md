# Task Similarity Tools

Tools for identifying duplicate or similar tasks in Task Master projects.

## Overview

This package provides two tools:

1. **Task Similarity Report** (`task_similarity_report.py`): A Python script that analyzes your tasks and lists pairs with similarity above a specified threshold.
   
2. **Check Similar Tasks** (`check_similar_tasks.sh`): A shell script wrapper around the report tool that simplifies running regular checks and saves logs.

These tools help maintain a clean task list by identifying potential duplicates based on fuzzy text matching.

## Installation

### Prerequisites

- Python 3.6+
- Required Python packages:
  - rapidfuzz
  - colorama

You can install the required packages with:

```bash
pip install rapidfuzz colorama
```

The shell script will attempt to install these packages automatically if they're not found.

## Usage

### Task Similarity Report

The main Python script provides detailed similarity analysis:

```bash
python task_similarity_report.py [options]
```

Options:
- `--threshold=NUM`: Similarity threshold (0.0-1.0) for reporting (default: 0.70)
- `--file=PATH`: Path to the tasks.json file (default: tasks/tasks.json)
- `--include-done`: Include completed tasks in the analysis (default: exclude done tasks)
- `--format=FORMAT`: Output format: basic, detailed (default: detailed)

Example:
```bash
python task_similarity_report.py --threshold=0.75 --format=basic
```

### Check Similar Tasks Shell Script

For simplified usage, especially for regular checks, use the shell script:

```bash
./check_similar_tasks.sh [options]
```

Options:
- `--threshold=NUM`: Set similarity threshold (0.0-1.0) (default: 0.75)
- `--format=TYPE`: Set output format (basic, detailed) (default: basic)
- `--include-done`: Include done tasks in the analysis
- `--file=PATH`: Path to tasks.json file (default: tasks/tasks.json)
- `--help`: Show help text

The script will save the results to a timestamped log file.

Example:
```bash
./check_similar_tasks.sh --threshold=0.80 --include-done
```

## Output Formats

### Basic Format

Shows a simple list of similar task pairs with their similarity score and titles:

```
Similarity: 0.81
Task 659: Task #659: Implement Core Nemesis/Rival System Data Models and Relationships
Task 660: Task #660: Implement Core Nemesis/Rival System Data Models and Relationships
--------------------------------------------------------------------------------
```

### Detailed Format

Shows comprehensive information about similar tasks, including descriptions and a diff view showing the exact differences:

```
Similarity Pair 1: 0.81
Task 659: Task #659: Implement Core Nemesis/Rival System Data Models and Relationships
Status: pending, Priority: high
Description: Design and implement...

Task 660: Task #660: Implement Core Nemesis/Rival System Data Models and Relationships
Status: pending, Priority: high
Description: Design and implement...

Description Differences:
- Original text line
+ Modified text line
```

## How It Works

The tool uses fuzzy string matching algorithms to compare task fields with different weights:

- Title: 2.0x weight (most important)
- Description: 1.5x weight (important)
- Details: 1.0x weight (standard)
- Test Strategy: 0.5x weight (less important)

The similarity score is calculated as a weighted average of the field comparisons, normalized to a 0.0-1.0 scale.

## Recommended Workflow

1. Run weekly similarity checks to catch potential duplicates:
   ```bash
   ./check_similar_tasks.sh
   ```

2. Examine any highly similar task pairs (>0.80 similarity):
   ```bash
   python task_similarity_report.py --threshold=0.80 --format=detailed
   ```

3. For tasks that are truly duplicates, consider:
   - Merging them (combining information from both)
   - Removing one and keeping the other
   - Converting them to subtasks of a parent task

4. For tasks that are similar but distinct, consider:
   - Revising titles/descriptions to clarify differences
   - Adding cross-references between related tasks
   - Creating a parent task with subtasks for related work 