#!/usr/bin/env python3
"""
💥 MONOLITH BREAKER
Intelligently breaks apart massive monolithic files into focused modules
"""

import os
import ast
import re
import shutil
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class MonolithBreaker:
    def __init__(self):
        self.archives_dir = Path("archives/monoliths")
        self.archives_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_functions(self, file_path: Path) -> Dict:
        """Analyze file and categorize functions for intelligent splitting"""
        
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        lines = content.splitlines()
        
        analysis = {
            'imports': [],
            'classes': [],
            'functions': [],
            'other_code': [],
            'total_lines': len(lines)
        }
        
        # Track line ranges that are accounted for
        accounted_lines = set()
        
        # Extract imports (at top of file)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_text = '\n'.join(lines[node.lineno-1:node.end_lineno])
                analysis['imports'].append({
                    'text': import_text,
                    'start': node.lineno,
                    'end': node.end_lineno
                })
                for i in range(node.lineno-1, node.end_lineno):
                    accounted_lines.add(i)
        
        # Extract classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_text = '\n'.join(lines[node.lineno-1:node.end_lineno])
                analysis['classes'].append({
                    'name': node.name,
                    'text': class_text,
                    'start': node.lineno,
                    'end': node.end_lineno,
                    'lines': node.end_lineno - node.lineno + 1
                })
                for i in range(node.lineno-1, node.end_lineno):
                    accounted_lines.add(i)
        
        # Extract functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip functions that are inside classes
                is_method = any(node.lineno >= cls['start'] and node.lineno <= cls['end'] 
                              for cls in analysis['classes'])
                if is_method:
                    continue
                    
                func_text = '\n'.join(lines[node.lineno-1:node.end_lineno])
                category = self._categorize_function(node.name, func_text)
                
                analysis['functions'].append({
                    'name': node.name,
                    'text': func_text,
                    'start': node.lineno,
                    'end': node.end_lineno,
                    'lines': node.end_lineno - node.lineno + 1,
                    'category': category
                })
                for i in range(node.lineno-1, node.end_lineno):
                    accounted_lines.add(i)
        
        # Extract other code (module-level variables, comments, etc.)
        other_lines = []
        for i, line in enumerate(lines):
            if i not in accounted_lines:
                other_lines.append((i+1, line))
        
        if other_lines:
            analysis['other_code'] = other_lines
            
        return analysis
    
    def _categorize_function(self, func_name: str, func_text: str) -> str:
        """Categorize function based on name and content"""
        
        func_lower = func_name.lower()
        text_lower = func_text.lower()
        
        # Database/CRUD operations
        if any(keyword in func_lower for keyword in ['create', 'update', 'delete', 'get_', 'find_', 'query', 'save', 'load', 'fetch']):
            return 'database'
        elif any(keyword in text_lower for keyword in ['select ', 'insert ', 'update ', 'delete ', 'sql', 'query']):
            return 'database'
            
        # Generation/Creation logic
        elif any(keyword in func_lower for keyword in ['generate', 'create_', 'build_', 'make_', 'spawn']):
            return 'generation'
            
        # Validation/Processing
        elif any(keyword in func_lower for keyword in ['validate', 'check', 'verify', 'process', 'calculate', 'compute']):
            return 'validation'
            
        # Event handling
        elif any(keyword in func_lower for keyword in ['handle_', 'on_', 'trigger', 'dispatch', 'emit', 'process_event']):
            return 'events'
            
        # API/Service endpoints
        elif any(keyword in func_lower for keyword in ['api_', 'service_', 'endpoint', 'route_']):
            return 'api'
            
        # Utility/Helper functions
        elif any(keyword in func_lower for keyword in ['_helper', '_util', '_format', '_convert', '_parse', 'helper', 'utility', 'format_', 'parse_']):
            return 'utils'
            
        # Initialization/Setup
        elif any(keyword in func_lower for keyword in ['init', 'setup', 'configure', 'initialize']):
            return 'initialization'
            
        # Private/Internal methods
        elif func_name.startswith('_'):
            return 'internal'
            
        else:
            return 'core'
    
    def create_split_modules(self, file_path: Path, analysis: Dict) -> Dict[str, str]:
        """Create split modules based on function categorization"""
        
        # Group functions by category
        category_groups = defaultdict(list)
        for func in analysis['functions']:
            category_groups[func['category']].append(func)
        
        # Create modules for categories with enough content
        modules = {}
        
        # Standard imports that most modules will need
        base_imports = '\n'.join([imp['text'] for imp in analysis['imports']])
        
        for category, functions in category_groups.items():
            if len(functions) < 2 and sum(f['lines'] for f in functions) < 50:
                # Too small, merge into core
                category_groups['core'].extend(functions)
                continue
                
            module_content = f'''"""
{category.title()} module for {file_path.stem}
Auto-generated by splitting {file_path.name}
"""

{base_imports}

'''
            
            # Add functions for this category
            for func in functions:
                module_content += f"\n{func['text']}\n\n"
            
            # Clean up extra newlines
            module_content = re.sub(r'\n{3,}', '\n\n', module_content)
            
            modules[f"{category}.py"] = module_content
            
        # Create core module with remaining content
        core_content = f'''"""
Core module for {file_path.stem}
Auto-generated by splitting {file_path.name}
"""

{base_imports}

'''
        
        # Add classes
        for cls in analysis['classes']:
            core_content += f"\n{cls['text']}\n\n"
            
        # Add core/uncategorized functions
        for func in category_groups['core']:
            core_content += f"\n{func['text']}\n\n"
            
        # Add other code
        if analysis['other_code']:
            core_content += "\n# Module-level code\n"
            for line_num, line in analysis['other_code']:
                core_content += f"{line}\n"
        
        core_content = re.sub(r'\n{3,}', '\n\n', core_content)
        modules[f"{file_path.stem}_core.py"] = core_content
        
        return modules
    
    def split_monolith(self, file_path: Path) -> bool:
        """Split a monolithic file into smaller modules"""
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return False
            
        print(f"\n💥 SPLITTING MONOLITH: {file_path}")
        print(f"📏 Size: {file_path.stat().st_size / 1024:.1f} KB")
        
        try:
            # Analyze the file
            analysis = self.analyze_functions(file_path)
            
            print(f"📊 Analysis:")
            print(f"   📄 Total lines: {analysis['total_lines']:,}")
            print(f"   🔧 Functions: {len(analysis['functions'])}")
            print(f"   🏗️  Classes: {len(analysis['classes'])}")
            print(f"   📦 Imports: {len(analysis['imports'])}")
            
            # Create split modules
            modules = self.create_split_modules(file_path, analysis)
            
            print(f"✂️  Creating {len(modules)} modules:")
            
            # Write new modules
            parent_dir = file_path.parent
            for module_name, content in modules.items():
                module_path = parent_dir / module_name
                module_path.write_text(content, encoding='utf-8')
                lines = len(content.splitlines())
                print(f"   📁 {module_name}: {lines:,} lines")
            
            # Archive original file
            archive_path = self.archives_dir / f"{file_path.parent.name}_{file_path.name}"
            shutil.copy2(file_path, archive_path)
            print(f"   📦 Archived: {archive_path}")
            
            # Remove original file
            file_path.unlink()
            print(f"   🗑️  Removed: {file_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error splitting {file_path}: {e}")
            return False

def break_all_monoliths():
    """Break apart all identified monolithic files"""
    
    systems_dir = Path("backend/systems")
    
    # Monoliths to break (ordered by size/impact)
    monoliths = [
        "loot/loot_utils.py",                    # 4,271 lines - BIGGEST
        "diplomacy/services.py",                 # 2,067 lines  
        "combat/combat_class.py",                # 2,010 lines - User mentioned
        "magic/services.py",                     # 1,473 lines
        "crafting/services/crafting_service.py", # 1,472 lines
        "motif/manager.py",                      # 1,455 lines
        "memory/memory_manager.py",              # 1,192 lines
        "faction/services/relationship_service.py", # 1,052 lines
    ]
    
    print("💥 MONOLITH BREAKER - INTELLIGENT FILE SPLITTING")
    print("=" * 80)
    
    breaker = MonolithBreaker()
    results = []
    
    total_lines_before = 0
    total_lines_after = 0
    
    for monolith_file in monoliths:
        monolith_path = systems_dir / monolith_file
        
        if not monolith_path.exists():
            print(f"⚠️  Skipping {monolith_file} - not found")
            continue
            
        # Get original size
        original_lines = len(monolith_path.read_text(encoding='utf-8').splitlines())
        total_lines_before += original_lines
        
        success = breaker.split_monolith(monolith_path)
        
        if success:
            # Count new module lines
            parent_dir = monolith_path.parent
            new_modules = list(parent_dir.glob(f"{monolith_path.stem}*.py"))
            new_modules.extend(parent_dir.glob("*database.py"))
            new_modules.extend(parent_dir.glob("*generation.py"))
            new_modules.extend(parent_dir.glob("*validation.py"))
            new_modules.extend(parent_dir.glob("*events.py"))
            new_modules.extend(parent_dir.glob("*utils.py"))
            
            module_lines = 0
            for module in new_modules:
                if module.exists():
                    module_lines += len(module.read_text(encoding='utf-8').splitlines())
            
            total_lines_after += module_lines
            
            results.append({
                'file': monolith_file,
                'original_lines': original_lines,
                'new_lines': module_lines,
                'modules_created': len([f for f in parent_dir.glob(f"{monolith_path.stem}*.py") if f.exists()]),
                'success': True
            })
        else:
            results.append({
                'file': monolith_file,
                'success': False
            })
    
    print(f"\n📊 SPLITTING RESULTS")
    print("=" * 80)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successfully split: {len(successful)} files")
    print(f"❌ Failed: {len(failed)} files")
    
    if successful:
        print(f"\n📈 IMPACT SUMMARY:")
        print(f"   📏 Total lines before: {total_lines_before:,}")
        print(f"   📏 Total lines after: {total_lines_after:,}")
        print(f"   📉 Overhead reduction: {total_lines_before - total_lines_after:,} lines")
        print(f"   📦 Files created: {sum(r['modules_created'] for r in successful)}")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in successful:
            print(f"   ✅ {result['file']}")
            print(f"      📏 {result['original_lines']:,} → {result['new_lines']:,} lines")
            print(f"      📦 {result['modules_created']} modules created")
            
    if failed:
        print(f"\n❌ FAILED FILES:")
        for result in failed:
            print(f"   ❌ {result['file']}")
    
    print(f"\n🎯 NEXT STEPS:")
    next_steps = [
        "1. 🧪 Run tests to ensure nothing is broken",
        "2. 🔍 Check for any import errors in the codebase",
        "3. 📝 Update documentation to reflect new module structure", 
        "4. 🔄 Update any hard-coded imports that reference old files",
        "5. 🚀 Commit changes with detailed explanation"
    ]
    
    for step in next_steps:
        print(f"   {step}")
    
    return results

if __name__ == "__main__":
    results = break_all_monoliths() 