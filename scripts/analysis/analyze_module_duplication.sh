#!/bin/bash

# Script to analyze potential duplicate functionality between module pairs
# This script examines file content similarities and outputs a report for each pair

set -e  # Exit on any error

MODULES_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/Modules"
OUTPUT_DIR="/Users/Sharrone/Visual_DM/module_analysis"
mkdir -p "$OUTPUT_DIR"

# List of module pairs to compare for duplication
declare -a MODULE_PAIRS=(
  "Characters:NPC"
  "Characters:NPCs"
  "NPC:NPCs"
  "Faction:Factions"
  "Quest:Quests"
  "Time:TimeSystem"
  "World:WorldGen"
  "World:WorldState"
  "WorldGen:WorldState"
)

echo "Module Duplication Analysis" > "$OUTPUT_DIR/duplication_report.md"
echo "=========================" >> "$OUTPUT_DIR/duplication_report.md"
echo "" >> "$OUTPUT_DIR/duplication_report.md"
echo "Generated on $(date)" >> "$OUTPUT_DIR/duplication_report.md"
echo "" >> "$OUTPUT_DIR/duplication_report.md"

for pair in "${MODULE_PAIRS[@]}"; do
  # Split the pair
  IFS=':' read -r module1 module2 <<< "$pair"
  
  echo "Analyzing $module1 vs $module2..."
  echo "## $module1 vs $module2" >> "$OUTPUT_DIR/duplication_report.md"
  echo "" >> "$OUTPUT_DIR/duplication_report.md"
  
  # Check if modules exist
  if [ ! -d "$MODULES_DIR/$module1" ] || [ ! -d "$MODULES_DIR/$module2" ]; then
    echo "One or both modules don't exist. Skipping."
    echo "One or both modules don't exist. Skipping." >> "$OUTPUT_DIR/duplication_report.md"
    echo "" >> "$OUTPUT_DIR/duplication_report.md"
    continue
  fi
  
  # Count files in each module
  files1=$(find "$MODULES_DIR/$module1" -type f -name "*.cs" | wc -l | tr -d ' ')
  files2=$(find "$MODULES_DIR/$module2" -type f -name "*.cs" | wc -l | tr -d ' ')
  
  echo "- $module1: $files1 C# files" >> "$OUTPUT_DIR/duplication_report.md"
  echo "- $module2: $files2 C# files" >> "$OUTPUT_DIR/duplication_report.md"
  echo "" >> "$OUTPUT_DIR/duplication_report.md"
  
  # List of similar file names (ignoring case)
  echo "### Similar file names (potential duplicates)" >> "$OUTPUT_DIR/duplication_report.md"
  echo "" >> "$OUTPUT_DIR/duplication_report.md"
  
  # Get file bases without paths or extensions
  files1_base=$(find "$MODULES_DIR/$module1" -type f -name "*.cs" -exec basename {} .cs \; | sort)
  files2_base=$(find "$MODULES_DIR/$module2" -type f -name "*.cs" -exec basename {} .cs \; | sort)
  
  # Create temporary files
  temp_dir=$(mktemp -d)
  echo "$files1_base" > "$temp_dir/files1.txt"
  echo "$files2_base" > "$temp_dir/files2.txt"
  
  # Find common file names
  similar_files=$(comm -12 <(tr '[:upper:]' '[:lower:]' < "$temp_dir/files1.txt" | sort) <(tr '[:upper:]' '[:lower:]' < "$temp_dir/files2.txt" | sort))
  
  if [ -z "$similar_files" ]; then
    echo "No files with similar names found." >> "$OUTPUT_DIR/duplication_report.md"
  else
    echo "```" >> "$OUTPUT_DIR/duplication_report.md"
    echo "$similar_files" >> "$OUTPUT_DIR/duplication_report.md"
    echo "```" >> "$OUTPUT_DIR/duplication_report.md"
    
    # For each similar file, create a detailed comparison
    echo "" >> "$OUTPUT_DIR/duplication_report.md"
    echo "### Detailed analysis of similar files" >> "$OUTPUT_DIR/duplication_report.md"
    echo "" >> "$OUTPUT_DIR/duplication_report.md"
    
    while IFS= read -r base_name; do
      if [ -z "$base_name" ]; then continue; fi
      
      # Find the actual filenames with case sensitivity
      file1=$(find "$MODULES_DIR/$module1" -type f -iname "${base_name}.cs" | head -1)
      file2=$(find "$MODULES_DIR/$module2" -type f -iname "${base_name}.cs" | head -1)
      
      if [ -f "$file1" ] && [ -f "$file2" ]; then
        echo "#### ${base_name}.cs" >> "$OUTPUT_DIR/duplication_report.md"
        echo "" >> "$OUTPUT_DIR/duplication_report.md"
        
        # Check if they are identical
        if cmp -s "$file1" "$file2"; then
          echo "**Files are identical**" >> "$OUTPUT_DIR/duplication_report.md"
        else
          # Count lines in each file
          lines1=$(wc -l < "$file1" | tr -d ' ')
          lines2=$(wc -l < "$file2" | tr -d ' ')
          
          # Check overlap percentage (using diff)
          total_lines=$((lines1 + lines2))
          diff_lines=$(diff -y --suppress-common-lines "$file1" "$file2" | wc -l)
          common_lines=$((total_lines - diff_lines))
          similarity=$(awk "BEGIN {print int(($common_lines * 200) / ($total_lines))}") # Times 100 for percentage, and then double because our diff calculation is an approximation
          
          if [ $similarity -gt 100 ]; then
            similarity=100
          fi
          
          echo "- $module1 version: $lines1 lines" >> "$OUTPUT_DIR/duplication_report.md"
          echo "- $module2 version: $lines2 lines" >> "$OUTPUT_DIR/duplication_report.md"
          echo "- Estimated similarity: ~$similarity%" >> "$OUTPUT_DIR/duplication_report.md"
          
          # Extract class definitions as a clue to functionality
          echo "" >> "$OUTPUT_DIR/duplication_report.md"
          echo "##### $module1 class definition:" >> "$OUTPUT_DIR/duplication_report.md"
          echo "```csharp" >> "$OUTPUT_DIR/duplication_report.md"
          grep -E "class |interface |struct " "$file1" | head -3 >> "$OUTPUT_DIR/duplication_report.md"
          echo "```" >> "$OUTPUT_DIR/duplication_report.md"
          
          echo "" >> "$OUTPUT_DIR/duplication_report.md"
          echo "##### $module2 class definition:" >> "$OUTPUT_DIR/duplication_report.md"
          echo "```csharp" >> "$OUTPUT_DIR/duplication_report.md"
          grep -E "class |interface |struct " "$file2" | head -3 >> "$OUTPUT_DIR/duplication_report.md"
          echo "```" >> "$OUTPUT_DIR/duplication_report.md"
          
          # Unique public methods in module1
          echo "" >> "$OUTPUT_DIR/duplication_report.md"
          echo "##### Methods unique to $module1:" >> "$OUTPUT_DIR/duplication_report.md"
          echo "```csharp" >> "$OUTPUT_DIR/duplication_report.md"
          grep -E "public [a-zA-Z0-9_<>]+ [a-zA-Z0-9_]+" "$file1" | grep -v "get;" | grep -v "set;" | grep -v "=>" | head -5 >> "$OUTPUT_DIR/duplication_report.md"
          echo "```" >> "$OUTPUT_DIR/duplication_report.md"
          
          # Unique public methods in module2
          echo "" >> "$OUTPUT_DIR/duplication_report.md"
          echo "##### Methods unique to $module2:" >> "$OUTPUT_DIR/duplication_report.md"
          echo "```csharp" >> "$OUTPUT_DIR/duplication_report.md"
          grep -E "public [a-zA-Z0-9_<>]+ [a-zA-Z0-9_]+" "$file2" | grep -v "get;" | grep -v "set;" | grep -v "=>" | head -5 >> "$OUTPUT_DIR/duplication_report.md"
          echo "```" >> "$OUTPUT_DIR/duplication_report.md"
        fi
        
        echo "" >> "$OUTPUT_DIR/duplication_report.md"
      fi
    done <<< "$similar_files"
  fi
  
  # Also check for files that have different names but potentially similar content
  echo "### Functionality overlap analysis" >> "$OUTPUT_DIR/duplication_report.md"
  echo "" >> "$OUTPUT_DIR/duplication_report.md"
  
  # Extract common C# terms/patterns that might indicate similar functionality
  module1_functions=$(find "$MODULES_DIR/$module1" -type f -name "*.cs" -exec grep -E "public [a-zA-Z0-9_<>]+ [a-zA-Z0-9_]+" {} \; | grep -v "get;" | grep -v "set;" | grep -v "=>" | sort | uniq)
  module2_functions=$(find "$MODULES_DIR/$module2" -type f -name "*.cs" -exec grep -E "public [a-zA-Z0-9_<>]+ [a-zA-Z0-9_]+" {} \; | grep -v "get;" | grep -v "set;" | grep -v "=>" | sort | uniq)
  
  # Extract method names only (approximate)
  module1_method_names=$(echo "$module1_functions" | sed -E 's/.*public [a-zA-Z0-9_<>]+ ([a-zA-Z0-9_]+).*/\1/' | sort | uniq)
  module2_method_names=$(echo "$module2_functions" | sed -E 's/.*public [a-zA-Z0-9_<>]+ ([a-zA-Z0-9_]+).*/\1/' | sort | uniq)
  
  # Create temporary files for method names
  echo "$module1_method_names" > "$temp_dir/methods1.txt"
  echo "$module2_method_names" > "$temp_dir/methods2.txt"
  
  # Find common method names
  common_methods=$(comm -12 <(sort "$temp_dir/methods1.txt") <(sort "$temp_dir/methods2.txt"))
  
  echo "#### Common method names (potential functional overlap)" >> "$OUTPUT_DIR/duplication_report.md"
  echo "" >> "$OUTPUT_DIR/duplication_report.md"
  
  if [ -z "$common_methods" ]; then
    echo "No common method names found." >> "$OUTPUT_DIR/duplication_report.md"
  else
    echo "```" >> "$OUTPUT_DIR/duplication_report.md"
    echo "$common_methods" >> "$OUTPUT_DIR/duplication_report.md"
    echo "```" >> "$OUTPUT_DIR/duplication_report.md"
  fi
  
  echo "" >> "$OUTPUT_DIR/duplication_report.md"
  echo "---" >> "$OUTPUT_DIR/duplication_report.md"
  echo "" >> "$OUTPUT_DIR/duplication_report.md"
  
  # Clean up temp files
  rm -rf "$temp_dir"
done

# General module statistics
echo "## General Module Statistics" >> "$OUTPUT_DIR/duplication_report.md"
echo "" >> "$OUTPUT_DIR/duplication_report.md"

echo "| Module | Files | Lines of Code |" >> "$OUTPUT_DIR/duplication_report.md"
echo "|--------|-------|--------------|" >> "$OUTPUT_DIR/duplication_report.md"

for module in $(find "$MODULES_DIR" -maxdepth 1 -mindepth 1 -type d | sort); do
  module_name=$(basename "$module")
  files=$(find "$module" -type f -name "*.cs" | wc -l | tr -d ' ')
  
  if [ "$files" -gt 0 ]; then
    lines=$(find "$module" -type f -name "*.cs" -exec wc -l {} \; | awk '{sum += $1} END {print sum}')
  else
    lines=0
  fi
  
  echo "| $module_name | $files | $lines |" >> "$OUTPUT_DIR/duplication_report.md"
done

echo "" >> "$OUTPUT_DIR/duplication_report.md"
echo "## Recommendations" >> "$OUTPUT_DIR/duplication_report.md"
echo "" >> "$OUTPUT_DIR/duplication_report.md"
echo "Based on the analysis above, here are the recommended consolidation actions:" >> "$OUTPUT_DIR/duplication_report.md"
echo "" >> "$OUTPUT_DIR/duplication_report.md"
echo "1. For files that are identical (100% similarity), keep only one copy in the more appropriate module." >> "$OUTPUT_DIR/duplication_report.md"
echo "2. For files with high similarity (>70%), merge functionality into one consolidated version." >> "$OUTPUT_DIR/duplication_report.md"
echo "3. For files with common method names but different implementations, review each to determine the better implementation." >> "$OUTPUT_DIR/duplication_report.md"
echo "4. Consider standardizing on singular module names (e.g., 'Faction' instead of 'Factions')." >> "$OUTPUT_DIR/duplication_report.md"
echo "" >> "$OUTPUT_DIR/duplication_report.md"

echo "Analysis complete! Report saved to $OUTPUT_DIR/duplication_report.md" 