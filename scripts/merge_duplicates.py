#!/usr/bin/env python3

"""
Script to merge duplicate code in the VDM project based on analysis results.
This script reads duplicate reports and performs automatic merges where possible.
"""

import os
import re
import json
import shutil
import difflib
from datetime import datetime
import argparse
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scripts/merge_duplicates.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DuplicateMerger:
    def __init__(self, cs_report_path, py_report_path, project_root, output_dir):
        """Initialize the merger with the paths to the reports and project root."""
        self.cs_report_path = cs_report_path
        self.py_report_path = py_report_path
        self.project_root = os.path.abspath(project_root)
        self.output_dir = os.path.abspath(output_dir)
        
        # Load reports
        self.cs_report = self._load_report(cs_report_path) if cs_report_path else None
        self.py_report = self._load_report(py_report_path) if py_report_path else None
        
        # Results tracking
        self.merged_files = {}
        self.merge_logs = []
        self.preferred_directories = [
            "Assets/Scripts",  # Preferred over "Assets/VisualDM"
            "Scripts/Core",    # Preferred location for core functionality
            "Backend/modules"  # Preferred over scattered Python modules
        ]
        
    def _load_report(self, report_path):
        """Load a report file into a dictionary."""
        try:
            with open(report_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading report {report_path}: {e}")
            return None
    
    def _log_merge(self, merge_type, source_file, target_files, reason):
        """Log details about a merge operation."""
        self.merge_logs.append({
            'type': merge_type,
            'source': source_file,
            'targets': target_files,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
        
    def _choose_best_file(self, files):
        """Choose the best file from a list of duplicates based on several heuristics."""
        if not files:
            return None
            
        # Use a scoring system to determine the "best" file
        file_scores = {}
        
        for file_path in files:
            abs_path = os.path.join(self.project_root, file_path)
            score = 0
            
            # 1. Prefer files in standard locations
            for preferred_dir in self.preferred_directories:
                if preferred_dir in file_path:
                    score += 5
                    break
                    
            # 2. Prefer more recently modified files
            try:
                mtime = os.path.getmtime(abs_path)
                # Convert to days since epoch to keep scores manageable
                days_since_epoch = mtime / (60*60*24)
                score += days_since_epoch / 1000  # Scale down to avoid dominating
            except:
                pass
                
            # 3. Prefer larger files (usually more complete implementations)
            try:
                size = os.path.getsize(abs_path)
                # Log scale to prevent large files from dominating
                if size > 0:
                    import math
                    score += math.log10(size)
            except:
                pass
                
            # 4. Prefer files with more imports/references (more integrated with codebase)
            try:
                with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Count imports
                    if file_path.endswith('.cs'):
                        imports = len(re.findall(r'using\s+[^;]+;', content))
                    elif file_path.endswith('.py'):
                        imports = len(re.findall(r'^(?:import|from)\s+', content, re.MULTILINE))
                    else:
                        imports = 0
                        
                    score += imports * 0.5
                    
                    # Count references to other project files
                    for ref in ['VisualDM', 'VDM', 'Assets', 'Scripts']:
                        refs = len(re.findall(rf'{ref}\.', content))
                        score += refs * 0.2
            except:
                pass
                
            file_scores[file_path] = score
            
        # Find the highest score
        best_file = max(file_scores.items(), key=lambda x: x[1])[0]
        
        return best_file
    
    def merge_exact_duplicates(self):
        """Merge files that have identical content."""
        results = {}
        
        # Process C# exact duplicates
        if self.cs_report and 'exact_duplicates' in self.cs_report:
            for hash_val, files in self.cs_report['exact_duplicates'].items():
                if len(files) <= 1:
                    continue
                    
                best_file = self._choose_best_file(files)
                if best_file:
                    redundant_files = [f for f in files if f != best_file]
                    results[best_file] = {
                        'source': best_file,
                        'identical_copies': redundant_files,
                        'type': 'exact_duplicate',
                        'language': 'cs'
                    }
                    
                    self._log_merge('exact_cs', best_file, redundant_files, 
                                   f"Identical content (hash: {hash_val})")
        
        # Process Python exact duplicates
        if self.py_report and 'exact_duplicates' in self.py_report:
            for hash_val, files in self.py_report['exact_duplicates'].items():
                if len(files) <= 1:
                    continue
                    
                best_file = self._choose_best_file(files)
                if best_file:
                    redundant_files = [f for f in files if f != best_file]
                    results[best_file] = {
                        'source': best_file,
                        'identical_copies': redundant_files,
                        'type': 'exact_duplicate',
                        'language': 'python'
                    }
                    
                    self._log_merge('exact_py', best_file, redundant_files, 
                                   f"Identical content (hash: {hash_val})")
        
        self.merged_files.update(results)
        print(f"Identified {len(results)} source files with exact duplicates to keep.")
        return results
        
    def merge_class_duplicates(self):
        """Merge C# classes that appear in multiple files."""
        results = {}
        
        if self.cs_report and 'class_duplicates' in self.cs_report:
            for class_name, files in self.cs_report['class_duplicates'].items():
                if len(files) <= 1:
                    continue
                    
                best_file = self._choose_best_file(files)
                if best_file:
                    redundant_files = [f for f in files if f != best_file]
                    results[best_file] = {
                        'source': best_file,
                        'similar_copies': redundant_files,
                        'type': 'class_duplicate',
                        'class_name': class_name,
                        'language': 'cs'
                    }
                    
                    self._log_merge('class', best_file, redundant_files, 
                                   f"Multiple implementations of class '{class_name}'")
        
        self.merged_files.update(results)
        print(f"Identified {len(results)} source files for duplicate classes to keep.")
        return results
        
    def merge_singleton_duplicates(self):
        """Merge C# singleton implementations."""
        results = {}
        
        if self.cs_report and 'singleton_duplicates' in self.cs_report:
            for class_name, files in self.cs_report['singleton_duplicates'].items():
                if len(files) <= 1:
                    continue
                    
                best_file = self._choose_best_file(files)
                if best_file:
                    redundant_files = [f for f in files if f != best_file]
                    results[best_file] = {
                        'source': best_file,
                        'similar_copies': redundant_files,
                        'type': 'singleton_duplicate',
                        'class_name': class_name,
                        'language': 'cs'
                    }
                    
                    self._log_merge('singleton', best_file, redundant_files, 
                                   f"Multiple singleton implementations of '{class_name}'")
        
        self.merged_files.update(results)
        print(f"Identified {len(results)} source files for duplicate singletons to keep.")
        return results
        
    def merge_manager_duplicates(self):
        """Merge C# manager classes with similar functionality."""
        results = {}
        
        if self.cs_report and 'manager_duplicates' in self.cs_report:
            for prefix, files in self.cs_report['manager_duplicates'].items():
                if len(files) <= 1:
                    continue
                    
                best_file = self._choose_best_file(files)
                if best_file:
                    redundant_files = [f for f in files if f != best_file]
                    results[best_file] = {
                        'source': best_file,
                        'similar_copies': redundant_files,
                        'type': 'manager_duplicate',
                        'manager_prefix': prefix,
                        'language': 'cs'
                    }
                    
                    self._log_merge('manager', best_file, redundant_files, 
                                   f"Multiple manager implementations with prefix '{prefix}'")
        
        self.merged_files.update(results)
        print(f"Identified {len(results)} source files for duplicate managers to keep.")
        return results
        
    def merge_module_duplicates(self):
        """Merge Python modules with similar functionality."""
        results = {}
        
        if self.py_report and 'module_duplicates' in self.py_report:
            for module_name, files in self.py_report['module_duplicates'].items():
                if len(files) <= 1:
                    continue
                    
                best_file = self._choose_best_file(files)
                if best_file:
                    redundant_files = [f for f in files if f != best_file]
                    results[best_file] = {
                        'source': best_file,
                        'similar_copies': redundant_files,
                        'type': 'module_duplicate',
                        'module_name': module_name,
                        'language': 'python'
                    }
                    
                    self._log_merge('module', best_file, redundant_files, 
                                   f"Multiple implementations of module '{module_name}'")
        
        self.merged_files.update(results)
        print(f"Identified {len(results)} source files for duplicate Python modules to keep.")
        return results
        
    def merge_similar_files(self, similarity_threshold=0.8):
        """Merge files that are similar but not identical."""
        results = {}
        
        # Process C# similar files
        if self.cs_report and 'similar_files' in self.cs_report:
            # Group by class or manager prefix
            similar_by_id = defaultdict(list)
            for item in self.cs_report['similar_files']:
                if item['similarity_info']['similarity'] >= similarity_threshold:
                    identifier = item.get('class_name', item.get('manager_prefix', 'Unknown'))
                    similar_by_id[identifier].append(item)
            
            for identifier, items in similar_by_id.items():
                if len(items) < 1:
                    continue
                    
                # Extract all unique files
                all_files = set()
                for item in items:
                    all_files.add(item['similarity_info']['file1'])
                    all_files.add(item['similarity_info']['file2'])
                    
                best_file = self._choose_best_file(list(all_files))
                if best_file:
                    redundant_files = [f for f in all_files if f != best_file]
                    results[best_file] = {
                        'source': best_file,
                        'similar_copies': list(redundant_files),
                        'type': 'similar_files',
                        'identifier': identifier,
                        'language': 'cs'
                    }
                    
                    self._log_merge('similar_cs', best_file, list(redundant_files), 
                                   f"Similar content for '{identifier}'")
        
        # Process Python similar files
        if self.py_report and 'similar_files' in self.py_report:
            # Group by module name
            similar_by_module = defaultdict(list)
            for item in self.py_report['similar_files']:
                if item['similarity_info']['similarity'] >= similarity_threshold:
                    module_name = item.get('module_name', 'Unknown')
                    similar_by_module[module_name].append(item)
            
            for module_name, items in similar_by_module.items():
                if len(items) < 1:
                    continue
                    
                # Extract all unique files
                all_files = set()
                for item in items:
                    all_files.add(item['similarity_info']['file1'])
                    all_files.add(item['similarity_info']['file2'])
                    
                best_file = self._choose_best_file(list(all_files))
                if best_file:
                    redundant_files = [f for f in all_files if f != best_file]
                    results[best_file] = {
                        'source': best_file,
                        'similar_copies': list(redundant_files),
                        'type': 'similar_files',
                        'module_name': module_name,
                        'language': 'python'
                    }
                    
                    self._log_merge('similar_py', best_file, list(redundant_files), 
                                   f"Similar content for module '{module_name}'")
        
        self.merged_files.update(results)
        print(f"Identified {len(results)} source files for similar content to keep.")
        return results
        
    def create_merge_plan(self):
        """Create a comprehensive plan for merging all duplicate types."""
        print("Creating merge plan...")
        
        # Run all merge operations
        self.merge_exact_duplicates()
        self.merge_class_duplicates()
        self.merge_singleton_duplicates()
        self.merge_manager_duplicates()
        self.merge_module_duplicates()
        self.merge_similar_files()
        
        # Create a comprehensive report
        report = {
            'summary': {
                'total_source_files': len(self.merged_files),
                'total_redundant_files': sum(
                    len(info.get('identical_copies', [])) + len(info.get('similar_copies', []))
                    for info in self.merged_files.values()
                ),
                'cs_files': sum(1 for info in self.merged_files.values() if info.get('language') == 'cs'),
                'python_files': sum(1 for info in self.merged_files.values() if info.get('language') == 'python'),
            },
            'merge_operations': self.merged_files,
            'merge_logs': self.merge_logs
        }
        
        # Write the report
        os.makedirs(self.output_dir, exist_ok=True)
        output_path = os.path.join(self.output_dir, 'merge_plan.json')
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Create human-readable version
        txt_output = os.path.join(self.output_dir, 'merge_plan.txt')
        with open(txt_output, 'w') as f:
            f.write("# Duplicate Files Merge Plan\n\n")
            
            f.write("## Summary\n")
            for key, value in report['summary'].items():
                f.write(f"- {key}: {value}\n")
                
            f.write("\n## Source Files to Keep\n")
            for source, info in self.merged_files.items():
                f.write(f"\n### {info['type']}: {source}\n")
                if 'identical_copies' in info:
                    f.write("Identical copies to remove:\n")
                    for file in info['identical_copies']:
                        f.write(f"- {file}\n")
                if 'similar_copies' in info:
                    f.write("Similar copies to remove/refactor:\n")
                    for file in info['similar_copies']:
                        f.write(f"- {file}\n")
                        
            f.write("\n## Merge Logs\n")
            for log in self.merge_logs:
                f.write(f"\n### {log['type']}: {log['source']}\n")
                f.write(f"Reason: {log['reason']}\n")
                f.write("Targets:\n")
                for target in log['targets']:
                    f.write(f"- {target}\n")
                f.write(f"Timestamp: {log['timestamp']}\n")
                
        print(f"Merge plan created and written to {output_path} and {txt_output}")
        return report
        
    def execute_merge_plan(self, dry_run=True):
        """Execute the merge plan by copying source files and removing duplicates."""
        if not self.merged_files:
            self.create_merge_plan()
            
        # Create backup directory structure
        backup_dir = os.path.join(self.output_dir, 'redundant_files_backup')
        os.makedirs(backup_dir, exist_ok=True)
        
        print(f"{'Simulating' if dry_run else 'Executing'} merge plan...")
        
        for source_relative, info in self.merged_files.items():
            source_path = os.path.join(self.project_root, source_relative)
            
            # Process identical copies
            if 'identical_copies' in info:
                for target_relative in info['identical_copies']:
                    target_path = os.path.join(self.project_root, target_relative)
                    backup_path = os.path.join(backup_dir, target_relative)
                    
                    # Ensure backup directory exists
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    
                    if not dry_run:
                        # Backup the file
                        shutil.copy2(target_path, backup_path)
                        # Remove the redundant file
                        os.remove(target_path)
                    
                    print(f"{'Would remove' if dry_run else 'Removed'} identical copy: {target_relative}")
                    
            # Process similar copies
            if 'similar_copies' in info:
                for target_relative in info['similar_copies']:
                    target_path = os.path.join(self.project_root, target_relative)
                    backup_path = os.path.join(backup_dir, target_relative)
                    
                    # Ensure backup directory exists
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    
                    if not dry_run:
                        # Backup the file
                        shutil.copy2(target_path, backup_path)
                        # Either remove or mark the file as deprecated
                        if info['type'] == 'exact_duplicate':
                            os.remove(target_path)
                            print(f"Removed duplicate: {target_relative}")
                        else:
                            # For similar files, we'll add a deprecation notice
                            self._add_deprecation_notice(target_path, source_relative)
                            print(f"Added deprecation notice to: {target_relative}")
                    else:
                        if info['type'] == 'exact_duplicate':
                            print(f"Would remove duplicate: {target_relative}")
                        else:
                            print(f"Would add deprecation notice to: {target_relative}")
        
        return {
            'dry_run': dry_run,
            'backup_dir': backup_dir,
            'files_processed': len(self.merged_files)
        }
        
    def _add_deprecation_notice(self, file_path, preferred_file):
        """Add a deprecation notice to a file, pointing to the preferred version."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if file_path.endswith('.cs'):
                notice = f"""
// DEPRECATED: This file contains duplicate/similar code to {preferred_file}
// Please use that file instead. This file will be removed in a future cleanup.
// Generated by duplicate code consolidation script on {datetime.datetime.now().strftime('%Y-%m-%d')}

"""
                # Add after any using statements or at the top
                if "using " in content:
                    last_using = content.rfind("using ", 0, content.find("namespace "))
                    if last_using != -1:
                        end_of_using = content.find(";", last_using) + 1
                        new_content = content[:end_of_using] + notice + content[end_of_using:]
                    else:
                        new_content = notice + content
                else:
                    new_content = notice + content
                
            elif file_path.endswith('.py'):
                notice = f"""
# DEPRECATED: This file contains duplicate/similar code to {preferred_file}
# Please use that file instead. This file will be removed in a future cleanup.
# Generated by duplicate code consolidation script on {datetime.datetime.now().strftime('%Y-%m-%d')}

"""
                # Add after any imports or at the top
                if "import " in content or "from " in content:
                    # Find the last import statement
                    import_pattern = re.compile(r'^(?:import|from)\s+', re.MULTILINE)
                    matches = list(import_pattern.finditer(content))
                    if matches:
                        last_import = matches[-1]
                        end_of_import = content.find("\n", last_import.start()) + 1
                        new_content = content[:end_of_import] + notice + content[end_of_import:]
                    else:
                        new_content = notice + content
                else:
                    new_content = notice + content
            else:
                # For other file types, just prepend the notice
                notice = f"DEPRECATED: This file contains duplicate/similar code to {preferred_file}\n"
                new_content = notice + content
                
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
        except Exception as e:
            print(f"Error adding deprecation notice to {file_path}: {e}")

def main():
    """Main function to run the duplicate merger."""
    # Parse command-line arguments
    if len(sys.argv) < 4:
        print("Usage: python merge_duplicates.py [cs_report] [py_report] [project_root] [output_dir]")
        sys.exit(1)
        
    cs_report = sys.argv[1]
    py_report = sys.argv[2]
    project_root = sys.argv[3]
    output_dir = sys.argv[4] if len(sys.argv) > 4 else os.path.join(project_root, 'scripts', 'consolidation')
    
    # Run merger
    merger = DuplicateMerger(cs_report, py_report, project_root, output_dir)
    merger.create_merge_plan()
    
    # By default, do a dry run
    merger.execute_merge_plan(dry_run=True)
    
    print("\nDry run complete. To actually perform the merge, run with:")
    print(f"python merge_duplicates.py {cs_report} {py_report} {project_root} {output_dir} --execute")
    
    # If --execute is passed, perform the actual merge
    if len(sys.argv) > 5 and sys.argv[5] == '--execute':
        input("Press Enter to continue with the actual merge (Ctrl+C to abort)...")
        merger.execute_merge_plan(dry_run=False)
        print("\nMerge completed. Duplicate files have been backed up in the output directory.")

if __name__ == "__main__":
    main() 