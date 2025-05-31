#!/usr/bin/env python3
"""
✂️ MONOLITH SPLITTER
Intelligently splits large monolithic files into focused smaller modules
"""

import os
import ast
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class MonolithSplitter:
    def __init__(self):
        self.function_groups = defaultdict(list)  # group_name -> [functions]
        self.imports = []
        self.classes = []
        
    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a monolithic file and suggest splits"""
        
        print(f"\n✂️ ANALYZING MONOLITH: {file_path.name}")
        
        content = file_path.read_text(encoding='utf-8')
        tree = ast.parse(content)
        
        analysis = {
            'file_path': file_path,
            'total_lines': len(content.splitlines()),
            'functions': [],
            'classes': [],
            'imports': [],
            'suggested_splits': {}
        }
        
        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                analysis['imports'].append(ast.get_source_segment(content, node))
        
        # Extract functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                func_lines = node.end_lineno - node.lineno + 1
                
                # Categorize function by naming patterns
                category = self._categorize_function(func_name)
                
                analysis['functions'].append({
                    'name': func_name,
                    'lines': func_lines,
                    'category': category,
                    'start_line': node.lineno,
                    'end_line': node.end_lineno
                })
                
            elif isinstance(node, ast.ClassDef):
                class_name = node.name
                class_lines = node.end_lineno - node.lineno + 1
                
                analysis['classes'].append({
                    'name': class_name,
                    'lines': class_lines,
                    'start_line': node.lineno,
                    'end_line': node.end_lineno
                })
        
        # Suggest splits based on function categories
        analysis['suggested_splits'] = self._suggest_splits(analysis)
        
        return analysis
        
    def _categorize_function(self, func_name: str) -> str:
        """Categorize function based on naming patterns"""
        
        func_lower = func_name.lower()
        
        # Database/CRUD operations
        if any(keyword in func_lower for keyword in ['create', 'update', 'delete', 'get', 'find', 'query', 'save', 'load']):
            return 'database'
            
        # Validation/Processing
        elif any(keyword in func_lower for keyword in ['validate', 'check', 'verify', 'process', 'calculate', 'compute']):
            return 'validation'
            
        # Utility/Helper functions
        elif any(keyword in func_lower for keyword in ['_helper', '_util', '_format', '_convert', '_parse', 'helper', 'utility']):
            return 'utils'
            
        # Event/Action handling
        elif any(keyword in func_lower for keyword in ['handle', 'on_', 'trigger', 'dispatch', 'emit']):
            return 'events'
            
        # API/Service layer
        elif any(keyword in func_lower for keyword in ['api_', 'service_', 'endpoint', 'route']):
            return 'api'
            
        # Private/Internal methods
        elif func_name.startswith('_'):
            return 'internal'
            
        # Initialization/Setup
        elif any(keyword in func_lower for keyword in ['init', 'setup', 'configure', 'initialize']):
            return 'init'
            
        else:
            return 'general'
    
    def _suggest_splits(self, analysis: Dict) -> Dict:
        """Suggest how to split the file based on function categories"""
        
        # Group functions by category
        category_groups = defaultdict(list)
        category_lines = defaultdict(int)
        
        for func in analysis['functions']:
            category = func['category']
            category_groups[category].append(func)
            category_lines[category] += func['lines']
        
        # Only suggest splits for categories with significant content
        suggested_splits = {}
        
        for category, functions in category_groups.items():
            if len(functions) >= 3 or category_lines[category] >= 100:  # Minimum threshold
                suggested_splits[category] = {
                    'functions': functions,
                    'total_lines': category_lines[category],
                    'file_name': f"{category}.py"
                }
        
        return suggested_splits

    def create_split_plan(self, analysis: Dict) -> str:
        """Create a detailed split plan for the monolith"""
        
        file_path = analysis['file_path']
        total_lines = analysis['total_lines']
        
        plan = f"""
📋 SPLIT PLAN FOR {file_path.name}
{'=' * 60}

📊 Current size: {total_lines:,} lines
📦 Functions: {len(analysis['functions'])}
🏗️  Classes: {len(analysis['classes'])}

🎯 SUGGESTED SPLITS:
"""
        
        if not analysis['suggested_splits']:
            plan += "   ❌ No clear split opportunities identified\n"
            plan += "   💡 Consider refactoring by feature rather than function type\n"
            return plan
        
        for category, split_info in analysis['suggested_splits'].items():
            functions = split_info['functions']
            lines = split_info['total_lines']
            file_name = split_info['file_name']
            
            plan += f"\n📁 {file_name} ({category}):\n"
            plan += f"   📏 {lines} lines ({len(functions)} functions)\n"
            plan += f"   🔧 Functions: {', '.join([f['name'] for f in functions[:3]])}"
            if len(functions) > 3:
                plan += f", ... and {len(functions) - 3} more"
            plan += "\n"
        
        # Calculate remaining content
        split_lines = sum(split['total_lines'] for split in analysis['suggested_splits'].values())
        remaining_lines = total_lines - split_lines
        
        plan += f"\n📋 REMAINING CONTENT:\n"
        plan += f"   📏 ~{remaining_lines} lines (classes, imports, misc functions)\n"
        plan += f"   📄 Keep in: {file_path.stem}_core.py\n"
        
        plan += f"\n🔧 REFACTORING BENEFITS:\n"
        plan += f"   📉 Reduce main file from {total_lines:,} to ~{remaining_lines} lines\n"
        plan += f"   📁 Create {len(analysis['suggested_splits'])} focused modules\n"
        plan += f"   🧹 Improve maintainability and testability\n"
        
        return plan

def analyze_monoliths():
    """Analyze all identified monoliths and suggest splitting strategies"""
    
    systems_dir = Path("backend/systems")
    
    # Focus on the largest monoliths
    monolith_files = [
        "loot/loot_utils.py",        # 4,271 lines
        "diplomacy/services.py",     # 2,067 lines  
        "combat/combat_class.py",    # 2,010 lines
        "magic/services.py",         # 1,473 lines
        "crafting/services/crafting_service.py",  # 1,472 lines
        "motif/manager.py",          # 1,455 lines
        "memory/memory_manager.py",  # 1,192 lines
    ]
    
    print("✂️ MONOLITH SPLITTING ANALYZER")
    print("=" * 60)
    
    splitter = MonolithSplitter()
    all_plans = []
    
    for monolith_file in monolith_files:
        monolith_path = systems_dir / monolith_file
        
        if not monolith_path.exists():
            print(f"⚠️  File not found: {monolith_file}")
            continue
            
        try:
            analysis = splitter.analyze_file(monolith_path)
            plan = splitter.create_split_plan(analysis)
            all_plans.append(plan)
            print(plan)
            
        except Exception as e:
            print(f"❌ Error analyzing {monolith_file}: {e}")
    
    # Create summary recommendations
    print(f"\n🎯 OVERALL REFACTORING RECOMMENDATIONS")
    print("=" * 60)
    
    recommendations = [
        "1. 🥇 PRIORITY: Focus on loot_utils.py (4,271 lines) - biggest impact",
        "2. 🏗️  STRATEGY: Split by functional domains rather than technical layers", 
        "3. 📦 MODULES: Create focused modules like loot_generation.py, loot_validation.py",
        "4. 🧪 TESTING: Add unit tests for each new module",
        "5. 📝 DOCS: Document the new module structure",
        "6. 🔄 IMPORTS: Update all import statements after splitting",
        "7. 🎯 GRADUAL: Do one monolith at a time to avoid breaking changes"
    ]
    
    for rec in recommendations:
        print(f"   {rec}")
    
    return all_plans

if __name__ == "__main__":
    analyze_monoliths() 