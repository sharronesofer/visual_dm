"""
Feat-to-Feat Prerequisite Adjustment Script

This script analyzes and adjusts feat-to-feat prerequisites to create more
coherent progression paths and improve game balance.
"""

import sys
import os
import json
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict
import csv
import copy

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.feats import FeatManager, PowerLevel, Feat, FeatType
from models.feat_templates import ALL_FEATS
from models.feat_progressions import PROGRESSION_PATHS, ProgressionCategory

def analyze_feat_prerequisite_relationships():
    """Analyze the current feat prerequisite relationships"""
    
    # Track direct prerequisite relationships
    prereq_graph = defaultdict(list)  # feat_id -> list of feats that require it
    depends_on_graph = defaultdict(list)  # feat_id -> list of feats it requires
    
    # Build dependency graphs
    for feat_id, feat in ALL_FEATS.items():
        if feat.prerequisites.feat_requirements:
            for prereq_id in feat.prerequisites.feat_requirements:
                prereq_graph[prereq_id].append(feat_id)
                depends_on_graph[feat_id].append(prereq_id)
    
    # Find orphaned feats (no prerequisites and not a prerequisite for anything)
    orphaned_feats = []
    for feat_id in ALL_FEATS:
        if feat_id not in prereq_graph and not depends_on_graph.get(feat_id):
            orphaned_feats.append(feat_id)
    
    # Find gateway feats (feats that are prerequisites for many others)
    gateway_feats = [(feat_id, len(dependent_feats)) 
                     for feat_id, dependent_feats in prereq_graph.items() 
                     if len(dependent_feats) >= 3]
    gateway_feats.sort(key=lambda x: x[1], reverse=True)
    
    # Find terminal feats (feats that have prerequisites but aren't prerequisites for anything else)
    terminal_feats = []
    for feat_id in depends_on_graph:
        if feat_id not in prereq_graph:
            terminal_feats.append(feat_id)
    
    # Find feats with circular dependencies
    circular_dependencies = find_circular_dependencies(depends_on_graph)
    
    # Print analysis results
    print("\n===== FEAT PREREQUISITE RELATIONSHIPS =====")
    print(f"Total feats: {len(ALL_FEATS)}")
    print(f"Feats with prerequisites: {len(depends_on_graph)}")
    print(f"Feats that are prerequisites: {len(prereq_graph)}")
    print(f"Orphaned feats: {len(orphaned_feats)}")
    print(f"Terminal feats: {len(terminal_feats)}")
    print(f"Circular dependencies found: {len(circular_dependencies)}")
    
    print("\n===== TOP GATEWAY FEATS =====")
    for feat_id, count in gateway_feats[:10]:
        print(f"{ALL_FEATS[feat_id].name} ({feat_id}): Required by {count} feats")
    
    if circular_dependencies:
        print("\n===== CIRCULAR DEPENDENCIES =====")
        for cycle in circular_dependencies:
            print(" -> ".join([ALL_FEATS[feat_id].name for feat_id in cycle]))
    
    # Create a CSV report of relationships
    with open('feat_relationships.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Feat ID', 'Feat Name', 'Prerequisites', 'Required By'])
        
        for feat_id, feat in ALL_FEATS.items():
            writer.writerow([
                feat_id,
                feat.name,
                ", ".join(depends_on_graph.get(feat_id, [])),
                ", ".join(prereq_graph.get(feat_id, []))
            ])
    
    print(f"\nFeat relationships saved to feat_relationships.csv")
    
    return {
        "prereq_graph": dict(prereq_graph),
        "depends_on_graph": dict(depends_on_graph),
        "orphaned_feats": orphaned_feats,
        "gateway_feats": gateway_feats,
        "terminal_feats": terminal_feats,
        "circular_dependencies": circular_dependencies
    }

def find_circular_dependencies(depends_on_graph):
    """Find circular dependencies in the feat prerequisite graph using depth-first search"""
    
    circular_dependencies = []
    visited = set()
    path = []
    
    def dfs(feat_id):
        if feat_id in path:
            # Found a cycle
            cycle_start = path.index(feat_id)
            circular_dependencies.append(path[cycle_start:] + [feat_id])
            return True
            
        if feat_id in visited:
            return False
            
        visited.add(feat_id)
        path.append(feat_id)
        
        for prereq_id in depends_on_graph.get(feat_id, []):
            if dfs(prereq_id):
                return True
                
        path.pop()
        return False
    
    # Check each feat as a potential starting point
    for feat_id in depends_on_graph:
        if feat_id not in visited:
            dfs(feat_id)
    
    return circular_dependencies

def analyze_progression_path_completeness():
    """Analyze if the defined progression paths have consistent feat prerequisites"""
    
    path_issues = []
    
    for path_name, progression in PROGRESSION_PATHS.items():
        feat_ids = progression.feat_ids
        
        # Check each feat in the path (except the first one)
        for i in range(1, len(feat_ids)):
            current_feat_id = feat_ids[i]
            previous_feat_id = feat_ids[i-1]
            
            # Get the current feat
            if current_feat_id in ALL_FEATS:
                current_feat = ALL_FEATS[current_feat_id]
                
                # Check if previous feat is a prerequisite
                if not current_feat.prerequisites.feat_requirements or previous_feat_id not in current_feat.prerequisites.feat_requirements:
                    path_issues.append({
                        "path_name": path_name,
                        "current_feat": current_feat_id,
                        "previous_feat": previous_feat_id,
                        "issue": "Missing prerequisite relationship"
                    })
    
    # Print issues
    print("\n===== PROGRESSION PATH ISSUES =====")
    for issue in path_issues:
        print(f"Path '{issue['path_name']}': {ALL_FEATS[issue['current_feat']].name} should require {ALL_FEATS[issue['previous_feat']].name}")
    
    # Save issues to CSV
    with open('progression_path_issues.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["path_name", "current_feat", "previous_feat", "issue"])
        writer.writeheader()
        writer.writerows(path_issues)
    
    print(f"Progression path issues saved to progression_path_issues.csv")
    
    return path_issues

def suggest_feat_prerequisite_adjustments(relationship_analysis, path_issues):
    """Suggest adjustments to feat prerequisites based on analysis and progression paths"""
    
    adjustments = []
    
    # Fix circular dependencies
    for cycle in relationship_analysis["circular_dependencies"]:
        # Find the feat with the highest level requirement to break
        highest_level_feat = max(cycle, key=lambda feat_id: ALL_FEATS[feat_id].prerequisites.level_requirement)
        
        # Find what it depends on in the cycle
        cycle_index = cycle.index(highest_level_feat)
        dependency_to_remove = cycle[(cycle_index - 1) % len(cycle)]
        
        adjustments.append({
            "feat_id": highest_level_feat,
            "adjustment_type": "remove_prerequisite",
            "dependency": dependency_to_remove,
            "reason": f"Breaking circular dependency in cycle: {' -> '.join([ALL_FEATS[f].name for f in cycle])}"
        })
    
    # Fix progression path issues
    for issue in path_issues:
        adjustments.append({
            "feat_id": issue["current_feat"],
            "adjustment_type": "add_prerequisite",
            "dependency": issue["previous_feat"],
            "reason": f"Completing progression path '{issue['path_name']}'"
        })
    
    # Suggest integration for orphaned feats
    orphaned_feats = relationship_analysis["orphaned_feats"]
    
    # Only process some orphaned feats to avoid overwhelming the output
    for orphaned_feat_id in orphaned_feats[:min(20, len(orphaned_feats))]:
        orphaned_feat = ALL_FEATS[orphaned_feat_id]
        
        # Try to find a suitable existing feat that this could depend on
        best_match = None
        best_match_score = 0
        
        for existing_id, existing_feat in ALL_FEATS.items():
            if existing_id == orphaned_feat_id:
                continue
                
            # Skip if existing feat has a higher level requirement
            if existing_feat.prerequisites.level_requirement >= orphaned_feat.prerequisites.level_requirement:
                continue
                
            # Calculate match score based on shared tags
            score = 0
            if orphaned_feat.tags and existing_feat.tags:
                shared_tags = set(orphaned_feat.tags) & set(existing_feat.tags)
                score += len(shared_tags) * 2
            
            # Bonus for appropriate level gap
            level_gap = orphaned_feat.prerequisites.level_requirement - existing_feat.prerequisites.level_requirement
            if 1 <= level_gap <= 4:
                score += 3
                
            # Bonus for same feat type
            if orphaned_feat.feat_type == existing_feat.feat_type:
                score += 2
                
            if score > best_match_score:
                best_match_score = score
                best_match = existing_id
        
        # If we found a reasonable match
        if best_match_score >= 4 and best_match:
            adjustments.append({
                "feat_id": orphaned_feat_id,
                "adjustment_type": "add_prerequisite",
                "dependency": best_match,
                "reason": f"Integrating orphaned feat into progression (match score: {best_match_score})"
            })
    
    # Print suggested adjustments
    print("\n===== SUGGESTED FEAT PREREQUISITE ADJUSTMENTS =====")
    for adjustment in adjustments:
        feat_name = ALL_FEATS[adjustment["feat_id"]].name
        dependency_name = ALL_FEATS[adjustment["dependency"]].name
        
        if adjustment["adjustment_type"] == "add_prerequisite":
            print(f"Add: {feat_name} should require {dependency_name}")
        else:
            print(f"Remove: {feat_name} should no longer require {dependency_name}")
        print(f"  Reason: {adjustment['reason']}\n")
    
    # Save adjustments to CSV
    with open('suggested_prerequisite_adjustments.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["feat_id", "feat_name", "adjustment_type", "dependency", "dependency_name", "reason"])
        writer.writeheader()
        
        for adjustment in adjustments:
            writer.writerow({
                "feat_id": adjustment["feat_id"],
                "feat_name": ALL_FEATS[adjustment["feat_id"]].name,
                "adjustment_type": adjustment["adjustment_type"],
                "dependency": adjustment["dependency"],
                "dependency_name": ALL_FEATS[adjustment["dependency"]].name,
                "reason": adjustment["reason"]
            })
    
    print(f"Suggested adjustments saved to suggested_prerequisite_adjustments.csv")
    
    return adjustments

def apply_prerequisite_adjustments(adjustments):
    """Apply the suggested adjustments to create an adjusted feat set"""
    
    adjusted_feats = copy.deepcopy(ALL_FEATS)
    
    for adjustment in adjustments:
        feat_id = adjustment["feat_id"]
        dependency = adjustment["dependency"]
        
        if adjustment["adjustment_type"] == "add_prerequisite":
            # Add prerequisite
            if dependency not in adjusted_feats[feat_id].prerequisites.feat_requirements:
                adjusted_feats[feat_id].prerequisites.feat_requirements.append(dependency)
        else:  # remove_prerequisite
            # Remove prerequisite
            if dependency in adjusted_feats[feat_id].prerequisites.feat_requirements:
                adjusted_feats[feat_id].prerequisites.feat_requirements.remove(dependency)
    
    return adjusted_feats

def generate_adjusted_feats(adjusted_feats, output_file="adjusted_feats.py"):
    """Generate a Python file with the adjusted feat templates"""
    
    # Generate Python code
    code = """\"\"\"
Adjusted Feat Templates

This file contains feat templates with adjusted prerequisites
for better progression paths and game balance.
\"\"\"

from typing import Dict, List
from app.core.models.feats import Feat, FeatType, TriggerType, ResourceType, FeatPrerequisite, FeatResource, FeatEffect, PowerLevel
from app.core.models.effects import StatModifierEffect, DamageModifierEffect

# Adjusted feat templates
ADJUSTED_FEATS: Dict[str, Feat] = {
"""
    
    # Add each feat definition
    for feat_id, feat in adjusted_feats.items():
        code += f"""    "{feat_id}": Feat(
        id="{feat.id}",
        name="{feat.name}",
        description="{feat.description}",
        feat_type=FeatType.{feat.feat_type.name},
"""
        
        # Add prerequisites
        code += "        prerequisites=FeatPrerequisite(\n"
        
        if feat.prerequisites.stat_requirements:
            stats_str = ", ".join([f'"{k}": {v}' for k, v in feat.prerequisites.stat_requirements.items()])
            code += f"            stat_requirements={{{stats_str}}},\n"
        
        code += f"            level_requirement={feat.prerequisites.level_requirement},\n"
        
        if feat.prerequisites.feat_requirements:
            feats_str = ", ".join([f'"{f}"' for f in feat.prerequisites.feat_requirements])
            code += f"            feat_requirements=[{feats_str}],\n"
        
        if feat.prerequisites.class_requirements:
            classes_str = ", ".join([f'"{c}"' for c in feat.prerequisites.class_requirements])
            code += f"            class_requirements=[{classes_str}],\n"
        
        if feat.prerequisites.race_requirements:
            races_str = ", ".join([f'"{r}"' for r in feat.prerequisites.race_requirements])
            code += f"            race_requirements=[{races_str}],\n"
        
        if feat.prerequisites.skill_requirements:
            skills_str = ", ".join([f'"{k}": {v}' for k, v in feat.prerequisites.skill_requirements.items()])
            code += f"            skill_requirements={{{skills_str}}},\n"
        
        if hasattr(feat.prerequisites, "power_level"):
            code += f"            power_level=PowerLevel.{feat.prerequisites.power_level.name},\n"
        
        code += "        ),\n"
        
        # Add effects placeholder
        code += "        effects=[],  # Effects would need to be properly defined\n"
        
        # Add trigger if present
        if feat.trigger:
            code += f"        trigger=TriggerType.{feat.trigger.name},\n"
        
        # Add resource if present
        if feat.resource:
            code += f"        resource=FeatResource(type=ResourceType.{feat.resource.type.name}, amount={feat.resource.amount}),\n"
        
        # Add other properties
        code += f"        stacking={str(feat.stacking)},\n"
        
        if feat.tags:
            tags_str = ", ".join([f'"{t}"' for t in feat.tags])
            code += f"        tags=[{tags_str}],\n"
        
        code += "    ),\n"
    
    # Close the dictionary and module
    code += "}\n"
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(code)
    
    print(f"Adjusted feats written to {output_file}")
    return adjusted_feats

def export_adjustment_comparison(original_feats, adjusted_feats, output_file="prerequisite_comparison.csv"):
    """Create a CSV comparing original and adjusted feat prerequisites"""
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Feat ID', 'Feat Name', 'Original Prerequisites', 'Adjusted Prerequisites', 'Changes'
        ])
        
        for feat_id, adjusted_feat in adjusted_feats.items():
            original_feat = original_feats[feat_id]
            
            # Get original and adjusted prerequisites
            original_prereqs = original_feat.prerequisites.feat_requirements or []
            adjusted_prereqs = adjusted_feat.prerequisites.feat_requirements or []
            
            # Identify changes
            added = set(adjusted_prereqs) - set(original_prereqs)
            removed = set(original_prereqs) - set(adjusted_prereqs)
            
            changes = []
            if added:
                changes.append(f"Added: {', '.join([ALL_FEATS[f].name for f in added])}")
            if removed:
                changes.append(f"Removed: {', '.join([ALL_FEATS[f].name for f in removed])}")
            
            # Write row
            writer.writerow([
                feat_id,
                original_feat.name,
                ", ".join([f"{p} ({ALL_FEATS[p].name})" for p in original_prereqs]),
                ", ".join([f"{p} ({ALL_FEATS[p].name})" for p in adjusted_prereqs]),
                "; ".join(changes)
            ])
    
    print(f"Prerequisite comparison exported to {output_file}")

if __name__ == "__main__":
    print("Analyzing feat prerequisite relationships...")
    relationships = analyze_feat_prerequisite_relationships()
    
    print("\nAnalyzing progression path completeness...")
    path_issues = analyze_progression_path_completeness()
    
    print("\nGenerating prerequisite adjustment suggestions...")
    adjustments = suggest_feat_prerequisite_adjustments(relationships, path_issues)
    
    print("\nApplying prerequisite adjustments...")
    adjusted_feats = apply_prerequisite_adjustments(adjustments)
    
    print("\nGenerating adjusted feat templates...")
    generate_adjusted_feats(adjusted_feats)
    
    print("\nExporting comparison report...")
    export_adjustment_comparison(ALL_FEATS, adjusted_feats)
    
    print("\nPrerequisite adjustment complete!") 