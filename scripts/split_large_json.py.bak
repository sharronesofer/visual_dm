#!/usr/bin/env python3
"""
Script to split large JSON line-delimited files into smaller chunks.
Each line in the source file is treated as a separate JSON object.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from contextlib import contextmanager


@contextmanager
def safe_open_write(path):
    """Safely open a file for writing using a context manager."""
    try:
        f = open(path, 'w')
        yield f
    finally:
        f.close()


def split_json_file(filename, output_dir, lines_per_file=100000):
    """
    Split a line-delimited JSON file into multiple smaller files.
    
    Args:
        filename: Path to the large JSON file
        output_dir: Directory where split files will be saved
        lines_per_file: Number of lines per output file
    """
    input_path = Path(filename)
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get base name for output files
    base_name = input_path.stem
    
    # Count total lines in file
    with open(input_path, 'r') as f:
        line_count = sum(1 for _ in f)
    
    print(f"Splitting {filename} with {line_count:,} lines into chunks of {lines_per_file:,} lines each")
    
    # Split the file
    with open(input_path, 'r') as input_file:
        file_number = 1
        line_number = 1
        
        output_file_path = output_path / f"{base_name}_part{file_number:03d}.json"
        print(f"Creating {base_name}_part{file_number:03d}.json")
        
        with safe_open_write(output_file_path) as current_output_file:
            for line in input_file:
                # Validate each line is valid JSON
                try:
                    json.loads(line.strip())
                    current_output_file.write(line)
                except json.JSONDecodeError:
                    print(f"Warning: Skipping invalid JSON at line {line_number}")
                
                line_number += 1
                
                # If we've reached the max lines per file, start a new file
                if (line_number - 1) % lines_per_file == 0 and line_number > 1:
                    # Close current file (handled by context manager)
                    # Start a new file
                    file_number += 1
                    output_file_path = output_path / f"{base_name}_part{file_number:03d}.json"
                    print(f"Creating {base_name}_part{file_number:03d}.json")
                    
                    # Need to close the current file and open a new one
                    # This breaks out of the current context manager and creates a new one
                    break
            
        # Continue with remaining lines if there are any
        if line_number <= line_count:
            # Continue processing the remaining lines
            remaining_lines = []
            for remaining_line in input_file:
                remaining_lines.append(remaining_line)
                if len(remaining_lines) >= lines_per_file:
                    # Write this batch to a file
                    with safe_open_write(output_file_path) as current_output_file:
                        for line in remaining_lines:
                            try:
                                json.loads(line.strip())
                                current_output_file.write(line)
                            except json.JSONDecodeError:
                                print(f"Warning: Skipping invalid JSON at line {line_number}")
                            line_number += 1
                    
                    # Start a new batch
                    remaining_lines = []
                    file_number += 1
                    output_file_path = output_path / f"{base_name}_part{file_number:03d}.json"
                    print(f"Creating {base_name}_part{file_number:03d}.json")
            
            # Write any remaining lines to the last file
            if remaining_lines:
                with safe_open_write(output_file_path) as current_output_file:
                    for line in remaining_lines:
                        try:
                            json.loads(line.strip())
                            current_output_file.write(line)
                        except json.JSONDecodeError:
                            print(f"Warning: Skipping invalid JSON at line {line_number}")
                        line_number += 1
    
    print(f"Split complete. Created {file_number} files in {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description='Split large JSON files into smaller chunks.')
    parser.add_argument('filename', help='Path to the large JSON file')
    parser.add_argument('--output-dir', '-o', default='./split_output', 
                        help='Directory where split files will be saved')
    parser.add_argument('--lines', '-l', type=int, default=100000,
                        help='Number of lines per output file (default: 100,000)')
    
    args = parser.parse_args()
    
    split_json_file(args.filename, args.output_dir, args.lines)


if __name__ == '__main__':
    main() 