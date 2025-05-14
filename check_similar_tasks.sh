#!/bin/bash
# Script to check for similar tasks in the Task Master tasks.json file

# Default values
THRESHOLD=0.75
FORMAT="basic"
INCLUDE_DONE=false
TASKS_FILE="tasks/tasks.json"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --threshold=*)
      THRESHOLD="${1#*=}"
      shift
      ;;
    --format=*)
      FORMAT="${1#*=}"
      shift
      ;;
    --include-done)
      INCLUDE_DONE=true
      shift
      ;;
    --file=*)
      TASKS_FILE="${1#*=}"
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --threshold=NUM   Set similarity threshold (0.0-1.0) [default: 0.75]"
      echo "  --format=TYPE     Set output format (basic, detailed) [default: basic]"
      echo "  --include-done    Include done tasks in the analysis"
      echo "  --file=PATH       Path to tasks.json file [default: tasks/tasks.json]"
      echo "  --help            Show this help text"
      exit 0
      ;;
    *)
      echo "Unknown parameter: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Check if task_similarity_report.py exists
if [ ! -f "task_similarity_report.py" ]; then
  echo "Error: task_similarity_report.py not found. Please ensure it exists in the current directory."
  exit 1
fi

# Check if required Python packages are installed
python -c "import rapidfuzz, colorama" >/dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "Installing required Python packages..."
  pip install rapidfuzz colorama
fi

# Print header
echo "Running Task Similarity Check"
echo "=============================="
echo "Threshold: $THRESHOLD"
echo "Format: $FORMAT"
echo "Include done tasks: $INCLUDE_DONE"
echo "Tasks file: $TASKS_FILE"
echo "=============================="
echo

# Build command
CMD="python task_similarity_report.py --threshold=$THRESHOLD --format=$FORMAT --file=$TASKS_FILE"
if [ "$INCLUDE_DONE" = true ]; then
  CMD="$CMD --include-done"
fi

# Run the analysis
echo "Analysis started at $(date)"
$CMD

# Add result to log file
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="task_similarity_$TIMESTAMP.log"

echo "Saving log to $LOG_FILE"
{
  echo "Task Similarity Analysis - $TIMESTAMP"
  echo "=============================="
  echo "Threshold: $THRESHOLD"
  echo "Format: $FORMAT"
  echo "Include done tasks: $INCLUDE_DONE"
  echo "Tasks file: $TASKS_FILE"
  echo "=============================="
  echo
  $CMD
} > "$LOG_FILE"

echo "Analysis complete. Check $LOG_FILE for details." 