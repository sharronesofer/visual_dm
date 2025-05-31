#!/usr/bin/env python3
"""
🔍 ZOMBIE ANALYZER
Analyzes zombie monoliths for function duplication and creates safe removal strategy
"""

import os
import re
import ast
import hashlib
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple

class FunctionAnalyzer:
    def __init__(self):
        self.function_signatures = defaultdict(list)  # signature -> [file_paths]
        self.function_bodies = defaultdict(list)      # body_hash -> [file_paths]
        self.file_functions = defaultdict(list)       # file_path -> [function_names]
        
    def extract_functions(self, file_path: Path) -> List[Tuple[str, str, str]]:
        """Extract function signatures and bodies from a Python file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Get function signature
                    args = [arg.arg for arg in node.args.args]
                    signature = f"{node.name}({', '.join(args)})"
                    
                    # Get function body (simplified)
                    body_lines = content.split('\n')[node.lineno-1:node.end_lineno]
                    body = '\n'.join(body_lines).strip()
                    
                    # Create hash of normalized body (remove whitespace/comments)
                    normalized_body = re.sub(r'#.*', '', body)  # Remove comments
                    normalized_body = re.sub(r'\s+', ' ', normalized_body)  # Normalize whitespace
                    body_hash = hashlib.md5(normalized_body.encode()).hexdigest()[:12]
                    
                    functions.append((signature, body, body_hash))
                    
            return functions
            
        except Exception as e:
            print(f"   ⚠️  Error parsing {file_path}: {e}")
            return []

    def analyze_file(self, file_path: Path):
        """Analyze a single file for functions"""
        functions = self.extract_functions(file_path)
        
        for signature, body, body_hash in functions:
            self.function_signatures[signature].append(str(file_path))
            self.function_bodies[body_hash].append(str(file_path))
            self.file_functions[str(file_path)].append(signature)

def analyze_zombie_duplication():
    """Analyze zombie monoliths for function duplication"""
    
    systems_dir = Path("backend/systems")
    if not systems_dir.exists():
        print("❌ backend/systems directory not found")
        return
    
    print("🔍 ZOMBIE DUPLICATION ANALYZER")
    print("=" * 70)
    
    # Get zombie candidates from previous analysis
    zombie_files = [
        "loot/loot_utils.py",
        "diplomacy/services.py", 
        "combat/combat_class.py",
        "magic/services.py",
        "crafting/services/crafting_service.py",
        "motif/manager.py",
        "memory/memory_manager.py",
        "faction/services/relationship_service.py",
        "economy/economy_manager.py"
    ]
    
    analyzer = FunctionAnalyzer()
    zombie_analysis = {}
    
    print("\n📊 ANALYZING ZOMBIE MONOLITHS")
    print("=" * 70)
    
    for zombie_file in zombie_files:
        zombie_path = systems_dir / zombie_file
        if not zombie_path.exists():
            print(f"⚠️  Zombie file not found: {zombie_file}")
            continue
            
        print(f"\n🧟 Analyzing: {zombie_file}")
        
        # Analyze the zombie file
        analyzer.analyze_file(zombie_path)
        zombie_functions = analyzer.file_functions[str(zombie_path)]
        
        # Find all files in the same system directory
        system_dir = zombie_path.parent
        system_files = []
        
        for py_file in system_dir.rglob("*.py"):
            if py_file != zombie_path and py_file.is_file():
                system_files.append(py_file)
                analyzer.analyze_file(py_file)
        
        print(f"   📄 Functions in zombie: {len(zombie_functions)}")
        print(f"   📁 Other files in system: {len(system_files)}")
        
        # Analyze duplication
        duplicated_signatures = 0
        duplicated_bodies = 0
        unique_functions = []
        
        for func_sig in zombie_functions:
            files_with_sig = analyzer.function_signatures[func_sig]
            if len(files_with_sig) > 1:
                duplicated_signatures += 1
            else:
                unique_functions.append(func_sig)
        
        zombie_analysis[zombie_file] = {
            'path': zombie_path,
            'total_functions': len(zombie_functions),
            'duplicated_signatures': duplicated_signatures,
            'unique_functions': unique_functions,
            'system_files': system_files,
            'size_lines': len(zombie_path.read_text(encoding='utf-8').splitlines()),
            'size_kb': zombie_path.stat().st_size / 1024
        }
        
        print(f"   🔄 Duplicated signatures: {duplicated_signatures}")
        print(f"   ✨ Unique functions: {len(unique_functions)}")
        
        if unique_functions:
            print(f"   📝 Sample unique: {', '.join(unique_functions[:3])}")
            if len(unique_functions) > 3:
                print(f"        ... and {len(unique_functions) - 3} more")
    
    print(f"\n🎯 ZOMBIE REMOVAL STRATEGY")
    print("=" * 70)
    
    total_removable_lines = 0
    total_removable_kb = 0
    safe_removals = []
    archive_candidates = []
    
    for zombie_file, analysis in zombie_analysis.items():
        total_funcs = analysis['total_functions']
        duplicated = analysis['duplicated_signatures'] 
        unique = len(analysis['unique_functions'])
        lines = analysis['size_lines']
        size_kb = analysis['size_kb']
        
        duplication_ratio = duplicated / total_funcs if total_funcs > 0 else 0
        
        print(f"\n📋 {zombie_file}")
        print(f"   📊 {total_funcs} functions ({duplicated} duplicated, {unique} unique)")
        print(f"   📏 {lines:,} lines, {size_kb:.1f} KB")
        print(f"   💯 {duplication_ratio:.1%} duplication ratio")
        
        if duplication_ratio >= 0.9:  # 90%+ duplicated
            print(f"   ✅ SAFE REMOVAL - Almost all functions duplicated")
            safe_removals.append(zombie_file)
            total_removable_lines += lines
            total_removable_kb += size_kb
            
        elif duplication_ratio >= 0.7:  # 70%+ duplicated
            print(f"   📦 ARCHIVE CANDIDATE - Mostly duplicated but has some unique content")
            archive_candidates.append(zombie_file)
            
        else:
            print(f"   ⚠️  REVIEW NEEDED - Significant unique content")
    
    print(f"\n🗑️  REMOVAL SUMMARY")
    print("=" * 70)
    print(f"Safe removals: {len(safe_removals)} files")
    print(f"Archive candidates: {len(archive_candidates)} files")
    print(f"Potential lines removed: {total_removable_lines:,}")
    print(f"Potential size reduction: {total_removable_kb:.1f} KB")
    
    if safe_removals:
        print(f"\n✅ SAFE TO REMOVE:")
        for zombie in safe_removals:
            print(f"   • {zombie}")
    
    if archive_candidates:
        print(f"\n📦 MOVE TO ARCHIVES:")
        for zombie in archive_candidates:
            print(f"   • {zombie}")
    
    return safe_removals, archive_candidates, zombie_analysis

def create_removal_script(safe_removals: List[str], archive_candidates: List[str]):
    """Create a script to safely remove/archive zombie files"""
    
    script_content = '''#!/bin/bash
# 🧟 ZOMBIE CLEANUP SCRIPT
# Auto-generated script to remove/archive zombie monolith files

set -e  # Exit on any error

echo "🧹 STARTING ZOMBIE CLEANUP"
echo "=========================="

# Create archives directory if it doesn't exist
mkdir -p archives/zombie_monoliths
echo "📦 Created archives/zombie_monoliths directory"

'''
    
    if archive_candidates:
        script_content += '''
echo ""
echo "📦 ARCHIVING FILES WITH UNIQUE CONTENT"
echo "======================================"
'''
        for zombie in archive_candidates:
            script_content += f'''
if [ -f "backend/systems/{zombie}" ]; then
    echo "📦 Archiving {zombie}"
    cp "backend/systems/{zombie}" "archives/zombie_monoliths/$(basename {zombie})"
    rm "backend/systems/{zombie}"
    echo "   ✅ Moved to archives"
else
    echo "   ⚠️  File not found: {zombie}"
fi
'''
    
    if safe_removals:
        script_content += '''
echo ""
echo "🗑️  REMOVING FULLY DUPLICATED FILES"
echo "=================================="
'''
        for zombie in safe_removals:
            script_content += f'''
if [ -f "backend/systems/{zombie}" ]; then
    echo "🗑️  Removing {zombie}"
    rm "backend/systems/{zombie}"
    echo "   ✅ Deleted (functions exist elsewhere)"
else
    echo "   ⚠️  File not found: {zombie}"
fi
'''
    
    script_content += '''
echo ""
echo "✅ ZOMBIE CLEANUP COMPLETE"
echo "========================="
echo "📊 Summary:"
'''
    
    script_content += f'echo "   📦 Archived: {len(archive_candidates)} files"\n'
    script_content += f'echo "   🗑️  Removed: {len(safe_removals)} files"\n'
    
    script_content += '''
echo ""
echo "🔍 Next steps:"
echo "   1. Run tests to ensure nothing is broken"
echo "   2. Check for any import errors"  
echo "   3. Update documentation if needed"
echo "   4. Commit changes with detailed message"
'''
    
    # Write the script
    script_path = Path("cleanup_zombies.sh")
    script_path.write_text(script_content)
    script_path.chmod(0o755)  # Make executable
    
    print(f"\n📜 CLEANUP SCRIPT CREATED: {script_path}")
    print("   Run with: ./cleanup_zombies.sh")

if __name__ == "__main__":
    safe_removals, archive_candidates, analysis = analyze_zombie_duplication()
    
    if safe_removals or archive_candidates:
        print(f"\n🔧 ADDITIONAL REFACTORING OPPORTUNITIES")
        print("=" * 70)
        
        # Suggest other improvements
        print("1. 📁 Directory consolidation (already planned)")
        print("2. 🔄 Import statement cleanup after file removal")
        print("3. 📝 Documentation updates for removed modules")
        print("4. 🧪 Test file cleanup for removed modules")
        print("5. 🔍 Search for dead imports/references")
        
        create_removal_script(safe_removals, archive_candidates)
    else:
        print("\n🤷 No clear zombie files identified for removal") 