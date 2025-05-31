#!/usr/bin/env python3

import os
import re
import hashlib
import ast
from collections import defaultdict, Counter
from pathlib import Path
from difflib import SequenceMatcher
import json
from typing import Dict, List, Tuple, Set
import sys

class ComprehensiveDuplicationVerifier:
    def __init__(self, backend_dir):
        self.backend_dir = Path(backend_dir)
        self.verification_results = {
            'exact_file_duplicates': [],
            'exact_function_duplicates': [],
            'exact_class_duplicates': [],
            'structural_duplicates': [],
            'semantic_duplicates': [],
            'high_similarity_pairs': [],
            'total_files': 0,
            'total_functions': 0,
            'total_classes': 0,
            'unique_content_ratio': 0.0,
            'duplication_score': 0.0,
            'is_fully_deduplicated': False
        }
    
    def calculate_file_hash(self, file_path):
        """Calculate multiple types of hashes for a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                'exact_hash': hashlib.sha256(content.encode()).hexdigest(),
                'normalized_hash': hashlib.sha256(self.normalize_content(content).encode()).hexdigest(),
                'structure_hash': self.get_structure_hash(content),
                'semantic_hash': self.get_semantic_hash(content)
            }
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None
    
    def normalize_content(self, content):
        """Aggressively normalize content for comparison"""
        # Remove all comments
        content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'""".*?"""', '', content, flags=re.DOTALL)
        content = re.sub(r"'''.*?'''", '', content, flags=re.DOTALL)
        
        # Remove all whitespace variations
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\s*([{}()[\],;:=+\-*/])\s*', r'\1', content)
        
        # Normalize all string literals
        content = re.sub(r'"[^"]*"', '"STR"', content)
        content = re.sub(r"'[^']*'", "'STR'", content)
        
        # Normalize all numbers
        content = re.sub(r'\b\d+\.?\d*\b', 'NUM', content)
        
        # Sort import statements to ignore order
        lines = content.split('\n')
        imports = []
        other_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                imports.append(stripped)
            else:
                other_lines.append(line)
        
        imports.sort()
        return '\n'.join(imports + other_lines).strip()
    
    def get_structure_hash(self, content):
        """Get hash based on AST structure"""
        try:
            tree = ast.parse(content)
            # Remove all names and literals, keep only structure
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    node.id = 'VAR'
                elif isinstance(node, (ast.Str, ast.Constant)):
                    if hasattr(node, 'value'):
                        if isinstance(node.value, str):
                            node.value = 'STR'
                        elif isinstance(node.value, (int, float)):
                            node.value = 0
            
            structure = ast.dump(tree, annotate_fields=False, include_attributes=False)
            return hashlib.sha256(structure.encode()).hexdigest()
        except:
            # Fallback for unparseable Python
            return hashlib.sha256(self.normalize_content(content).encode()).hexdigest()
    
    def get_semantic_hash(self, content):
        """Get hash based on semantic meaning"""
        # Extract all function and class signatures
        signatures = []
        
        # Function signatures
        func_matches = re.findall(r'def\s+(\w+)\s*\([^)]*\):', content)
        signatures.extend(sorted(func_matches))
        
        # Class signatures
        class_matches = re.findall(r'class\s+(\w+)(?:\([^)]*\))?:', content)
        signatures.extend(sorted(class_matches))
        
        # Variable assignments (simplified)
        var_matches = re.findall(r'(\w+)\s*=', content)
        var_counter = Counter(var_matches)
        signatures.extend(sorted(var_counter.keys()))
        
        semantic_signature = '|'.join(signatures)
        return hashlib.sha256(semantic_signature.encode()).hexdigest()
    
    def extract_all_functions(self, content):
        """Extract all function definitions with normalization"""
        functions = []
        
        # Use AST for reliable function extraction
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Get function source
                    func_lines = content.split('\n')[node.lineno-1:node.end_lineno]
                    func_source = '\n'.join(func_lines)
                    
                    # Create normalized version
                    normalized = self.normalize_content(func_source)
                    
                    functions.append({
                        'name': node.name,
                        'original': func_source,
                        'normalized': normalized,
                        'exact_hash': hashlib.sha256(func_source.encode()).hexdigest(),
                        'normalized_hash': hashlib.sha256(normalized.encode()).hexdigest(),
                        'signature': f"{node.name}({len(node.args.args)})"
                    })
        except:
            # Fallback regex method
            func_pattern = r'(def\s+\w+\s*\([^)]*\):.*?)(?=\ndef|\nclass|\n\n|\Z)'
            matches = re.findall(func_pattern, content, re.DOTALL)
            
            for match in matches:
                func_name = re.search(r'def\s+(\w+)', match)
                if func_name:
                    normalized = self.normalize_content(match)
                    functions.append({
                        'name': func_name.group(1),
                        'original': match,
                        'normalized': normalized,
                        'exact_hash': hashlib.sha256(match.encode()).hexdigest(),
                        'normalized_hash': hashlib.sha256(normalized.encode()).hexdigest(),
                        'signature': func_name.group(0)
                    })
        
        return functions
    
    def extract_all_classes(self, content):
        """Extract all class definitions with normalization"""
        classes = []
        
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Get class source
                    class_lines = content.split('\n')[node.lineno-1:node.end_lineno]
                    class_source = '\n'.join(class_lines)
                    
                    normalized = self.normalize_content(class_source)
                    
                    classes.append({
                        'name': node.name,
                        'original': class_source,
                        'normalized': normalized,
                        'exact_hash': hashlib.sha256(class_source.encode()).hexdigest(),
                        'normalized_hash': hashlib.sha256(normalized.encode()).hexdigest()
                    })
        except:
            # Fallback regex method
            class_pattern = r'(class\s+\w+.*?)(?=\nclass|\ndef|\n\n|\Z)'
            matches = re.findall(class_pattern, content, re.DOTALL)
            
            for match in matches:
                class_name = re.search(r'class\s+(\w+)', match)
                if class_name:
                    normalized = self.normalize_content(match)
                    classes.append({
                        'name': class_name.group(1),
                        'original': match,
                        'normalized': normalized,
                        'exact_hash': hashlib.sha256(match.encode()).hexdigest(),
                        'normalized_hash': hashlib.sha256(normalized.encode()).hexdigest()
                    })
        
        return classes
    
    def calculate_similarity_score(self, content1, content2):
        """Calculate similarity score between two content pieces"""
        # Multiple similarity metrics
        exact_similarity = 1.0 if content1 == content2 else 0.0
        
        # Sequence matcher on normalized content
        norm1 = self.normalize_content(content1)
        norm2 = self.normalize_content(content2)
        sequence_similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Line-by-line similarity
        lines1 = set(line.strip() for line in content1.split('\n') if line.strip())
        lines2 = set(line.strip() for line in content2.split('\n') if line.strip())
        
        if lines1 or lines2:
            line_similarity = len(lines1.intersection(lines2)) / len(lines1.union(lines2))
        else:
            line_similarity = 1.0
        
        # Combined score
        combined_score = (exact_similarity * 0.5 + sequence_similarity * 0.3 + line_similarity * 0.2)
        
        return {
            'exact': exact_similarity,
            'sequence': sequence_similarity,
            'line': line_similarity,
            'combined': combined_score
        }
    
    def verify_no_file_duplicates(self):
        """Verify no duplicate files exist"""
        print("🔍 Verifying no file duplicates...")
        
        python_files = list(self.backend_dir.rglob("*.py"))
        self.verification_results['total_files'] = len(python_files)
        
        file_hashes = defaultdict(list)
        
        for file_path in python_files:
            hashes = self.calculate_file_hash(file_path)
            if hashes:
                # Check all hash types
                file_hashes[hashes['exact_hash']].append(('exact', file_path))
                file_hashes[hashes['normalized_hash']].append(('normalized', file_path))
                file_hashes[hashes['structure_hash']].append(('structure', file_path))
                file_hashes[hashes['semantic_hash']].append(('semantic', file_path))
        
        # Find duplicates
        for hash_value, file_list in file_hashes.items():
            if len(file_list) > 1:
                # Group by hash type
                by_type = defaultdict(list)
                for hash_type, file_path in file_list:
                    by_type[hash_type].append(file_path)
                
                for hash_type, files in by_type.items():
                    if len(files) > 1:
                        if hash_type == 'exact':
                            self.verification_results['exact_file_duplicates'].append(files)
                        elif hash_type in ['normalized', 'structure', 'semantic']:
                            self.verification_results['structural_duplicates'].append((hash_type, files))
        
        exact_dupes = len(self.verification_results['exact_file_duplicates'])
        struct_dupes = len(self.verification_results['structural_duplicates'])
        
        print(f"   📊 Files analyzed: {len(python_files)}")
        print(f"   🔴 Exact file duplicates: {exact_dupes}")
        print(f"   🟡 Structural duplicates: {struct_dupes}")
        
        return exact_dupes == 0 and struct_dupes == 0
    
    def verify_no_function_duplicates(self):
        """Verify no duplicate functions exist"""
        print("🔍 Verifying no function duplicates...")
        
        all_functions = []
        python_files = list(self.backend_dir.rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                functions = self.extract_all_functions(content)
                for func in functions:
                    func['file'] = file_path
                    all_functions.append(func)
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        self.verification_results['total_functions'] = len(all_functions)
        
        # Group by hashes
        exact_func_hashes = defaultdict(list)
        norm_func_hashes = defaultdict(list)
        
        for func in all_functions:
            exact_func_hashes[func['exact_hash']].append(func)
            norm_func_hashes[func['normalized_hash']].append(func)
        
        # Find exact duplicates
        exact_dupes = 0
        for hash_val, funcs in exact_func_hashes.items():
            if len(funcs) > 1:
                self.verification_results['exact_function_duplicates'].append(funcs)
                exact_dupes += len(funcs) - 1
        
        # Find normalized duplicates
        norm_dupes = 0
        for hash_val, funcs in norm_func_hashes.items():
            if len(funcs) > 1:
                # Check if not already in exact duplicates
                exact_hashes = {f['exact_hash'] for f in funcs}
                if len(exact_hashes) > 1:  # Different exact hashes but same normalized
                    self.verification_results['semantic_duplicates'].append(funcs)
                    norm_dupes += len(funcs) - 1
        
        print(f"   📊 Functions analyzed: {len(all_functions)}")
        print(f"   🔴 Exact function duplicates: {exact_dupes}")
        print(f"   🟡 Semantic function duplicates: {norm_dupes}")
        
        return exact_dupes == 0 and norm_dupes == 0
    
    def verify_no_class_duplicates(self):
        """Verify no duplicate classes exist"""
        print("🔍 Verifying no class duplicates...")
        
        all_classes = []
        python_files = list(self.backend_dir.rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                classes = self.extract_all_classes(content)
                for cls in classes:
                    cls['file'] = file_path
                    all_classes.append(cls)
                    
            except Exception as e:
                continue
        
        self.verification_results['total_classes'] = len(all_classes)
        
        # Group by hashes
        exact_class_hashes = defaultdict(list)
        norm_class_hashes = defaultdict(list)
        
        for cls in all_classes:
            exact_class_hashes[cls['exact_hash']].append(cls)
            norm_class_hashes[cls['normalized_hash']].append(cls)
        
        # Find exact duplicates
        exact_dupes = 0
        for hash_val, classes in exact_class_hashes.items():
            if len(classes) > 1:
                self.verification_results['exact_class_duplicates'].append(classes)
                exact_dupes += len(classes) - 1
        
        # Find normalized duplicates
        norm_dupes = 0
        for hash_val, classes in norm_class_hashes.items():
            if len(classes) > 1:
                exact_hashes = {c['exact_hash'] for c in classes}
                if len(exact_hashes) > 1:
                    self.verification_results['semantic_duplicates'].append(classes)
                    norm_dupes += len(classes) - 1
        
        print(f"   📊 Classes analyzed: {len(all_classes)}")
        print(f"   🔴 Exact class duplicates: {exact_dupes}")
        print(f"   🟡 Semantic class duplicates: {norm_dupes}")
        
        return exact_dupes == 0 and norm_dupes == 0
    
    def find_high_similarity_pairs(self):
        """Find files with high similarity that might be near-duplicates"""
        print("🔍 Finding high similarity pairs...")
        
        python_files = list(self.backend_dir.rglob("*.py"))
        file_contents = {}
        
        # Read all files
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_contents[file_path] = f.read()
            except:
                continue
        
        high_similarity_pairs = []
        files = list(file_contents.keys())
        
        # Compare all pairs (this might be slow for large codebases)
        print(f"   Comparing {len(files)} files pairwise...")
        
        for i in range(len(files)):
            if i % 50 == 0:
                print(f"   Progress: {i}/{len(files)}")
                
            for j in range(i + 1, len(files)):
                file1, file2 = files[i], files[j]
                content1, content2 = file_contents[file1], file_contents[file2]
                
                # Skip very small files
                if len(content1.strip()) < 100 or len(content2.strip()) < 100:
                    continue
                
                similarity = self.calculate_similarity_score(content1, content2)
                
                # Flag high similarity (>80% but not exact)
                if 0.8 <= similarity['combined'] < 1.0:
                    high_similarity_pairs.append({
                        'file1': file1,
                        'file2': file2,
                        'similarity': similarity
                    })
        
        self.verification_results['high_similarity_pairs'] = high_similarity_pairs
        
        print(f"   🟠 High similarity pairs found: {len(high_similarity_pairs)}")
        
        return len(high_similarity_pairs) == 0
    
    def calculate_uniqueness_metrics(self):
        """Calculate overall uniqueness metrics"""
        print("📊 Calculating uniqueness metrics...")
        
        # Calculate duplication score
        total_items = (self.verification_results['total_files'] + 
                      self.verification_results['total_functions'] + 
                      self.verification_results['total_classes'])
        
        total_duplicates = (len(self.verification_results['exact_file_duplicates']) +
                           len(self.verification_results['exact_function_duplicates']) +
                           len(self.verification_results['exact_class_duplicates']) +
                           len(self.verification_results['structural_duplicates']) +
                           len(self.verification_results['semantic_duplicates']) +
                           len(self.verification_results['high_similarity_pairs']))
        
        if total_items > 0:
            uniqueness_ratio = 1.0 - (total_duplicates / total_items)
            duplication_score = (total_duplicates / total_items) * 100
        else:
            uniqueness_ratio = 1.0
            duplication_score = 0.0
        
        self.verification_results['unique_content_ratio'] = uniqueness_ratio
        self.verification_results['duplication_score'] = duplication_score
        
        print(f"   📈 Unique content ratio: {uniqueness_ratio:.4f} ({uniqueness_ratio*100:.2f}%)")
        print(f"   📉 Duplication score: {duplication_score:.2f}%")
        
        return uniqueness_ratio >= 0.98  # 98% unique content
    
    def run_comprehensive_verification(self):
        """Run complete verification and return definitive answer"""
        print("🔬 COMPREHENSIVE DUPLICATION VERIFICATION")
        print("=" * 70)
        
        # Run all verification checks
        no_file_dupes = self.verify_no_file_duplicates()
        no_func_dupes = self.verify_no_function_duplicates()
        no_class_dupes = self.verify_no_class_duplicates()
        no_high_similarity = self.find_high_similarity_pairs()
        high_uniqueness = self.calculate_uniqueness_metrics()
        
        # Determine if fully deduplicated
        is_fully_deduplicated = (no_file_dupes and no_func_dupes and 
                               no_class_dupes and no_high_similarity and 
                               high_uniqueness)
        
        self.verification_results['is_fully_deduplicated'] = is_fully_deduplicated
        
        # Generate final report
        print("\n" + "=" * 70)
        print("🎯 FINAL VERIFICATION RESULTS")
        print("=" * 70)
        
        print(f"📁 Total files analyzed: {self.verification_results['total_files']}")
        print(f"🔧 Total functions analyzed: {self.verification_results['total_functions']}")
        print(f"🏗️  Total classes analyzed: {self.verification_results['total_classes']}")
        
        print(f"\n🔍 DUPLICATION DETECTION RESULTS:")
        print(f"   Exact file duplicates: {len(self.verification_results['exact_file_duplicates'])}")
        print(f"   Exact function duplicates: {len(self.verification_results['exact_function_duplicates'])}")
        print(f"   Exact class duplicates: {len(self.verification_results['exact_class_duplicates'])}")
        print(f"   Structural duplicates: {len(self.verification_results['structural_duplicates'])}")
        print(f"   Semantic duplicates: {len(self.verification_results['semantic_duplicates'])}")
        print(f"   High similarity pairs: {len(self.verification_results['high_similarity_pairs'])}")
        
        print(f"\n📊 UNIQUENESS METRICS:")
        print(f"   Unique content ratio: {self.verification_results['unique_content_ratio']:.4f}")
        print(f"   Duplication score: {self.verification_results['duplication_score']:.2f}%")
        
        print(f"\n🎉 FINAL VERDICT:")
        if is_fully_deduplicated:
            print("✅ CODEBASE IS FULLY DEDUPLICATED!")
            print("   No duplicates detected with 100% confidence.")
            print("   Your codebase has achieved maximum uniqueness.")
        else:
            print("❌ CODEBASE STILL CONTAINS DUPLICATES")
            print("   Remaining duplicates detected. Further cleanup needed.")
            
            # Show specific issues
            if self.verification_results['exact_file_duplicates']:
                print(f"   • {len(self.verification_results['exact_file_duplicates'])} exact file duplicates")
            if self.verification_results['exact_function_duplicates']:
                print(f"   • {len(self.verification_results['exact_function_duplicates'])} exact function duplicates")
            if self.verification_results['high_similarity_pairs']:
                print(f"   • {len(self.verification_results['high_similarity_pairs'])} high similarity pairs")
        
        return self.verification_results
    
    def save_detailed_report(self, output_file="duplication_verification_report.json"):
        """Save detailed verification report"""
        # Convert Path objects to strings for JSON serialization
        serializable_results = {}
        for key, value in self.verification_results.items():
            if isinstance(value, list):
                serializable_results[key] = []
                for item in value:
                    if isinstance(item, Path):
                        serializable_results[key].append(str(item))
                    elif isinstance(item, dict):
                        serialized_item = {}
                        for k, v in item.items():
                            if isinstance(v, Path):
                                serialized_item[k] = str(v)
                            else:
                                serialized_item[k] = v
                        serializable_results[key].append(serialized_item)
                    else:
                        serializable_results[key].append(item)
            else:
                serializable_results[key] = value
        
        with open(output_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {output_file}")


def main():
    backend_dir = "backend/systems"
    
    if not os.path.exists(backend_dir):
        print(f"❌ Backend directory not found: {backend_dir}")
        sys.exit(1)
    
    verifier = ComprehensiveDuplicationVerifier(backend_dir)
    results = verifier.run_comprehensive_verification()
    verifier.save_detailed_report()
    
    # Exit with appropriate code
    if results['is_fully_deduplicated']:
        print(f"\n🎊 SUCCESS: Codebase verification complete!")
        sys.exit(0)
    else:
        print(f"\n⚠️  WARNING: Duplicates still exist!")
        sys.exit(1)


if __name__ == "__main__":
    main() 