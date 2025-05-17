"""
Feat Analysis Script

This script analyzes the current feats in the system and categorizes them
by type, power level, and prerequisite complexity to help with rebalancing.
"""

import sys
import os
import json
from typing import Dict, List, Tuple, Set
from collections import defaultdict
import csv

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.feats import FeatManager, PowerLevel, Feat, FeatType, TriggerType
from models.feat_templates import ALL_FEATS

def analyze_feat_distribution():
    """Analyze the distribution of feats by type, power level, etc."""
    
    # Counters for various categorizations
    feat_types = defaultdict(int)
    trigger_types = defaultdict(int)
    power_levels = defaultdict(int)
    complexity_ranges = {
        "Very Simple (0-5)": 0,
        "Simple (6-10)": 0,
        "Moderate (11-15)": 0,
        "Complex (16-20)": 0,
        "Very Complex (21+)": 0
    }
    
    # Tags and prerequisites for similarity analysis
    feat_by_tags = defaultdict(list)
    prerequisites_by_type = {
        "stat": defaultdict(list),
        "level": defaultdict(list),
        "feat": defaultdict(list),
        "class": defaultdict(list),
        "race": defaultdict(list),
        "skill": defaultdict(list),
    }
    
    # Calculate complexities for each feat
    feat_complexities = {}
    for feat_id, feat in ALL_FEATS.items():
        complexity = feat.prerequisites.get_prerequisite_complexity()
        feat_complexities[feat_id] = complexity
        
        # Add to type counters
        feat_types[feat.feat_type.name] += 1
        if feat.trigger:
            trigger_types[feat.trigger.name] += 1
        else:
            trigger_types["NONE"] += 1
            
        # Add to power level counter (use default if not specified)
        if hasattr(feat.prerequisites, "power_level"):
            power_level = feat.prerequisites.power_level.name
        else:
            power_level = "MEDIUM"  # Default
        power_levels[power_level] += 1
        
        # Categorize by complexity
        if complexity <= 5:
            complexity_ranges["Very Simple (0-5)"] += 1
        elif complexity <= 10:
            complexity_ranges["Simple (6-10)"] += 1
        elif complexity <= 15:
            complexity_ranges["Moderate (11-15)"] += 1
        elif complexity <= 20:
            complexity_ranges["Complex (16-20)"] += 1
        else:
            complexity_ranges["Very Complex (21+)"] += 1
            
        # Add to tag index
        if feat.tags:
            for tag in feat.tags:
                feat_by_tags[tag].append(feat_id)
                
        # Add to prerequisite indices
        if feat.prerequisites.stat_requirements:
            for stat in feat.prerequisites.stat_requirements:
                prerequisites_by_type["stat"][stat].append(feat_id)
                
        if feat.prerequisites.level_requirement > 1:
            level = feat.prerequisites.level_requirement
            prerequisites_by_type["level"][str(level)].append(feat_id)
            
        if feat.prerequisites.feat_requirements:
            for req_feat in feat.prerequisites.feat_requirements:
                prerequisites_by_type["feat"][req_feat].append(feat_id)
                
        if feat.prerequisites.class_requirements:
            for req_class in feat.prerequisites.class_requirements:
                prerequisites_by_type["class"][req_class].append(feat_id)
                
        if feat.prerequisites.race_requirements:
            for req_race in feat.prerequisites.race_requirements:
                prerequisites_by_type["race"][req_race].append(feat_id)
                
        if feat.prerequisites.skill_requirements:
            for skill in feat.prerequisites.skill_requirements:
                prerequisites_by_type["skill"][skill].append(feat_id)
    
    # Print distribution reports
    print("\n===== FEAT TYPE DISTRIBUTION =====")
    for feat_type, count in feat_types.items():
        print(f"{feat_type}: {count} ({count/len(ALL_FEATS)*100:.1f}%)")
    
    print("\n===== TRIGGER TYPE DISTRIBUTION =====")
    for trigger_type, count in trigger_types.items():
        print(f"{trigger_type}: {count} ({count/len(ALL_FEATS)*100:.1f}%)")
        
    print("\n===== POWER LEVEL DISTRIBUTION =====")
    for power_level, count in power_levels.items():
        print(f"{power_level}: {count} ({count/len(ALL_FEATS)*100:.1f}%)")
        
    print("\n===== COMPLEXITY DISTRIBUTION =====")
    for range_name, count in complexity_ranges.items():
        print(f"{range_name}: {count} ({count/len(ALL_FEATS)*100:.1f}%)")
        
    print("\n===== TOP TAGS =====")
    top_tags = sorted(feat_by_tags.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for tag, feats in top_tags:
        print(f"{tag}: {len(feats)} feats")
        
    print("\n===== PREREQUISITE ANALYSIS =====")
    for prereq_type, prereqs in prerequisites_by_type.items():
        if prereqs:
            print(f"\n{prereq_type.upper()} REQUIREMENTS:")
            for value, feats in sorted(prereqs.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
                print(f"  {value}: {len(feats)} feats")
    
    # Generate CSV report
    with open('feat_analysis.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['ID', 'Name', 'Type', 'Trigger', 'Tags', 'Complexity', 'Stat Reqs', 
                         'Level Req', 'Feat Reqs', 'Class Reqs', 'Race Reqs', 'Skill Reqs'])
        
        for feat_id, feat in ALL_FEATS.items():
            writer.writerow([
                feat_id,
                feat.name,
                feat.feat_type.name,
                feat.trigger.name if feat.trigger else "NONE",
                ", ".join(feat.tags) if feat.tags else "",
                feat_complexities[feat_id],
                json.dumps(feat.prerequisites.stat_requirements) if feat.prerequisites.stat_requirements else "",
                feat.prerequisites.level_requirement,
                ", ".join(feat.prerequisites.feat_requirements) if feat.prerequisites.feat_requirements else "",
                ", ".join(feat.prerequisites.class_requirements) if feat.prerequisites.class_requirements else "",
                ", ".join(feat.prerequisites.race_requirements) if feat.prerequisites.race_requirements else "",
                json.dumps(feat.prerequisites.skill_requirements) if feat.prerequisites.skill_requirements else ""
            ])
    
    print(f"\nDetailed analysis saved to feat_analysis.csv")
    
    # Return key metrics for further processing
    return {
        "feat_types": dict(feat_types),
        "trigger_types": dict(trigger_types),
        "power_levels": dict(power_levels),
        "complexity_ranges": complexity_ranges,
        "feat_complexities": feat_complexities
    }

def identify_unbalanced_feats(metrics):
    """Identify feats that may be unbalanced based on analysis metrics"""
    
    complexity_thresholds = {
        PowerLevel.LOW.name: 8,     # Low power feats should have minimal requirements
        PowerLevel.MEDIUM.name: 15,  # Medium power feats can have modest requirements
        PowerLevel.HIGH.name: 25,    # High power feats should have significant requirements
        PowerLevel.VERY_HIGH.name: 35  # Very high power feats need extensive requirements
    }
    
    unbalanced_feats = []
    
    for feat_id, feat in ALL_FEATS.items():
        complexity = metrics["feat_complexities"][feat_id]
        
        # Determine expected power level based on complexity
        expected_power = None
        if complexity <= complexity_thresholds[PowerLevel.LOW.name]:
            expected_power = PowerLevel.LOW.name
        elif complexity <= complexity_thresholds[PowerLevel.MEDIUM.name]:
            expected_power = PowerLevel.MEDIUM.name
        elif complexity <= complexity_thresholds[PowerLevel.HIGH.name]:
            expected_power = PowerLevel.HIGH.name
        else:
            expected_power = PowerLevel.VERY_HIGH.name
            
        # Get actual power level
        if hasattr(feat.prerequisites, "power_level"):
            actual_power = feat.prerequisites.power_level.name
        else:
            actual_power = "MEDIUM"  # Default
            
        # Check for significant mismatch
        if expected_power != actual_power:
            unbalanced_feats.append({
                "id": feat_id,
                "name": feat.name,
                "type": feat.feat_type.name,
                "actual_power": actual_power,
                "expected_power": expected_power,
                "complexity": complexity,
                "issue": "Power level does not match prerequisite complexity"
            })
            
        # Check for other potential issues
        if feat.feat_type == FeatType.PASSIVE and complexity > complexity_thresholds[PowerLevel.MEDIUM.name]:
            unbalanced_feats.append({
                "id": feat_id,
                "name": feat.name,
                "type": feat.feat_type.name,
                "actual_power": actual_power,
                "complexity": complexity,
                "issue": "Passive feat with high complexity prerequisites"
            })
            
        if feat.prerequisites.level_requirement > 15 and actual_power != PowerLevel.VERY_HIGH.name:
            unbalanced_feats.append({
                "id": feat_id,
                "name": feat.name,
                "type": feat.feat_type.name,
                "actual_power": actual_power,
                "level_req": feat.prerequisites.level_requirement,
                "issue": "High level requirement but not VERY_HIGH power"
            })
    
    print("\n===== POTENTIALLY UNBALANCED FEATS =====")
    for feat in unbalanced_feats:
        print(f"{feat['name']} ({feat['id']}): {feat['issue']}")
        
    # Save to CSV
    with open('unbalanced_feats.csv', 'w', newline='') as csvfile:
        fieldnames = ['id', 'name', 'type', 'actual_power', 'expected_power', 'complexity', 'level_req', 'issue']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for feat in unbalanced_feats:
            writer.writerow(feat)
    
    print(f"\nPotentially unbalanced feats saved to unbalanced_feats.csv")
    return unbalanced_feats

def suggest_progression_paths():
    """Analyze feat relationships and suggest potential progression paths"""
    
    # Identify feats with feat prerequisites
    feat_dependencies = {}
    reverse_dependencies = defaultdict(list)
    
    for feat_id, feat in ALL_FEATS.items():
        if feat.prerequisites.feat_requirements:
            feat_dependencies[feat_id] = feat.prerequisites.feat_requirements
            for req_feat in feat.prerequisites.feat_requirements:
                reverse_dependencies[req_feat].append(feat_id)
    
    # Identify potential starting points (feats with no feat prerequisites)
    starting_feats = []
    for feat_id, feat in ALL_FEATS.items():
        if not feat.prerequisites.feat_requirements:
            # Check if this feat is a prerequisite for others
            if feat_id in reverse_dependencies:
                starting_feats.append(feat_id)
    
    # Generate paths from each starting point
    suggested_paths = []
    
    for start_feat in starting_feats:
        # Follow chain of dependencies
        current_path = [start_feat]
        current_feat = start_feat
        
        while current_feat in reverse_dependencies:
            # For simplicity, just take the first dependent feat
            # In a real implementation, we'd want to explore all branches
            next_feat = reverse_dependencies[current_feat][0]
            current_path.append(next_feat)
            current_feat = next_feat
            
            # Avoid cycles
            if next_feat in current_path[:-1]:
                break
        
        # Only include paths with at least 2 feats
        if len(current_path) >= 2:
            path_name = f"{ALL_FEATS[start_feat].name} Path"
            suggested_paths.append({
                "name": path_name,
                "feats": current_path,
                "description": f"Progression starting with {ALL_FEATS[start_feat].name}"
            })
    
    # Look for tag-based paths (feats with same tags but no explicit dependencies)
    tag_groups = defaultdict(list)
    for feat_id, feat in ALL_FEATS.items():
        if feat.tags:
            primary_tag = feat.tags[0]  # Use first tag as primary
            tag_groups[primary_tag].append(feat_id)
    
    for tag, feats in tag_groups.items():
        if len(feats) >= 3:  # Only consider tags with at least 3 feats
            # Sort by level requirement or complexity to form progression
            sorted_feats = sorted(feats, key=lambda x: (
                ALL_FEATS[x].prerequisites.level_requirement, 
                ALL_FEATS[x].prerequisites.get_prerequisite_complexity()
            ))
            
            # Check if this forms a new path (not already covered by explicit dependencies)
            is_new_path = True
            for path in suggested_paths:
                if len(set(sorted_feats) & set(path["feats"])) > 1:
                    is_new_path = False
                    break
                    
            if is_new_path:
                suggested_paths.append({
                    "name": f"{tag.capitalize()} Specialization",
                    "feats": sorted_feats,
                    "description": f"Progression of {tag}-focused feats"
                })
    
    print("\n===== SUGGESTED PROGRESSION PATHS =====")
    for path in suggested_paths:
        print(f"\n{path['name']}: {path['description']}")
        for feat_id in path['feats']:
            prereqs = ALL_FEATS[feat_id].prerequisites
            print(f"  - {ALL_FEATS[feat_id].name} (Level {prereqs.level_requirement})")
    
    # Save paths to JSON
    with open('suggested_paths.json', 'w') as jsonfile:
        json.dump(suggested_paths, jsonfile, indent=2)
        
    print(f"\nSuggested progression paths saved to suggested_paths.json")
    return suggested_paths

if __name__ == "__main__":
    print("Analyzing feat system...")
    metrics = analyze_feat_distribution()
    print("\nIdentifying potentially unbalanced feats...")
    unbalanced = identify_unbalanced_feats(metrics)
    print("\nSuggesting progression paths...")
    paths = suggest_progression_paths()
    
    print("\nAnalysis complete!") 