"""
Transformer for rumor content mutation and truth tracking.

This module provides functionality for transforming rumors as they spread,
including AI-powered content mutation and tracking how truth values change.
"""
import logging
import random
from typing import Dict, List, Optional, Any
import re

from backend.core.ai.gpt_client import GPTClient

logger = logging.getLogger(__name__)

class RumorTransformer:
    """
    Transforms rumors using AI and heuristics as they spread through entities.
    
    This class is responsible for:
    1. Mutating rumor content when spread from one entity to another
    2. Tracking and adjusting truth values as rumors mutate
    3. Managing distortion based on entity traits and relationships
    """
    
    def __init__(self, gpt_client: Optional[GPTClient] = None):
        """
        Initialize the rumor transformer.
        
        Args:
            gpt_client: Optional GPT client for AI-powered transformations
        """
        self.gpt_client = gpt_client or GPTClient()
        
    async def transform_rumor(
        self, 
        event: str,
        rumor: str,
        traits: str = "",
        distortion_level: float = 0.2,
        semantic_direction: Optional[str] = None
    ) -> str:
        """
        Transform a rumor using AI based on entity traits and distortion level.
        
        Args:
            event: The original event the rumor is based on
            rumor: The current rumor content
            traits: Traits of the entity spreading the rumor
            distortion_level: How much to distort the rumor (0.0 to 1.0)
            semantic_direction: Optional direction for the transformation
                (e.g., "exaggerate", "downplay", "contradict")
                
        Returns:
            The transformed rumor content
        """
        if distortion_level < 0.05:
            return rumor  # Almost no distortion, return as is
        
        # Construct prompt based on parameters
        prompt = self._build_transformation_prompt(
            event=event,
            rumor=rumor,
            traits=traits,
            distortion_level=distortion_level,
            semantic_direction=semantic_direction
        )
        
        try:
            response = await self.gpt_client.generate_text(prompt)
            
            # Extract just the transformed rumor, not any explanation
            transformed = self._extract_transformed_rumor(response)
            
            logger.info(f"Transformed rumor with distortion {distortion_level}")
            return transformed
        except Exception as e:
            logger.error(f"Error transforming rumor: {e}")
            # Fallback to rule-based transformation
            return self.fallback_transform(rumor, distortion_level)
    
    def _build_transformation_prompt(
        self,
        event: str,
        rumor: str,
        traits: str,
        distortion_level: float,
        semantic_direction: Optional[str] = None
    ) -> str:
        """
        Build the prompt for the GPT transformation.
        
        Args:
            event: The original event
            rumor: The current rumor
            traits: Entity traits
            distortion_level: Distortion level
            semantic_direction: Direction for transformation
            
        Returns:
            Formatted prompt for GPT
        """
        # Map distortion level to descriptive terms
        distortion_desc = "minimal"
        if distortion_level > 0.7:
            distortion_desc = "extreme"
        elif distortion_level > 0.4:
            distortion_desc = "significant"
        elif distortion_level > 0.2:
            distortion_desc = "moderate"
        
        prompt_parts = [
            "Transform the following rumor as it's being retold.",
            f"Original event: {event}",
            f"Current rumor: {rumor}",
        ]
        
        if traits:
            prompt_parts.append(f"The person retelling has these traits: {traits}")
        
        prompt_parts.append(f"Apply {distortion_desc} distortion level ({distortion_level:.1f} out of 1.0)")
        
        if semantic_direction:
            prompt_parts.append(f"Direction: {semantic_direction}")
        
        prompt_parts.append("Return ONLY the transformed rumor text with no explanations or additional information.")
        
        return "\n\n".join(prompt_parts)
    
    def _extract_transformed_rumor(self, response: str) -> str:
        """
        Extract just the rumor from a potentially longer GPT response.
        
        Args:
            response: The GPT response
            
        Returns:
            Cleaned rumor text
        """
        # Remove any explanation or metadata the model might have included
        lines = response.strip().split("\n")
        
        # If multiple lines, look for the most rumor-like content
        if len(lines) > 1:
            # Skip lines that are clearly just labels or instructions
            content_lines = []
            for line in lines:
                lowercase = line.lower()
                if not (
                    lowercase.startswith("transformed rumor:")
                    or lowercase.startswith("rumor:")
                    or lowercase.startswith("response:")
                    or lowercase.startswith("here's the transformed")
                    or lowercase.startswith("i've transformed")
                    or lowercase.startswith("explanation:")
                ):
                    content_lines.append(line)
            
            if content_lines:
                return " ".join(content_lines)
        
        # If we can't determine which part is the rumor or only one line, return the whole response
        return response.strip()
    
    def fallback_transform(self, rumor: str, distortion_level: float) -> str:
        """
        Rule-based fallback transformation when AI transformation fails.
        
        Args:
            rumor: Original rumor content
            distortion_level: Level of distortion to apply
            
        Returns:
            Transformed rumor
        """
        if distortion_level < 0.1:
            return rumor
        
        # Split into words
        words = rumor.split()
        
        # Determine how many words to modify based on distortion level
        num_to_modify = int(len(words) * distortion_level * 0.5)
        num_to_modify = max(1, min(num_to_modify, len(words) // 3))  # At least 1, at most 1/3 of words
        
        # Choose random positions to modify
        positions = random.sample(range(len(words)), num_to_modify)
        
        for pos in positions:
            # Simple transformations
            if len(words[pos]) > 3 and random.random() < 0.3:
                # Exaggerate quantities
                if words[pos].isdigit():
                    words[pos] = str(int(words[pos]) * random.randint(2, 5))
                # Replace adjectives with more extreme versions
                elif words[pos].lower() in ["big", "large", "huge"]:
                    words[pos] = "enormous"
                elif words[pos].lower() in ["small", "tiny", "little"]:
                    words[pos] = "minuscule"
                # Add qualifiers
                elif random.random() < 0.5:
                    if pos > 0 and not words[pos-1].lower() in ["very", "extremely", "incredibly"]:
                        words[pos] = "very " + words[pos]
        
        return " ".join(words)

    def calculate_truth_value(
        self, 
        original_event: str, 
        transformed_rumor: str,
        base_truth: float = 0.5
    ) -> float:
        """
        Calculate how true a transformed rumor is compared to the original event.
        
        Args:
            original_event: The factual event that happened
            transformed_rumor: The transformed rumor to evaluate
            base_truth: Starting truth value (0.0 to 1.0)
            
        Returns:
            New truth value (0.0 to 1.0)
        """
        # Simple heuristic: decrease truth based on word count difference
        orig_word_count = len(original_event.split())
        transformed_word_count = len(transformed_rumor.split())
        
        word_count_diff = abs(orig_word_count - transformed_word_count) / max(orig_word_count, 1)
        word_penalty = word_count_diff * 0.2  # Up to 0.2 penalty for length difference
        
        # Check for factual inconsistencies based on key words
        original_lower = original_event.lower()
        transformed_lower = transformed_rumor.lower()
        
        # Extract key nouns and verbs (very simplified)
        orig_key_words = set(re.findall(r'\b\w{4,}\b', original_lower))
        transformed_key_words = set(re.findall(r'\b\w{4,}\b', transformed_lower))
        
        # Calculate word overlap
        common_words = orig_key_words.intersection(transformed_key_words)
        word_overlap = len(common_words) / max(len(orig_key_words), 1)
        
        # Calculate truth decay
        truth_decay = 0.3 * (1 - word_overlap) + word_penalty
        
        # Ensure truth value stays in bounds
        new_truth = max(0.0, min(1.0, base_truth - truth_decay))
        
        logger.info(f"Calculated truth value: {new_truth:.2f} (from {base_truth:.2f})")
        return new_truth
        
    async def evaluate_rumor_truthfulness(
        self,
        original_event: str,
        rumor: str,
        base_truth: float = 0.5
    ) -> float:
        """
        Use AI to evaluate how truthful a rumor is compared to the original event.
        
        Args:
            original_event: The original event that happened
            rumor: The rumor to evaluate
            base_truth: Starting truth value
            
        Returns:
            AI-evaluated truth value (0.0 to 1.0)
        """
        if not self.gpt_client:
            return self.calculate_truth_value(original_event, rumor, base_truth)
            
        try:
            prompt = (
                f"Original factual event: \"{original_event}\"\n\n"
                f"Rumor: \"{rumor}\"\n\n"
                "Rate how truthful the rumor is compared to the original event on a scale of 0.0 to 1.0, "
                "where 1.0 means completely true and accurate, and 0.0 means completely false.\n\n"
                "Respond with ONLY the numeric value between 0.0 and 1.0."
            )
            
            response = await self.gpt_client.generate_text(prompt)
            
            # Extract the numeric value from the response
            numeric_match = re.search(r'(\d+\.\d+|\d+)', response)
            if numeric_match:
                truth_value = float(numeric_match.group(1))
                # Ensure it's in the valid range
                truth_value = max(0.0, min(1.0, truth_value))
                return truth_value
            else:
                logger.warning(f"Could not extract truth value from AI response: {response}")
                return self.calculate_truth_value(original_event, rumor, base_truth)
        except Exception as e:
            logger.error(f"Error evaluating rumor truthfulness: {e}")
            return self.calculate_truth_value(original_event, rumor, base_truth) 