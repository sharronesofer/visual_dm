"""
Feat Rebalancing Script

This script helps rebalance feat prerequisites to improve game balance
and create more logical progression paths.
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

def load_analysis_data():
    """Load analysis data from previous runs of analyze_feats.py"""
    if not os.path.exists('feat_analysis.csv'):
        print("Error: feat_analysis.csv not found. Run analyze_feats.py first.")
        return None
    
    if not os.path.exists('unbalanced_feats.csv'):
        print("Error: unbalanced_feats.csv not found. Run analyze_feats.py first.")
        return None
    
    # Load feat analysis data
    feat_data = {}
    with open('feat_analysis.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            feat_data[row['ID']] = row
    
    # Load unbalanced feats data
    unbalanced_feats = []
    with open('unbalanced_feats.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            unbalanced_feats.append(row)
    
    return {
        'feat_data': feat_data,
        'unbalanced_feats': unbalanced_feats
    }

def rebalance_stat_requirements():
    """Rebalance stat requirements based on power level and feat type"""
    
    # Define baseline stat requirements by power level
    baseline_stat_reqs = {
        PowerLevel.LOW: 10,       # Low power feats have minimal stat requirements
        PowerLevel.MEDIUM: 13,    # Medium power feats require moderate stats
        PowerLevel.HIGH: 16,      # High power feats need significant stat investment
        PowerLevel.VERY_HIGH: 18  # Very high power feats require exceptional stats
    }
    
    # Map feat types to primary stats
    feat_type_to_stats = {
        FeatType.PASSIVE: {
            "general": ["constitution"],
            "combat": ["strength", "dexterity"],
            "magic": ["intelligence", "wisdom", "charisma"],
            "skills": ["dexterity", "intelligence"]
        },
        FeatType.ACTIVATED: {
            "general": ["dexterity", "intelligence"],
            "combat": ["strength", "dexterity"],
            "magic": ["intelligence", "wisdom", "charisma"],
            "skills": ["dexterity", "intelligence"]
        },
        FeatType.REACTIVE: {
            "general": ["wisdom", "dexterity"],
            "combat": ["dexterity", "constitution"],
            "magic": ["intelligence", "wisdom"],
            "skills": ["dexterity", "wisdom"]
        },
        FeatType.STANCE: {
            "general": ["constitution", "wisdom"],
            "combat": ["strength", "constitution"],
            "magic": ["intelligence", "charisma"],
            "skills": ["dexterity", "wisdom"]
        }
    }
    
    # Adjusted feat templates with rebalanced stats
    rebalanced_feats = {}
    
    # Process each feat
    for feat_id, feat in ALL_FEATS.items():
        # Create a deep copy to avoid modifying the original
        new_feat = copy.deepcopy(feat)
        
        # Determine feat category based on tags or default to "general"
        category = "general"
        if feat.tags:
            if any(tag in ["melee", "ranged", "armor", "shield", "weapon"] for tag in feat.tags):
                category = "combat"
            elif any(tag in ["spell", "magic", "arcane", "divine"] for tag in feat.tags):
                category = "magic"
            elif any(tag in ["skill", "stealth", "social", "knowledge"] for tag in feat.tags):
                category = "skills"
        
        # Get power level (default to MEDIUM if not specified)
        if hasattr(feat.prerequisites, "power_level"):
            power_level = feat.prerequisites.power_level
        else:
            power_level = PowerLevel.MEDIUM
        
        # Get baseline stat requirement for this power level
        base_req = baseline_stat_reqs[power_level]
        
        # Get appropriate stats for this feat type and category
        appropriate_stats = feat_type_to_stats.get(feat.feat_type, {}).get(category, ["constitution"])
        
        # Initialize stat requirements if none exist
        if not new_feat.prerequisites.stat_requirements:
            new_feat.prerequisites.stat_requirements = {}
        
        # Clear inappropriate stat requirements
        current_stats = list(new_feat.prerequisites.stat_requirements.keys())
        for stat in current_stats:
            if stat not in appropriate_stats:
                # Only remove if not significantly higher than baseline
                if new_feat.prerequisites.stat_requirements[stat] <= base_req + 2:
                    del new_feat.prerequisites.stat_requirements[stat]
        
        # Ensure at least one appropriate stat requirement exists
        if not new_feat.prerequisites.stat_requirements:
            # Choose the first appropriate stat
            new_feat.prerequisites.stat_requirements[appropriate_stats[0]] = base_req
        
        # Adjust existing stat requirements to match power level
        for stat, value in new_feat.prerequisites.stat_requirements.items():
            # Don't decrease existing high requirements
            if value < base_req:
                new_feat.prerequisites.stat_requirements[stat] = base_req
        
        # Store the rebalanced feat
        rebalanced_feats[feat_id] = new_feat
    
    return rebalanced_feats

def adjust_feat_prerequisites_for_progression():
    """Adjust feat prerequisites to reflect progression paths"""
    
    # Start with rebalanced stat requirements
    rebalanced_feats = rebalance_stat_requirements()
    
    # Process each progression path
    for path_name, progression in PROGRESSION_PATHS.items():
        feat_ids = progression.feat_ids
        
        # Skip invalid progressions with fewer than 2 feats
        if len(feat_ids) < 2:
            continue
        
        # Ensure each feat requires the previous feat in the path
        for i in range(1, len(feat_ids)):
            current_feat_id = feat_ids[i]
            prev_feat_id = feat_ids[i-1]
            
            # Skip if feat doesn't exist in our rebalanced set
            if current_feat_id not in rebalanced_feats or prev_feat_id not in rebalanced_feats:
                continue
            
            current_feat = rebalanced_feats[current_feat_id]
            
            # Initialize feat_requirements if it doesn't exist
            if not current_feat.prerequisites.feat_requirements:
                current_feat.prerequisites.feat_requirements = []
            
            # Add previous feat as a prerequisite if not already there
            if prev_feat_id not in current_feat.prerequisites.feat_requirements:
                current_feat.prerequisites.feat_requirements.append(prev_feat_id)
            
            # Ensure level requirements are progressive
            prev_feat = rebalanced_feats[prev_feat_id]
            if current_feat.prerequisites.level_requirement <= prev_feat.prerequisites.level_requirement:
                # Add at least 1 level, more for higher power feats
                if hasattr(current_feat.prerequisites, "power_level"):
                    power_level = current_feat.prerequisites.power_level
                else:
                    power_level = PowerLevel.MEDIUM
                
                level_increment = power_level.value  # 1 for LOW, 2 for MEDIUM, etc.
                current_feat.prerequisites.level_requirement = prev_feat.prerequisites.level_requirement + level_increment
    
    return rebalanced_feats

def generate_rebalanced_feats(output_file="rebalanced_feats.py"):
    """Generate a new file with rebalanced feat definitions"""
    
    rebalanced_feats = adjust_feat_prerequisites_for_progression()
    
    # Generate Python code for the rebalanced feats
    code = """\"\"\"
Rebalanced Feat Templates

This file contains rebalanced feat templates with improved prerequisites
for better game balance and progression paths.
\"\"\"

from typing import Dict, List
from app.core.models.feats import Feat, FeatType, TriggerType, ResourceType, FeatPrerequisite, FeatResource, FeatEffect, PowerLevel
from app.core.models.effects import StatModifierEffect, DamageModifierEffect

# Rebalanced feat templates
REBALANCED_FEATS: Dict[str, Feat] = {
"""
    
    # Add each feat definition
    for feat_id, feat in rebalanced_feats.items():
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
        
        # Add effects placeholder (this would need to be expanded in a real implementation)
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
    
    print(f"Rebalanced feats written to {output_file}")
    return rebalanced_feats

def export_csv_comparison(rebalanced_feats, output_file="feat_comparison.csv"):
    """Create a CSV comparing original and rebalanced feats"""
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'ID', 'Name', 'Original Stat Requirements', 'Rebalanced Stat Requirements',
            'Original Level', 'Rebalanced Level', 'Original Feat Prerequisites',
            'Rebalanced Feat Prerequisites', 'Changes Made'
        ])
        
        for feat_id, rebalanced_feat in rebalanced_feats.items():
            original_feat = ALL_FEATS[feat_id]
            
            # Identify changes
            changes = []
            
            # Check stat requirements
            orig_stats = original_feat.prerequisites.stat_requirements or {}
            new_stats = rebalanced_feat.prerequisites.stat_requirements or {}
            if orig_stats != new_stats:
                changes.append("Stat requirements modified")
            
            # Check level
            if original_feat.prerequisites.level_requirement != rebalanced_feat.prerequisites.level_requirement:
                changes.append(f"Level changed from {original_feat.prerequisites.level_requirement} to {rebalanced_feat.prerequisites.level_requirement}")
            
            # Check feat prerequisites
            orig_feats = original_feat.prerequisites.feat_requirements or []
            new_feats = rebalanced_feat.prerequisites.feat_requirements or []
            if set(orig_feats) != set(new_feats):
                added = set(new_feats) - set(orig_feats)
                if added:
                    changes.append(f"Added feat prerequisites: {', '.join(added)}")
            
            # Write row
            writer.writerow([
                feat_id,
                original_feat.name,
                json.dumps(orig_stats),
                json.dumps(new_stats),
                original_feat.prerequisites.level_requirement,
                rebalanced_feat.prerequisites.level_requirement,
                ", ".join(orig_feats),
                ", ".join(new_feats),
                "; ".join(changes)
            ])
    
    print(f"Feat comparison exported to {output_file}")

if __name__ == "__main__":
    print("Rebalancing feat prerequisites...")
    rebalanced_feats = generate_rebalanced_feats()
    
    print("\nGenerating comparison report...")
    export_csv_comparison(rebalanced_feats)
    
    print("\nRebalancing complete!") 