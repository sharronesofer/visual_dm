#!/usr/bin/env python3
"""
BiomeAdjacencyMatrix.py - Part of the World Generation System

Implements adjacency rules for biomes, determining which biomes can be adjacent
to each other and how to handle transitions between incompatible biomes.
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Tuple, Union
import json
import math

from .BiomeTypes import BiomeType, BiomeClassification, BIOME_PARAMETERS, TRANSITION_BIOMES


class AdjacencyRuleType(Enum):
    """Types of biome adjacency rules"""
    COMPATIBLE = "compatible"  # Biomes can be directly adjacent
    INCOMPATIBLE = "incompatible"  # Biomes should never be directly adjacent
    TRANSITION_NEEDED = "transition_needed"  # Biomes require transition zones


class BiomeAdjacencyRule:
    """Rule defining the adjacency relationship between two biomes"""
    
    def __init__(self, biome1: BiomeType, biome2: BiomeType, 
                 rule_type: AdjacencyRuleType, 
                 transition_biomes: Optional[List[BiomeType]] = None,
                 min_transition_width: int = 1,
                 transition_weight: float = 1.0):
        """
        Initialize a biome adjacency rule
        
        Args:
            biome1: The first biome
            biome2: The second biome
            rule_type: The type of adjacency rule
            transition_biomes: List of biomes suitable for transitions (if rule_type is TRANSITION_NEEDED)
            min_transition_width: Minimum width of transition zone in cells
            transition_weight: Weight factor for this transition (higher = more likely)
        """
        self.biome1 = biome1
        self.biome2 = biome2
        self.rule_type = rule_type
        self.transition_biomes = transition_biomes or []
        self.min_transition_width = min_transition_width
        self.transition_weight = transition_weight
        
    def __str__(self) -> str:
        return f"{self.biome1.value} - {self.rule_type.value} - {self.biome2.value}"
        
    def to_dict(self) -> Dict:
        """Convert rule to a dictionary for serialization"""
        return {
            "biome1": self.biome1.value,
            "biome2": self.biome2.value,
            "rule_type": self.rule_type.value,
            "transition_biomes": [b.value for b in self.transition_biomes] if self.transition_biomes else [],
            "min_transition_width": self.min_transition_width,
            "transition_weight": self.transition_weight
        }
        
    @classmethod
    def from_dict(cls, data: Dict) -> 'BiomeAdjacencyRule':
        """Create rule from dictionary"""
        return cls(
            biome1=BiomeType(data["biome1"]),
            biome2=BiomeType(data["biome2"]),
            rule_type=AdjacencyRuleType(data["rule_type"]),
            transition_biomes=[BiomeType(b) for b in data.get("transition_biomes", [])],
            min_transition_width=data.get("min_transition_width", 1),
            transition_weight=data.get("transition_weight", 1.0)
        )


class BiomeAdjacencyMatrix:
    """
    Matrix of rules governing which biomes can be adjacent to each other
    and how transitions should be handled.
    """
    
    def __init__(self, rules: Optional[List[BiomeAdjacencyRule]] = None):
        """
        Initialize the adjacency matrix
        
        Args:
            rules: Optional list of predefined rules
        """
        self.rules: Dict[BiomeType, Dict[BiomeType, BiomeAdjacencyRule]] = {}
        
        # Initialize the matrix with default rules if none provided
        if rules is None:
            self._initialize_default_rules()
        else:
            for rule in rules:
                self.add_rule(rule)
    
    def _initialize_default_rules(self) -> None:
        """Initialize the matrix with default rules based on biome classifications"""
        for biome1 in BiomeType:
            for biome2 in BiomeType:
                if biome1 == biome2:
                    # Biomes are always compatible with themselves
                    continue
                    
                params1 = BIOME_PARAMETERS[biome1]
                params2 = BIOME_PARAMETERS[biome2]
                
                # Get classifications
                class1 = params1.classification
                class2 = params2.classification
                
                # Get temperature and moisture levels
                temp1 = params1.temperature_class.value
                temp2 = params2.temperature_class.value
                moisture1 = params1.moisture_class.value
                moisture2 = params2.moisture_class.value
                
                # Calculate temperature and moisture differences
                temp_diff = abs(temp1 - temp2)
                moisture_diff = abs(moisture1 - moisture2)
                
                # Rule determination logic
                rule = self._determine_rule(biome1, biome2, class1, class2, temp_diff, moisture_diff)
                
                if rule:
                    self.add_rule(rule)
    
    def _determine_rule(self, biome1: BiomeType, biome2: BiomeType, 
                        class1: BiomeClassification, class2: BiomeClassification,
                        temp_diff: int, moisture_diff: int) -> Optional[BiomeAdjacencyRule]:
        """
        Determine the appropriate adjacency rule between two biomes
        
        Args:
            biome1: First biome
            biome2: Second biome
            class1: Classification of first biome
            class2: Classification of second biome
            temp_diff: Temperature difference between biomes
            moisture_diff: Moisture difference between biomes
            
        Returns:
            The determined adjacency rule or None if already processed
        """
        # Skip if the rule is already defined (avoids redundancy)
        if self.has_rule(biome1, biome2):
            return None
            
        # Transition biomes are compatible with all adjacent biomes
        if biome1 in TRANSITION_BIOMES or biome2 in TRANSITION_BIOMES:
            return BiomeAdjacencyRule(biome1, biome2, AdjacencyRuleType.COMPATIBLE)
            
        # Same classification biomes are usually compatible
        if class1 == class2:
            return BiomeAdjacencyRule(biome1, biome2, AdjacencyRuleType.COMPATIBLE)
            
        # Special case: water biomes are compatible with coastal biomes
        if (class1 == BiomeClassification.WATER and biome2 == BiomeType.BEACH) or \
           (class2 == BiomeClassification.WATER and biome1 == BiomeType.BEACH):
            return BiomeAdjacencyRule(biome1, biome2, AdjacencyRuleType.COMPATIBLE)
            
        # Extreme differences need transitions
        if temp_diff >= 3 or moisture_diff >= 3:
            # Find appropriate transition biomes
            transition_biomes = self._find_transition_biomes(biome1, biome2)
            
            # Set minimum width based on difference severity
            min_width = max(1, min(3, max(temp_diff, moisture_diff) - 1))
            
            return BiomeAdjacencyRule(
                biome1, biome2,
                AdjacencyRuleType.TRANSITION_NEEDED,
                transition_biomes=transition_biomes,
                min_transition_width=min_width,
                transition_weight=1.0
            )
            
        # Moderate differences are compatible
        if temp_diff <= 1 and moisture_diff <= 1:
            return BiomeAdjacencyRule(biome1, biome2, AdjacencyRuleType.COMPATIBLE)
            
        # Other cases need transitions but are less severe
        transition_biomes = self._find_transition_biomes(biome1, biome2)
        return BiomeAdjacencyRule(
            biome1, biome2,
            AdjacencyRuleType.TRANSITION_NEEDED,
            transition_biomes=transition_biomes,
            min_transition_width=1,
            transition_weight=1.0
        )
    
    def _find_transition_biomes(self, biome1: BiomeType, biome2: BiomeType) -> List[BiomeType]:
        """
        Find appropriate transition biomes between two incompatible biomes
        
        Args:
            biome1: First biome
            biome2: Second biome
            
        Returns:
            List of suitable transition biomes, ordered by suitability
        """
        params1 = BIOME_PARAMETERS[biome1]
        params2 = BIOME_PARAMETERS[biome2]
        
        # First, consider explicit transition biomes
        candidates = list(TRANSITION_BIOMES)
        
        # Calculate midpoints of parameters
        mid_temp_min = (params1.temperature_range[0] + params2.temperature_range[0]) / 2
        mid_temp_max = (params1.temperature_range[1] + params2.temperature_range[1]) / 2
        mid_moisture_min = (params1.moisture_range[0] + params2.moisture_range[0]) / 2
        mid_moisture_max = (params1.moisture_range[1] + params2.moisture_range[1]) / 2
        
        # Score each potential transition biome
        scored_candidates = []
        for candidate in candidates:
            candidate_params = BIOME_PARAMETERS[candidate]
            
            # Skip if the candidate is the same as either biome
            if candidate == biome1 or candidate == biome2:
                continue
                
            # Calculate how well the candidate fits as a transition
            temp_overlap = self._calculate_range_overlap(
                candidate_params.temperature_range,
                (mid_temp_min, mid_temp_max)
            )
            
            moisture_overlap = self._calculate_range_overlap(
                candidate_params.moisture_range,
                (mid_moisture_min, mid_moisture_max)
            )
            
            # Combine scores and weight by transition_weight property
            score = (temp_overlap + moisture_overlap) * candidate_params.transition_weight
            
            # Only include if there's some overlap
            if score > 0:
                scored_candidates.append((candidate, score))
        
        # Sort by score (highest first) and extract just the biomes
        return [c[0] for c in sorted(scored_candidates, key=lambda x: x[1], reverse=True)]
    
    def _calculate_range_overlap(self, range1: Tuple[float, float], 
                                 range2: Tuple[float, float]) -> float:
        """
        Calculate the degree of overlap between two ranges
        
        Args:
            range1: First range (min, max)
            range2: Second range (min, max)
            
        Returns:
            Overlap score (0-1)
        """
        # Calculate overlap
        overlap_start = max(range1[0], range2[0])
        overlap_end = min(range1[1], range2[1])
        
        if overlap_start >= overlap_end:
            return 0.0  # No overlap
            
        # Calculate the overlap ratio relative to range1
        range1_size = range1[1] - range1[0]
        if range1_size <= 0:
            return 0.0
            
        overlap_size = overlap_end - overlap_start
        return overlap_size / range1_size
    
    def add_rule(self, rule: BiomeAdjacencyRule) -> None:
        """
        Add a new adjacency rule to the matrix
        
        Args:
            rule: The adjacency rule to add
        """
        # Initialize dictionaries if needed
        if rule.biome1 not in self.rules:
            self.rules[rule.biome1] = {}
        if rule.biome2 not in self.rules:
            self.rules[rule.biome2] = {}
        
        # Add rule in both directions for easy lookup
        self.rules[rule.biome1][rule.biome2] = rule
        
        # Create a mirrored rule for the other direction
        mirrored_rule = BiomeAdjacencyRule(
            biome1=rule.biome2,
            biome2=rule.biome1,
            rule_type=rule.rule_type,
            transition_biomes=rule.transition_biomes.copy() if rule.transition_biomes else None,
            min_transition_width=rule.min_transition_width,
            transition_weight=rule.transition_weight
        )
        self.rules[rule.biome2][rule.biome1] = mirrored_rule
    
    def has_rule(self, biome1: BiomeType, biome2: BiomeType) -> bool:
        """
        Check if a rule exists between two biomes
        
        Args:
            biome1: First biome
            biome2: Second biome
            
        Returns:
            True if a rule exists, False otherwise
        """
        return biome1 in self.rules and biome2 in self.rules[biome1]
    
    def get_rule(self, biome1: BiomeType, biome2: BiomeType) -> Optional[BiomeAdjacencyRule]:
        """
        Get the adjacency rule between two biomes
        
        Args:
            biome1: First biome
            biome2: Second biome
            
        Returns:
            The adjacency rule or None if no rule exists
        """
        if self.has_rule(biome1, biome2):
            return self.rules[biome1][biome2]
        return None
    
    def are_compatible(self, biome1: BiomeType, biome2: BiomeType) -> bool:
        """
        Check if two biomes are compatible (can be directly adjacent)
        
        Args:
            biome1: First biome
            biome2: Second biome
            
        Returns:
            True if biomes are compatible, False otherwise
        """
        # Same biome is always compatible
        if biome1 == biome2:
            return True
            
        rule = self.get_rule(biome1, biome2)
        if rule is None:
            # Default to requiring transition if no rule exists
            return False
            
        return rule.rule_type == AdjacencyRuleType.COMPATIBLE
    
    def get_transition_biomes(self, biome1: BiomeType, biome2: BiomeType) -> List[BiomeType]:
        """
        Get suitable transition biomes between two incompatible biomes
        
        Args:
            biome1: First biome
            biome2: Second biome
            
        Returns:
            List of suitable transition biomes, or empty list if none or not needed
        """
        rule = self.get_rule(biome1, biome2)
        
        if rule is None or rule.rule_type != AdjacencyRuleType.TRANSITION_NEEDED:
            return []
            
        return rule.transition_biomes
    
    def get_min_transition_width(self, biome1: BiomeType, biome2: BiomeType) -> int:
        """
        Get the minimum transition width needed between two biomes
        
        Args:
            biome1: First biome
            biome2: Second biome
            
        Returns:
            Minimum transition width in cells, or 0 if no transition needed
        """
        rule = self.get_rule(biome1, biome2)
        
        if rule is None or rule.rule_type != AdjacencyRuleType.TRANSITION_NEEDED:
            return 0
            
        return rule.min_transition_width
    
    def to_dict(self) -> Dict:
        """Convert the entire matrix to a dictionary for serialization"""
        rules_list = []
        processed_pairs = set()
        
        for biome1, rules_dict in self.rules.items():
            for biome2, rule in rules_dict.items():
                # Avoid duplicates by only processing each pair once
                pair = tuple(sorted([biome1.value, biome2.value]))
                if pair in processed_pairs:
                    continue
                    
                rules_list.append(rule.to_dict())
                processed_pairs.add(pair)
        
        return {"rules": rules_list}
    
    def to_json(self, indent: int = 2) -> str:
        """Convert the matrix to a JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BiomeAdjacencyMatrix':
        """Create a matrix from a dictionary"""
        rules = [BiomeAdjacencyRule.from_dict(r) for r in data.get("rules", [])]
        return cls(rules=rules)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BiomeAdjacencyMatrix':
        """Create a matrix from a JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def save_to_file(self, filepath: str) -> None:
        """Save the matrix to a JSON file"""
        with open(filepath, 'w') as f:
            f.write(self.to_json())
    
    @classmethod
    def load_from_file(cls, filepath: str) -> 'BiomeAdjacencyMatrix':
        """Load a matrix from a JSON file"""
        with open(filepath, 'r') as f:
            return cls.from_json(f.read())
    
    def override_rule(self, biome1: BiomeType, biome2: BiomeType, 
                     rule_type: AdjacencyRuleType,
                     transition_biomes: Optional[List[BiomeType]] = None,
                     min_transition_width: int = 1) -> None:
        """
        Override an existing rule or create a new one
        
        Args:
            biome1: First biome
            biome2: Second biome
            rule_type: The new rule type
            transition_biomes: Optional list of transition biomes
            min_transition_width: Minimum transition width
        """
        new_rule = BiomeAdjacencyRule(
            biome1=biome1,
            biome2=biome2,
            rule_type=rule_type,
            transition_biomes=transition_biomes,
            min_transition_width=min_transition_width
        )
        self.add_rule(new_rule) 