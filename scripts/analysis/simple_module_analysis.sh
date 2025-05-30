#!/bin/bash

# Simple script to analyze module structure and list files in each module
# This is a more reliable version that doesn't try to parse code

set -e  # Exit on any error

MODULES_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/Modules"
OUTPUT_DIR="/Users/Sharrone/Visual_DM/module_analysis"
mkdir -p "$OUTPUT_DIR"

# Output file for the report
REPORT_FILE="$OUTPUT_DIR/module_structure_report.md"

echo "# Module Structure Analysis" > "$REPORT_FILE"
echo "=========================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "Generated on $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Module pairs to examine
declare -a MODULE_PAIRS=(
  "Characters:NPC:NPCs"
  "Faction:Factions"
  "Quest:Quests"
  "Time:TimeSystem"
  "World:WorldGen:WorldState"
)

# Function to analyze a module
analyze_module() {
  local module_name=$1
  local module_dir="$MODULES_DIR/$module_name"
  
  if [ ! -d "$module_dir" ]; then
    echo "Module $module_name not found, skipping"
    return
  fi
  
  echo "## Module: $module_name" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"
  
  # Count files
  file_count=$(find "$module_dir" -type f -name "*.cs" | wc -l | tr -d ' ')
  echo "Total C# files: $file_count" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"
  
  # List files
  echo "### Files in module:" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"
  echo "```" >> "$REPORT_FILE"
  find "$module_dir" -type f -name "*.cs" -exec basename {} \; | sort >> "$REPORT_FILE"
  echo "```" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"
  
  # Try to get namespaces
  echo "### Namespaces used:" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"
  echo "```" >> "$REPORT_FILE"
  find "$module_dir" -type f -name "*.cs" -exec grep -l "namespace" {} \; -exec grep -m 1 "namespace" {} \; | sort | uniq >> "$REPORT_FILE"
  echo "```" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"
}

# Function to find common files between modules
find_common_files() {
  local modules=("$@")
  local count=${#modules[@]}
  
  # Skip if we have less than 2 modules
  if [ $count -lt 2 ]; then
    return
  fi
  
  echo "## Common Files Analysis: ${modules[*]}" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"
  
  local file_lists=()
  local module_file_counts=()
  
  # Get list of files for each module
  for ((i=0; i<$count; i++)); do
    module="${modules[$i]}"
    module_dir="$MODULES_DIR/$module"
    
    if [ ! -d "$module_dir" ]; then
      echo "Module $module not found, skipping comparison"
      return
    fi
    
    # Get file list and store it in a temporary file
    tmp_file=$(mktemp)
    find "$module_dir" -type f -name "*.cs" -exec basename {} \; | sort > "$tmp_file"
    file_lists+=("$tmp_file")
    
    # Count files
    file_count=$(wc -l < "$tmp_file" | tr -d ' ')
    module_file_counts+=("$file_count")
    
    echo "- $module: $file_count files" >> "$REPORT_FILE"
  done
  
  echo "" >> "$REPORT_FILE"
  echo "### Files with same name across modules:" >> "$REPORT_FILE"
  echo "" >> "$REPORT_FILE"
  
  # For two modules, we can use comm
  if [ $count -eq 2 ]; then
    echo "```" >> "$REPORT_FILE"
    comm -12 "${file_lists[0]}" "${file_lists[1]}" >> "$REPORT_FILE"
    echo "```" >> "$REPORT_FILE"
  else
    # For more than two modules, we need a different approach
    echo "```" >> "$REPORT_FILE"
    # Start with the first module's files
    cat "${file_lists[0]}" > /tmp/common_files.txt
    
    # Intersect with each subsequent module
    for ((i=1; i<$count; i++)); do
      comm -12 /tmp/common_files.txt "${file_lists[$i]}" > /tmp/new_common_files.txt
      mv /tmp/new_common_files.txt /tmp/common_files.txt
    done
    
    cat /tmp/common_files.txt >> "$REPORT_FILE"
    echo "```" >> "$REPORT_FILE"
  fi
  
  echo "" >> "$REPORT_FILE"
  
  # Clean up temporary files
  for file in "${file_lists[@]}"; do
    rm -f "$file"
  done
  rm -f /tmp/common_files.txt
}

# Generate a full list of modules
echo "# Module List" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "| Module | C# Files |" >> "$REPORT_FILE"
echo "|--------|----------|" >> "$REPORT_FILE"

for module_dir in $(find "$MODULES_DIR" -maxdepth 1 -mindepth 1 -type d | sort); do
  module_name=$(basename "$module_dir")
  file_count=$(find "$module_dir" -type f -name "*.cs" | wc -l | tr -d ' ')
  echo "| $module_name | $file_count |" >> "$REPORT_FILE"
done

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Analyze each module individually
for module_dir in $(find "$MODULES_DIR" -maxdepth 1 -mindepth 1 -type d | sort); do
  module_name=$(basename "$module_dir")
  analyze_module "$module_name"
done

# Analyze module pairs
echo "# Module Comparison" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for pair in "${MODULE_PAIRS[@]}"; do
  # Split the pair into an array
  IFS=':' read -ra modules <<< "$pair"
  find_common_files "${modules[@]}"
done

echo "Analysis complete! Report saved to $REPORT_FILE" 