"""
Response Quality Control for Visual DM LLM System

Provides comprehensive content validation, consistency checking, and style guide 
enforcement for all LLM-generated content to ensure quality and consistency.
"""

import logging
import re
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from backend.infrastructure.llm.utils.llm_utils import LLMUtils
from backend.infrastructure.shared.exceptions import LlmValidationError

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation strictness levels"""
    STRICT = "strict"        # All validation rules must pass
    MODERATE = "moderate"    # Most validation rules must pass
    LENIENT = "lenient"     # Basic validation only

@dataclass
class ValidationResult:
    """Result of content validation"""
    passed: bool
    confidence_score: float
    issues: List[str]
    suggestions: List[str]
    metadata: Dict[str, Any]

@dataclass
class StyleRule:
    """Represents a style guide rule"""
    name: str
    pattern: str
    replacement: str
    description: str
    category: str
    severity: str  # 'error', 'warning', 'suggestion'

class ContentValidator:
    """
    Validates generated content for quality and consistency.
    
    Features:
    - Content length validation
    - Style consistency checking
    - Character voice consistency
    - Content appropriateness filtering
    - Format validation
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.MODERATE):
        self.validation_level = validation_level
        self.token_estimator = LLMUtils()
        
        # Content length limits by type
        self.length_limits = {
            "dialogue": {"min": 10, "max": 500, "target": 150},
            "narrative": {"min": 50, "max": 800, "target": 300},
            "quest": {"min": 100, "max": 1500, "target": 600},
            "description": {"min": 30, "max": 400, "target": 200},
            "system": {"min": 5, "max": 200, "target": 50}
        }
        
        # Inappropriate content patterns
        self.inappropriate_patterns = [
            r'\b(fuck|shit|damn|hell)\b',  # Basic profanity
            r'\b(kill yourself|die|suicide)\b',  # Harmful content
            r'\b(racist|sexist|homophobic)\b',  # Discriminatory content
        ]
        
        # Quality indicators
        self.quality_patterns = {
            "positive": [
                r'"[^"]*"',  # Quoted dialogue
                r'\b(vivid|atmospheric|immersive|detailed)\b',  # Quality descriptors
                r'[.!?]',  # Proper sentence endings
            ],
            "negative": [
                r'\b(um|uh|er|like)\b',  # Filler words
                r'\.{3,}',  # Multiple ellipses
                r'[A-Z]{3,}',  # Excessive capitalization
                r'\b(very very|really really)\b',  # Repetitive intensifiers
            ]
        }
    
    async def validate_response(self, 
                              response: str, 
                              context: Dict[str, Any]) -> ValidationResult:
        """
        Comprehensive response validation.
        
        Args:
            response: Generated content to validate
            context: Context information (type, character, etc.)
            
        Returns:
            ValidationResult with pass/fail and detailed feedback
        """
        issues = []
        suggestions = []
        metadata = {}
        
        content_type = context.get("type", "general")
        character_context = context.get("character", {})
        
        # Basic content validation
        length_result = await self._validate_length(response, content_type)
        if not length_result["passed"]:
            issues.extend(length_result["issues"])
            suggestions.extend(length_result["suggestions"])
        
        # Style consistency validation
        style_result = await self._validate_style_consistency(response, context)
        if not style_result["passed"]:
            issues.extend(style_result["issues"])
            suggestions.extend(style_result["suggestions"])
        
        # Content appropriateness
        appropriateness_result = await self._validate_appropriateness(response)
        if not appropriateness_result["passed"]:
            issues.extend(appropriateness_result["issues"])
            suggestions.extend(appropriateness_result["suggestions"])
        
        # Character voice consistency (for dialogue)
        if content_type == "dialogue" and character_context:
            voice_result = await self._validate_character_voice(response, character_context)
            if not voice_result["passed"]:
                issues.extend(voice_result["issues"])
                suggestions.extend(voice_result["suggestions"])
        
        # Format validation
        format_result = await self._validate_format(response, content_type)
        if not format_result["passed"]:
            issues.extend(format_result["issues"])
            suggestions.extend(format_result["suggestions"])
        
        # Quality assessment
        quality_score = await self._assess_quality(response, content_type)
        metadata["quality_score"] = quality_score
        
        # Calculate overall confidence score
        confidence_score = self._calculate_confidence(
            len(issues), quality_score, len(suggestions)
        )
        
        # Determine pass/fail based on validation level
        passed = self._determine_pass_fail(issues, confidence_score)
        
        return ValidationResult(
            passed=passed,
            confidence_score=confidence_score,
            issues=issues,
            suggestions=suggestions,
            metadata=metadata
        )
    
    async def _validate_length(self, response: str, content_type: str) -> Dict[str, Any]:
        """Validate response length against expected limits"""
        limits = self.length_limits.get(content_type, self.length_limits["system"])
        length = len(response)
        
        issues = []
        suggestions = []
        
        if length < limits["min"]:
            issues.append(f"Response too short: {length} chars (min: {limits['min']})")
            suggestions.append(f"Expand content to at least {limits['min']} characters")
        elif length > limits["max"]:
            issues.append(f"Response too long: {length} chars (max: {limits['max']})")
            suggestions.append(f"Reduce content to under {limits['max']} characters")
        
        # Check if response is within target range
        target_min = limits["target"] * 0.7
        target_max = limits["target"] * 1.3
        
        if not (target_min <= length <= target_max):
            suggestions.append(f"Consider targeting ~{limits['target']} characters for optimal length")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    async def _validate_style_consistency(self, response: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate style consistency with established patterns"""
        issues = []
        suggestions = []
        
        content_type = context.get("type", "general")
        
        # Dialogue-specific style checks
        if content_type == "dialogue":
            if not (response.startswith('"') or response.startswith("'")):
                issues.append("Dialogue should be properly quoted")
                suggestions.append("Wrap dialogue in quotation marks")
            
            # Check for excessive length in single dialogue response
            if len(response) > 300:
                suggestions.append("Consider breaking long dialogue into shorter responses")
        
        # Narrative-specific style checks
        elif content_type == "narrative":
            # Check for present tense usage (preferred for immersion)
            past_tense_patterns = [r'\b\w+ed\b', r'\bwas\b', r'\bwere\b', r'\bhad\b']
            past_tense_count = sum(len(re.findall(pattern, response, re.IGNORECASE)) 
                                 for pattern in past_tense_patterns)
            
            if past_tense_count > len(response.split()) * 0.3:
                suggestions.append("Consider using present tense for more immersive narrative")
        
        # General style checks
        
        # Check for sentence variety
        sentences = re.split(r'[.!?]+', response)
        if len(sentences) > 3:
            avg_length = sum(len(s.split()) for s in sentences if s.strip()) / len([s for s in sentences if s.strip()])
            if avg_length < 3:
                suggestions.append("Vary sentence length for better flow")
        
        # Check for repetitive words
        words = response.lower().split()
        word_counts = {}
        for word in words:
            if len(word) > 3:  # Only check longer words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        repeated_words = [word for word, count in word_counts.items() if count > 2]
        if repeated_words:
            suggestions.append(f"Consider varying vocabulary (repeated: {', '.join(repeated_words[:3])})")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    async def _validate_appropriateness(self, response: str) -> Dict[str, Any]:
        """Validate content appropriateness"""
        issues = []
        suggestions = []
        
        # Check for inappropriate content
        for pattern in self.inappropriate_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                issues.append("Content contains inappropriate language or themes")
                suggestions.append("Revise content to be appropriate for all audiences")
                break
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    async def _validate_character_voice(self, response: str, character_context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate consistency with character voice and personality"""
        issues = []
        suggestions = []
        
        personality = character_context.get("personality", {})
        speech_style = character_context.get("speech_style", "")
        
        # Check speech style consistency
        if speech_style == "formal":
            informal_patterns = [r'\b(yeah|nah|ain\'t|gonna)\b']
            for pattern in informal_patterns:
                if re.search(pattern, response, re.IGNORECASE):
                    issues.append("Informal language inconsistent with formal speech style")
                    suggestions.append("Use more formal language patterns")
                    break
        
        elif speech_style == "casual":
            formal_patterns = [r'\b(indeed|furthermore|nevertheless)\b']
            for pattern in formal_patterns:
                if re.search(pattern, response, re.IGNORECASE):
                    suggestions.append("Consider using more casual language")
                    break
        
        # Check personality trait consistency
        if isinstance(personality, dict):
            # Check for traits that affect speech patterns
            if personality.get("aggressive", 0) > 7:
                if not re.search(r'[!]', response):
                    suggestions.append("Consider more assertive punctuation for aggressive character")
            
            if personality.get("timid", 0) > 7:
                if re.search(r'[!]{2,}', response):
                    suggestions.append("Excessive exclamation inconsistent with timid personality")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    async def _validate_format(self, response: str, content_type: str) -> Dict[str, Any]:
        """Validate format requirements for content type"""
        issues = []
        suggestions = []
        
        # Quest format validation
        if content_type == "quest":
            required_sections = ["title:", "description:", "objectives:"]
            missing_sections = []
            
            for section in required_sections:
                if section.lower() not in response.lower():
                    missing_sections.append(section)
            
            if missing_sections:
                issues.append(f"Missing required quest sections: {', '.join(missing_sections)}")
                suggestions.append("Include all required quest sections (Title, Description, Objectives)")
        
        # Dialogue format validation
        elif content_type == "dialogue":
            # Check for proper dialogue formatting
            if response.count('"') % 2 != 0:
                issues.append("Unmatched quotation marks in dialogue")
                suggestions.append("Ensure all dialogue is properly quoted")
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    async def _assess_quality(self, response: str, content_type: str) -> float:
        """Assess overall content quality (0.0 to 1.0)"""
        score = 0.5  # Base score
        
        # Positive quality indicators
        for pattern in self.quality_patterns["positive"]:
            matches = len(re.findall(pattern, response, re.IGNORECASE))
            score += min(matches * 0.1, 0.2)  # Cap contribution
        
        # Negative quality indicators
        for pattern in self.quality_patterns["negative"]:
            matches = len(re.findall(pattern, response, re.IGNORECASE))
            score -= min(matches * 0.1, 0.3)  # Cap penalty
        
        # Length-based quality adjustment
        limits = self.length_limits.get(content_type, self.length_limits["system"])
        length = len(response)
        
        # Optimal length range gets bonus
        if limits["target"] * 0.8 <= length <= limits["target"] * 1.2:
            score += 0.1
        
        # Sentence structure assessment
        sentences = [s.strip() for s in re.split(r'[.!?]+', response) if s.strip()]
        if len(sentences) > 1:
            # Variety in sentence length is good
            lengths = [len(s.split()) for s in sentences]
            if len(set(lengths)) > len(lengths) * 0.5:  # Good variety
                score += 0.1
        
        return max(0.0, min(1.0, score))
    
    def _calculate_confidence(self, issue_count: int, quality_score: float, suggestion_count: int) -> float:
        """Calculate confidence score based on validation results"""
        base_confidence = 1.0
        
        # Reduce confidence for each issue
        base_confidence -= issue_count * 0.2
        
        # Reduce confidence for low quality
        base_confidence *= quality_score
        
        # Slight reduction for suggestions (not as severe as issues)
        base_confidence -= suggestion_count * 0.05
        
        return max(0.0, min(1.0, base_confidence))
    
    def _determine_pass_fail(self, issues: List[str], confidence_score: float) -> bool:
        """Determine if validation passes based on level and results"""
        if self.validation_level == ValidationLevel.STRICT:
            return len(issues) == 0 and confidence_score >= 0.8
        elif self.validation_level == ValidationLevel.MODERATE:
            return len(issues) == 0 and confidence_score >= 0.6
        else:  # LENIENT
            return len(issues) == 0 and confidence_score >= 0.4

class StyleGuideEnforcer:
    """
    Enforces Visual DM style guide for generated content.
    
    Features:
    - Terminology consistency
    - Dialogue formatting
    - Narrative style enforcement
    - Character speech pattern application
    """
    
    def __init__(self):
        self.terminology_rules = self._load_terminology_rules()
        self.dialogue_rules = self._load_dialogue_rules()
        self.narrative_rules = self._load_narrative_rules()
    
    def _load_terminology_rules(self) -> List[StyleRule]:
        """Load terminology consistency rules"""
        return [
            StyleRule(
                name="dreamforge_capitalization",
                pattern=r'\bvisual dm\b',
                replacement="Visual DM",
                description="Capitalize Visual DM properly",
                category="terminology",
                severity="error"
            ),
            StyleRule(
                name="npc_capitalization",
                pattern=r'\bnpc\b',
                replacement="NPC",
                description="Capitalize NPC abbreviation",
                category="terminology",
                severity="error"
            ),
            StyleRule(
                name="dm_capitalization",
                pattern=r'\bdm\b',
                replacement="DM",
                description="Capitalize DM abbreviation",
                category="terminology",
                severity="error"
            ),
            StyleRule(
                name="consistent_currency",
                pattern=r'\b(gold pieces|gp|gold coins)\b',
                replacement="gold",
                description="Use consistent currency terms",
                category="terminology",
                severity="warning"
            )
        ]
    
    def _load_dialogue_rules(self) -> List[StyleRule]:
        """Load dialogue formatting rules"""
        return [
            StyleRule(
                name="dialogue_quotes",
                pattern=r'^([^"\']*[a-zA-Z][^"\']*)$',
                replacement=r'"\1"',
                description="Wrap dialogue in quotes",
                category="dialogue",
                severity="error"
            ),
            StyleRule(
                name="dialogue_punctuation_inside",
                pattern=r'"([^"]*[a-zA-Z])"([.!?])',
                replacement=r'"\1\2"',
                description="Move punctuation inside quotes",
                category="dialogue",
                severity="warning"
            ),
            StyleRule(
                name="remove_speech_tags",
                pattern=r'"([^"]*)" (he|she|they) (said|replied|answered|responded)',
                replacement=r'"\1"',
                description="Remove unnecessary speech tags",
                category="dialogue", 
                severity="suggestion"
            )
        ]
    
    def _load_narrative_rules(self) -> List[StyleRule]:
        """Load narrative style rules"""
        return [
            StyleRule(
                name="present_tense_preference",
                pattern=r'\b(walked|ran|looked|saw|heard)\b',
                replacement=lambda m: {
                    "walked": "walks", "ran": "runs", "looked": "looks",
                    "saw": "sees", "heard": "hears"
                }.get(m.group(1), m.group(1)),
                description="Prefer present tense for immersion",
                category="narrative",
                severity="suggestion"
            ),
            StyleRule(
                name="atmospheric_language",
                pattern=r'\b(very|really|quite)\s+(\w+)',
                replacement=r'\2',
                description="Remove weak intensifiers",
                category="narrative",
                severity="suggestion"
            )
        ]
    
    async def apply_style_guide(self, content: str, content_type: str) -> Tuple[str, List[str]]:
        """
        Apply style guide rules to content.
        
        Args:
            content: Content to process
            content_type: Type of content (dialogue, narrative, etc.)
            
        Returns:
            Tuple of (processed_content, applied_rules)
        """
        processed_content = content
        applied_rules = []
        
        # Apply universal terminology rules
        for rule in self.terminology_rules:
            if rule.severity in ["error", "warning"]:  # Only auto-apply important rules
                if re.search(rule.pattern, processed_content, re.IGNORECASE):
                    processed_content = re.sub(
                        rule.pattern, rule.replacement, processed_content, flags=re.IGNORECASE
                    )
                    applied_rules.append(rule.name)
        
        # Apply content-type specific rules
        if content_type == "dialogue":
            for rule in self.dialogue_rules:
                if rule.severity == "error":  # Only auto-apply errors for dialogue
                    if re.search(rule.pattern, processed_content):
                        processed_content = re.sub(rule.pattern, rule.replacement, processed_content)
                        applied_rules.append(rule.name)
        
        elif content_type == "narrative":
            for rule in self.narrative_rules:
                if rule.severity in ["error", "warning"]:
                    if re.search(rule.pattern, processed_content):
                        if callable(rule.replacement):
                            processed_content = re.sub(rule.pattern, rule.replacement, processed_content)
                        else:
                            processed_content = re.sub(rule.pattern, rule.replacement, processed_content)
                        applied_rules.append(rule.name)
        
        return processed_content, applied_rules
    
    def get_style_suggestions(self, content: str, content_type: str) -> List[Dict[str, str]]:
        """Get style suggestions without auto-applying them"""
        suggestions = []
        
        all_rules = self.terminology_rules + self.dialogue_rules + self.narrative_rules
        
        for rule in all_rules:
            if rule.severity == "suggestion":
                if re.search(rule.pattern, content, re.IGNORECASE):
                    suggestions.append({
                        "rule": rule.name,
                        "description": rule.description,
                        "category": rule.category
                    })
        
        return suggestions

class ResponseProcessor:
    """
    Main response processing pipeline combining validation and style enforcement.
    
    Coordinates validation and style guide enforcement for comprehensive
    quality control of LLM-generated content.
    """
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.MODERATE):
        self.validator = ContentValidator(validation_level)
        self.style_enforcer = StyleGuideEnforcer()
    
    async def process_response(self, 
                             response: str, 
                             context: Dict[str, Any],
                             apply_style_guide: bool = True) -> Dict[str, Any]:
        """
        Process LLM response through full quality control pipeline.
        
        Args:
            response: Generated response to process
            context: Context information for validation
            apply_style_guide: Whether to auto-apply style guide rules
            
        Returns:
            Dict containing processed response and quality metrics
        """
        content_type = context.get("type", "general")
        
        # Apply style guide first (if requested)
        processed_response = response
        applied_rules = []
        
        if apply_style_guide:
            processed_response, applied_rules = await self.style_enforcer.apply_style_guide(
                response, content_type
            )
        
        # Validate the processed response
        validation_result = await self.validator.validate_response(
            processed_response, context
        )
        
        # Get style suggestions (not auto-applied)
        style_suggestions = self.style_enforcer.get_style_suggestions(
            processed_response, content_type
        )
        
        return {
            "original_response": response,
            "processed_response": processed_response,
            "validation_passed": validation_result.passed,
            "confidence_score": validation_result.confidence_score,
            "validation_issues": validation_result.issues,
            "validation_suggestions": validation_result.suggestions,
            "style_suggestions": style_suggestions,
            "applied_style_rules": applied_rules,
            "metadata": {
                **validation_result.metadata,
                "processing_timestamp": datetime.utcnow().isoformat(),
                "content_type": content_type,
                "validation_level": self.validator.validation_level.value
            }
        }
    
    async def should_regenerate(self, processing_result: Dict[str, Any]) -> bool:
        """
        Determine if response should be regenerated based on quality assessment.
        
        Args:
            processing_result: Result from process_response
            
        Returns:
            True if response should be regenerated
        """
        # Don't regenerate if validation passed with high confidence
        if (processing_result["validation_passed"] and 
            processing_result["confidence_score"] > 0.8):
            return False
        
        # Regenerate if there are critical validation issues
        critical_issues = [
            issue for issue in processing_result["validation_issues"]
            if "inappropriate" in issue.lower() or "required" in issue.lower()
        ]
        
        if critical_issues:
            return True
        
        # Regenerate if confidence is very low
        if processing_result["confidence_score"] < 0.4:
            return True
        
        return False

# Global instances
_response_processor = None

async def get_response_processor(validation_level: ValidationLevel = ValidationLevel.MODERATE) -> ResponseProcessor:
    """Get the global response processor instance"""
    global _response_processor
    if _response_processor is None:
        _response_processor = ResponseProcessor(validation_level)
    return _response_processor 