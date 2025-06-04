"""
Enhanced Prompt Templates with Few-Shot Examples

This module provides sophisticated prompt engineering templates with context-aware
examples and dynamic prompt construction for improved LLM responses.
"""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import json

class PromptContext(Enum):
    """Context types for prompt selection"""
    ARC_GENERATION = "arc_generation"
    QUEST_GENERATION = "quest_generation"
    CHARACTER_DEVELOPMENT = "character_development"
    WORLD_BUILDING = "world_building"
    DIALOGUE_GENERATION = "dialogue_generation"
    OUTCOME_BRANCHING = "outcome_branching"
    NARRATIVE_CONTINUATION = "narrative_continuation"

@dataclass
class FewShotExample:
    """Structure for few-shot learning examples"""
    input_context: Dict[str, Any]
    expected_output: Dict[str, Any]
    explanation: str
    quality_score: float = 1.0  # For ranking examples

class PromptTemplate:
    """Enhanced prompt template with few-shot learning capabilities"""
    
    def __init__(
        self,
        template: str,
        context: PromptContext,
        examples: List[FewShotExample] = None,
        system_message: Optional[str] = None,
        constraints: List[str] = None,
        output_format: Optional[str] = None
    ):
        self.template = template
        self.context = context
        self.examples = examples or []
        self.system_message = system_message
        self.constraints = constraints or []
        self.output_format = output_format
    
    def format_prompt(
        self,
        variables: Dict[str, Any],
        include_examples: bool = True,
        max_examples: int = 3
    ) -> str:
        """Format the prompt with variables and examples"""
        prompt_parts = []
        
        # Add system message if available
        if self.system_message:
            prompt_parts.append(f"System: {self.system_message}\n")
        
        # Add few-shot examples if requested
        if include_examples and self.examples:
            prompt_parts.append("Here are some examples:\n")
            
            # Select best examples
            selected_examples = self._select_best_examples(variables, max_examples)
            
            for i, example in enumerate(selected_examples, 1):
                prompt_parts.append(f"Example {i}:")
                prompt_parts.append(f"Input: {json.dumps(example.input_context, indent=2)}")
                prompt_parts.append(f"Output: {json.dumps(example.expected_output, indent=2)}")
                if example.explanation:
                    prompt_parts.append(f"Explanation: {example.explanation}")
                prompt_parts.append("")
        
        # Add main prompt
        prompt_parts.append("Now, please generate content for this input:")
        prompt_parts.append(self.template.format(**variables))
        
        # Add constraints
        if self.constraints:
            prompt_parts.append("\nConstraints:")
            for constraint in self.constraints:
                prompt_parts.append(f"- {constraint}")
        
        # Add output format guidance
        if self.output_format:
            prompt_parts.append(f"\nOutput format: {self.output_format}")
        
        return "\n".join(prompt_parts)
    
    def _select_best_examples(
        self,
        variables: Dict[str, Any],
        max_examples: int
    ) -> List[FewShotExample]:
        """Select the most relevant examples based on context similarity"""
        if not self.examples:
            return []
        
        # Score examples based on relevance
        scored_examples = []
        for example in self.examples:
            relevance_score = self._calculate_relevance(variables, example.input_context)
            total_score = relevance_score * example.quality_score
            scored_examples.append((total_score, example))
        
        # Sort by score and return top examples
        scored_examples.sort(key=lambda x: x[0], reverse=True)
        return [example for _, example in scored_examples[:max_examples]]
    
    def _calculate_relevance(
        self,
        current_context: Dict[str, Any],
        example_context: Dict[str, Any]
    ) -> float:
        """Calculate relevance score between current context and example"""
        score = 0.0
        total_weight = 0.0
        
        # Compare key fields with appropriate weights
        field_weights = {
            "arc_type": 0.3,
            "themes": 0.2,
            "complexity": 0.1,
            "character_class": 0.15,
            "background": 0.15,
            "quest_type": 0.1
        }
        
        for field, weight in field_weights.items():
            if field in current_context and field in example_context:
                total_weight += weight
                
                current_val = current_context[field]
                example_val = example_context[field]
                
                if isinstance(current_val, list) and isinstance(example_val, list):
                    # Calculate overlap for lists
                    overlap = len(set(current_val) & set(example_val))
                    max_len = max(len(current_val), len(example_val))
                    if max_len > 0:
                        score += weight * (overlap / max_len)
                elif str(current_val).lower() == str(example_val).lower():
                    score += weight
        
        return score / total_weight if total_weight > 0 else 0.0

class EnhancedPromptTemplates:
    """Collection of enhanced prompt templates with few-shot examples"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[PromptContext, PromptTemplate]:
        """Initialize all prompt templates with examples"""
        return {
            PromptContext.ARC_GENERATION: self._create_arc_generation_template(),
            PromptContext.QUEST_GENERATION: self._create_quest_generation_template(),
            PromptContext.CHARACTER_DEVELOPMENT: self._create_character_development_template(),
            PromptContext.WORLD_BUILDING: self._create_world_building_template(),
            PromptContext.DIALOGUE_GENERATION: self._create_dialogue_generation_template(),
            PromptContext.OUTCOME_BRANCHING: self._create_outcome_branching_template(),
            PromptContext.NARRATIVE_CONTINUATION: self._create_narrative_continuation_template()
        }
    
    def _create_arc_generation_template(self) -> PromptTemplate:
        """Create enhanced arc generation template with examples"""
        
        examples = [
            FewShotExample(
                input_context={
                    "arc_type": "character",
                    "background": "noble",
                    "themes": ["redemption", "responsibility"],
                    "character_class": "paladin"
                },
                expected_output={
                    "title": "The Fallen Noble's Redemption",
                    "description": "A disgraced noble seeks to reclaim their honor through acts of heroism",
                    "themes": ["redemption", "responsibility", "honor"],
                    "chapters": [
                        {
                            "title": "Exile and Reflection",
                            "description": "The character confronts their fall from grace",
                            "character_growth": "Learning humility and self-reflection"
                        },
                        {
                            "title": "First Steps",
                            "description": "Small acts of heroism begin to rebuild reputation",
                            "character_growth": "Finding purpose in service to others"
                        },
                        {
                            "title": "The Great Trial",
                            "description": "A major challenge tests their commitment",
                            "character_growth": "Proving dedication to new ideals"
                        },
                        {
                            "title": "Redemption Achieved",
                            "description": "Honor is restored through sacrifice and heroism",
                            "character_growth": "Becoming a true leader and protector"
                        }
                    ]
                },
                explanation="This arc focuses on personal redemption while incorporating class-appropriate themes of honor and duty",
                quality_score=0.9
            ),
            FewShotExample(
                input_context={
                    "arc_type": "global",
                    "themes": ["war", "prophecy"],
                    "complexity": "high"
                },
                expected_output={
                    "title": "The Prophecy of the Shattered Crown",
                    "description": "An ancient prophecy unfolds as war threatens to consume the known world",
                    "themes": ["war", "prophecy", "destiny", "sacrifice"],
                    "chapters": [
                        {
                            "title": "Signs and Portents",
                            "description": "Strange omens herald the beginning of dark times",
                            "world_impact": "Growing unrest across nations"
                        },
                        {
                            "title": "The Crown Shatters",
                            "description": "A king's death sparks continental war",
                            "world_impact": "Multiple factions vie for power"
                        },
                        {
                            "title": "The Chosen Emerge",
                            "description": "Heroes rise to fulfill ancient prophecies",
                            "world_impact": "Hope returns as champions gather"
                        },
                        {
                            "title": "The Final Battle",
                            "description": "The fate of the world hangs in the balance",
                            "world_impact": "A new age begins based on the heroes' choices"
                        }
                    ]
                },
                explanation="Global arcs require large-scale consequences and multiple interconnected storylines",
                quality_score=0.95
            )
        ]
        
        return PromptTemplate(
            template="""
Create a compelling {arc_type} arc with the following characteristics:

**Background Context:** {background}
**Character Class:** {character_class}
**Themes:** {themes}
**Complexity Level:** {complexity}
**Additional Context:** {additional_context}

Please generate an arc that:
1. Builds naturally from the provided background and themes
2. Includes meaningful character growth or world development
3. Has clear narrative progression through 4-6 chapters
4. Incorporates appropriate challenges and conflicts
5. Provides satisfying resolution opportunities

**Required Format:** Return a JSON object with title, description, themes, and detailed chapters array.
""",
            context=PromptContext.ARC_GENERATION,
            examples=examples,
            system_message="You are an expert narrative designer creating compelling story arcs for tabletop RPGs",
            constraints=[
                "Each chapter must have clear objectives",
                "Character growth should be gradual and meaningful",
                "Themes should be consistently reinforced",
                "The arc should feel complete but allow for continuation"
            ],
            output_format="JSON object with title, description, themes, and chapters array"
        )
    
    def _create_quest_generation_template(self) -> PromptTemplate:
        """Create enhanced quest generation template"""
        
        examples = [
            FewShotExample(
                input_context={
                    "quest_type": "mystery",
                    "arc_theme": "corruption",
                    "location": "trading town",
                    "player_level": "medium"
                },
                expected_output={
                    "title": "The Merchant's Secret",
                    "description": "Strange disappearances in the trading quarter reveal a dark conspiracy",
                    "narrative_hook": "A respected merchant approaches you with tears in his eyes - his daughter has vanished like so many others",
                    "objectives": [
                        {
                            "id": "investigate",
                            "description": "Investigate the recent disappearances",
                            "narrative_context": "Uncovering the pattern will reveal the true threat"
                        },
                        {
                            "id": "confront",
                            "description": "Confront the corrupt official behind the scheme",
                            "narrative_context": "Justice must be served to prevent future victims"
                        }
                    ],
                    "key_npcs": [
                        {
                            "name": "Merchant Aldric",
                            "role": "quest_giver",
                            "dialogue_sample": "Please, heroes - my daughter means everything to me. I'll give you anything if you can bring her home safely."
                        }
                    ]
                },
                explanation="Mystery quests should build tension through investigation and revelation",
                quality_score=0.9
            )
        ]
        
        return PromptTemplate(
            template="""
Create a {quest_type} quest that fits within this narrative context:

**Arc Theme:** {arc_theme}
**Current Location:** {location}
**Player Experience Level:** {player_level}
**Step Context:** {step_context}
**World Setting:** {world_setting}

The quest should:
1. Flow naturally from the arc narrative
2. Provide meaningful choices and challenges
3. Include rich NPCs and atmospheric locations
4. Have clear but engaging objectives
5. Advance the larger story

**Format:** JSON object with title, description, narrative_hook, objectives, key_npcs, locations, and rewards.
""",
            context=PromptContext.QUEST_GENERATION,
            examples=examples,
            constraints=[
                "Objectives must be specific and achievable",
                "NPCs should have distinct personalities",
                "Rewards should match the effort required",
                "The quest should feel connected to the larger narrative"
            ]
        )
    
    def _create_character_development_template(self) -> PromptTemplate:
        """Create character development template"""
        
        examples = [
            FewShotExample(
                input_context={
                    "character_class": "rogue",
                    "background": "criminal",
                    "personality_traits": ["cynical", "loyal"],
                    "bonds": ["protects younger sibling"],
                    "flaws": ["trusts no one"]
                },
                expected_output={
                    "arc_title": "Learning to Trust",
                    "emotional_journey": "From isolation and suspicion to opening up and accepting help from others",
                    "growth_opportunities": [
                        {
                            "trigger": "Team member risks themselves for the rogue",
                            "growth": "Begins to question their belief that everyone is selfish",
                            "internal_conflict": "Wants to trust but fears betrayal"
                        },
                        {
                            "trigger": "Must rely on others to save their sibling",
                            "growth": "Learns that vulnerability can be strength",
                            "internal_conflict": "Pride versus love for family"
                        }
                    ]
                },
                explanation="Character development should address flaws while honoring bonds and traits",
                quality_score=0.85
            )
        ]
        
        return PromptTemplate(
            template="""
Design character development opportunities for:

**Class:** {character_class}
**Background:** {background}
**Personality Traits:** {personality_traits}
**Bonds:** {bonds}
**Flaws:** {flaws}
**Ideals:** {ideals}

Create a character growth arc that:
1. Addresses their flaws constructively
2. Leverages their bonds and ideals
3. Provides meaningful internal conflict
4. Shows gradual, believable change
5. Maintains their core identity

**Format:** JSON with arc_title, emotional_journey, and growth_opportunities array.
""",
            context=PromptContext.CHARACTER_DEVELOPMENT,
            examples=examples
        )
    
    def _create_world_building_template(self) -> PromptTemplate:
        """Create world building template"""
        return PromptTemplate(
            template="""
Expand the world setting for:

**Current Location:** {location}
**Theme:** {theme}
**Culture Level:** {culture_level}
**Notable Features:** {features}
**Historical Context:** {history}

Create rich world details including:
1. Physical geography and climate
2. Political structures and tensions
3. Cultural practices and beliefs
4. Economic systems and trade
5. Threats and opportunities
6. Notable NPCs and factions

**Format:** JSON with comprehensive world details.
""",
            context=PromptContext.WORLD_BUILDING,
            constraints=[
                "Details should feel realistic and lived-in",
                "Include both mundane and fantastical elements",
                "Create potential for interesting conflicts",
                "Maintain internal consistency"
            ]
        )
    
    def _create_dialogue_generation_template(self) -> PromptTemplate:
        """Create dialogue generation template"""
        return PromptTemplate(
            template="""
Generate dialogue for:

**Speaker:** {speaker_name}
**Character Traits:** {character_traits}
**Emotional State:** {emotional_state}
**Context:** {dialogue_context}
**Relationship to PC:** {relationship}
**Goal in Conversation:** {conversation_goal}

Create authentic dialogue that:
1. Reflects the character's personality and background
2. Matches their emotional state
3. Advances the conversation goal
4. Feels natural and engaging
5. Includes appropriate subtext

**Format:** JSON with dialogue lines and stage directions.
""",
            context=PromptContext.DIALOGUE_GENERATION,
            constraints=[
                "Dialogue should sound natural when spoken aloud",
                "Include emotional subtext and character voice",
                "Maintain consistency with established personality",
                "Leave room for player responses"
            ]
        )
    
    def _create_outcome_branching_template(self) -> PromptTemplate:
        """Create outcome branching template"""
        return PromptTemplate(
            template="""
Create branching storylines based on:

**Completed Event:** {completed_event}
**Outcome Type:** {outcome_type}
**Player Choices:** {player_choices}
**World State:** {world_state}
**Character Development:** {character_development}

Generate 3-5 possible follow-up scenarios that:
1. Flow logically from the outcome
2. Offer different emotional tones and themes
3. Provide meaningful consequences
4. Create new opportunities for engagement
5. Maintain narrative momentum

**Format:** JSON array of branching scenarios with triggers and descriptions.
""",
            context=PromptContext.OUTCOME_BRANCHING,
            constraints=[
                "Each branch should feel distinctly different",
                "Consider both immediate and long-term consequences",
                "Include emotional and practical ramifications",
                "Maintain player agency in future choices"
            ]
        )
    
    def _create_narrative_continuation_template(self) -> PromptTemplate:
        """Create narrative continuation template"""
        return PromptTemplate(
            template="""
Continue the narrative from:

**Previous Events:** {previous_events}
**Current Situation:** {current_situation}
**Active Conflicts:** {active_conflicts}
**Character States:** {character_states}
**Desired Tone:** {narrative_tone}

Create compelling continuation that:
1. Builds on established events and character development
2. Maintains narrative consistency
3. Introduces new elements without disrupting flow
4. Provides opportunities for character agency
5. Advances toward meaningful resolution

**Format:** JSON with narrative segments and character moments.
""",
            context=PromptContext.NARRATIVE_CONTINUATION,
            constraints=[
                "Maintain consistency with established facts",
                "Honor character development so far",
                "Include both action and character moments",
                "Create natural transition points"
            ]
        )
    
    def get_template(self, context: PromptContext) -> PromptTemplate:
        """Get template for specific context"""
        return self.templates.get(context)
    
    def format_prompt(
        self,
        context: PromptContext,
        variables: Dict[str, Any],
        include_examples: bool = True,
        max_examples: int = 3
    ) -> str:
        """Format prompt for specific context with variables"""
        template = self.get_template(context)
        if not template:
            raise ValueError(f"No template found for context: {context}")
        
        return template.format_prompt(variables, include_examples, max_examples)

# Global instance
enhanced_prompts = EnhancedPromptTemplates() 