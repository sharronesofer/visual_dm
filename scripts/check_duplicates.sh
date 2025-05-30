#!/bin/bash

# Script to check for duplicate files after reorganization
# This helps identify and report files that may have been copied to multiple folders

set -e  # Exit on any error

MODULES_DIR="/Users/Sharrone/Visual_DM/vdm/Assets/Scripts/Modules"
DUPLICATE_LOG="/Users/Sharrone/Visual_DM/duplicate_files_log.txt"

echo "Checking for duplicate files across module folders..."
echo "Duplicate Files Report - $(date)" > "$DUPLICATE_LOG"

# Create a temporary file to store all found files
tmp_file=$(mktemp)

# Find all CS files in the modules directory and save their basenames to tmp file
find "$MODULES_DIR" -type f -name "*.cs" | xargs -I{} basename {} | sort > "$tmp_file"

# Check for duplicates
echo "Possible duplicates (files with same name in different directories):" >> "$DUPLICATE_LOG"
cat "$tmp_file" | uniq -d | while read filename; do
  echo "File: $filename found in:" >> "$DUPLICATE_LOG"
  find "$MODULES_DIR" -name "$filename" | while read path; do
    echo "  - $path" >> "$DUPLICATE_LOG"
  done
  echo "" >> "$DUPLICATE_LOG"
done

# Count files per module
echo "Files per module:" >> "$DUPLICATE_LOG"
echo "----------------" >> "$DUPLICATE_LOG"

for dir in "$MODULES_DIR"/*; do
  if [ -d "$dir" ]; then
    module_name=$(basename "$dir")
    file_count=$(find "$dir" -type f -name "*.cs" | wc -l)
    echo "$module_name: $file_count files" >> "$DUPLICATE_LOG"
  fi
done

# Check for empty modules
echo "" >> "$DUPLICATE_LOG"
echo "Empty modules (no CS files):" >> "$DUPLICATE_LOG"
echo "-------------------------" >> "$DUPLICATE_LOG"

for dir in "$MODULES_DIR"/*; do
  if [ -d "$dir" ]; then
    module_name=$(basename "$dir")
    file_count=$(find "$dir" -type f -name "*.cs" | wc -l)
    if [ "$file_count" -eq 0 ]; then
      echo "$module_name" >> "$DUPLICATE_LOG"
    fi
  fi
done

# Check for potential namespace issues
echo "" >> "$DUPLICATE_LOG"
echo "Files with potential namespace issues:" >> "$DUPLICATE_LOG"
echo "---------------------------------" >> "$DUPLICATE_LOG"

for dir in "$MODULES_DIR"/*; do
  if [ -d "$dir" ]; then
    module_name=$(basename "$dir")
    find "$dir" -type f -name "*.cs" | xargs grep -l "namespace" | while read file; do
      if ! grep -q "namespace.*${module_name}" "$file"; then
        echo "$(basename "$file") in $module_name has namespace mismatch" >> "$DUPLICATE_LOG"
      fi
    done
  fi
done

# Delete temp file
rm "$tmp_file"

echo "Check complete. Results saved to $DUPLICATE_LOG"
echo "Next steps:"
echo "1. Review the duplicate files and decide which to keep"
echo "2. Update namespace declarations if needed"
echo "3. Make backup before actually deleting any files" 