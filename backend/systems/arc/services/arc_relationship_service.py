"""
Arc Relationship Service

Manages relationships between arcs, including LLM-powered follow-up generation,
dependency validation, and dynamic outcome branching.
"""

from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from datetime import datetime
import json
import logging

from backend.systems.arc.models.arc import ArcModel, ArcRelationship, ArcRelationshipType, ArcInfluenceLevel
from backend.systems.arc.models.arc_step import ArcStepModel
from backend.systems.arc.business_rules import calculate_arc_complexity_score
from backend.infrastructure.llm.services.llm_service import LLMService, GenerationContext

logger = logging.getLogger(__name__)

class OutcomeBranchingEngine:
    """Handles dynamic story branching based on arc outcomes and player choices"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service
    
    async def generate_outcome_branches(
        self,
        completed_arc: ArcModel,
        outcome_data: Dict[str, Any],
        player_choices: List[Dict[str, Any]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate multiple possible follow-up arcs based on different outcomes.
        
        Args:
            completed_arc: The arc that was completed
            outcome_data: Data about how the arc was completed
            player_choices: Key choices made during the arc
            
        Returns:
            Dict mapping outcome types to lists of possible follow-up arcs
        """
        if self.llm_service:
            return await self._generate_llm_outcome_branches(completed_arc, outcome_data, player_choices)
        else:
            return self._generate_template_outcome_branches(completed_arc, outcome_data, player_choices)
    
    async def _generate_llm_outcome_branches(
        self,
        completed_arc: ArcModel,
        outcome_data: Dict[str, Any],
        player_choices: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate outcome branches using LLM with comprehensive context"""
        
        prompt_template = """
Create multiple branching storylines based on how this arc was completed:

**Completed Arc:**
- Title: {arc_title}
- Type: {arc_type}
- Themes: {arc_themes}
- Description: {arc_description}

**Completion Details:**
- Outcome Type: {outcome_type}
- Success Level: {success_level}
- Final Outcome: {final_outcome}
- World Changes: {world_changes}
- Character Development: {character_development}
- Unresolved Elements: {unresolved_elements}

**Key Player Choices:**
{player_choices_formatted}

**Relationship Context:**
- Predecessor Arcs: {predecessor_arcs}
- Related Arcs: {related_arcs}
- Faction Involvement: {factions}

Please create 3-5 different follow-up arc possibilities that could emerge from this completion, considering:
1. Different interpretations of the outcome
2. Various character motivations and reactions
3. Unresolved plot threads
4. New conflicts or opportunities created
5. Different emotional tones (triumph, tragedy, mystery, etc.)

For each branch, consider these outcome categories:
- **Immediate Consequences**: Direct results of the arc's conclusion
- **Long-term Implications**: How the world/characters change over time
- **Character-focused**: Personal growth and relationships
- **World-shaping**: Broader political/social impacts
- **Conflict Resolution**: Addressing unresolved tensions

Respond with a JSON object in this format:
{{
  "immediate_consequences": [
    {{
      "title": "Arc Title",
      "description": "Arc description focusing on immediate aftermath",
      "trigger_conditions": "What specific outcome triggers this arc",
      "themes": ["theme1", "theme2"],
      "estimated_complexity": "low/medium/high",
      "key_npcs": ["npc names affected"],
      "relationship_type": "sequel/consequence/branching",
      "emotional_tone": "triumph/tragedy/mystery/etc",
      "narrative_hook": "Compelling opening scenario"
    }}
  ],
  "long_term_implications": [
    // Similar structure for long-term consequences
  ],
  "character_focused": [
    // Similar structure for character development arcs
  ],
  "world_shaping": [
    // Similar structure for world-changing arcs
  ],
  "conflict_resolution": [
    // Similar structure for resolving tensions
  ]
}}
"""
        
        # Format player choices for the prompt
        choices_formatted = ""
        if player_choices:
            for i, choice in enumerate(player_choices, 1):
                choices_formatted += f"{i}. {choice.get('context', 'Unknown context')}: {choice.get('option', 'Unknown choice')} -> {choice.get('consequence', 'Unknown consequence')}\n"
        else:
            choices_formatted = "No specific choices recorded"
        
        # Build context for the prompt
        context = {
            "arc_title": completed_arc.title,
            "arc_type": completed_arc.arc_type.value,
            "arc_themes": ", ".join(completed_arc.themes or []),
            "arc_description": completed_arc.description or "",
            "outcome_type": outcome_data.get("outcome_type", "standard"),
            "success_level": outcome_data.get("success_level", "partial"),
            "final_outcome": outcome_data.get("final_outcome", "completed"),
            "world_changes": outcome_data.get("world_changes", "minimal"),
            "character_development": outcome_data.get("character_development", "moderate"),
            "unresolved_elements": outcome_data.get("unresolved_elements", "few"),
            "player_choices_formatted": choices_formatted,
            "predecessor_arcs": ", ".join([str(aid) for aid in completed_arc.predecessor_arcs]),
            "related_arcs": ", ".join([str(aid) for aid in completed_arc.related_arcs]),
            "factions": ", ".join(completed_arc.faction_ids or [])
        }
        
        try:
            response = await self.llm_service.generate_content(
                prompt=prompt_template.format(**context),
                context=GenerationContext.NARRATIVE,
                max_tokens=4000,
                temperature=0.8  # High creativity for branching narratives
            )
            
            response_text = response.get("response", "")
            return self._parse_outcome_branches_response(response_text, completed_arc)
            
        except Exception as e:
            logger.error(f"LLM outcome branching generation failed: {e}")
            return self._generate_template_outcome_branches(completed_arc, outcome_data, player_choices)
    
    def _parse_outcome_branches_response(
        self,
        response_text: str,
        completed_arc: ArcModel
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Parse LLM response into structured outcome branches"""
        import re
        
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_data = json.loads(json_str)
                
                # Enhance each branch with additional metadata
                for category, branches in parsed_data.items():
                    for branch in branches:
                        branch.update({
                            "source_arc_id": str(completed_arc.id),
                            "generated_via": "llm_branching",
                            "generation_timestamp": datetime.utcnow().isoformat(),
                            "branch_category": category
                        })
                
                return parsed_data
                
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse LLM outcome branches response: {e}")
        
        # Fallback: create basic branches from text
        return self._extract_branches_from_text(response_text, completed_arc)
    
    def _extract_branches_from_text(
        self,
        response_text: str,
        completed_arc: ArcModel
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Extract branch information from free-form text"""
        lines = response_text.split('\n')
        
        branches = {
            "immediate_consequences": [],
            "long_term_implications": [],
            "character_focused": [],
            "world_shaping": [],
            "conflict_resolution": []
        }
        
        current_branch = None
        current_category = "immediate_consequences"
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for category indicators
            line_lower = line.lower()
            if "immediate" in line_lower or "consequence" in line_lower:
                current_category = "immediate_consequences"
            elif "long" in line_lower or "term" in line_lower:
                current_category = "long_term_implications"
            elif "character" in line_lower:
                current_category = "character_focused"
            elif "world" in line_lower:
                current_category = "world_shaping"
            elif "conflict" in line_lower or "resolution" in line_lower:
                current_category = "conflict_resolution"
            
            # Look for arc titles or descriptions
            if any(keyword in line_lower for keyword in ['arc:', 'title:', 'story:']):
                if current_branch:
                    branches[current_category].append(current_branch)
                
                title = line.split(':', 1)[-1].strip() if ':' in line else line
                current_branch = {
                    "title": title,
                    "description": "",
                    "trigger_conditions": "Based on arc completion",
                    "themes": completed_arc.themes or [],
                    "estimated_complexity": "medium",
                    "key_npcs": [],
                    "relationship_type": "sequel",
                    "emotional_tone": "continuation",
                    "narrative_hook": title,
                    "source_arc_id": str(completed_arc.id),
                    "generated_via": "text_extraction",
                    "branch_category": current_category
                }
            elif current_branch and len(line) > 20:
                current_branch["description"] += f" {line}"
        
        if current_branch:
            branches[current_category].append(current_branch)
        
        # Ensure each category has at least one branch
        for category in branches:
            if not branches[category]:
                branches[category].append({
                    "title": f"Follow-up to {completed_arc.title}",
                    "description": f"A {category.replace('_', ' ')} arc following the completion of {completed_arc.title}",
                    "trigger_conditions": "Arc completion",
                    "themes": completed_arc.themes or ["continuation"],
                    "estimated_complexity": "medium",
                    "key_npcs": [],
                    "relationship_type": "sequel",
                    "emotional_tone": "continuation",
                    "narrative_hook": f"The story continues after {completed_arc.title}",
                    "source_arc_id": str(completed_arc.id),
                    "generated_via": "fallback",
                    "branch_category": category
                })
        
        return branches
    
    def _generate_template_outcome_branches(
        self,
        completed_arc: ArcModel,
        outcome_data: Dict[str, Any],
        player_choices: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Generate outcome branches using templates when LLM is unavailable"""
        
        outcome_type = outcome_data.get("outcome_type", "standard")
        success_level = outcome_data.get("success_level", "partial")
        
        # Template-based branching logic
        branch_templates = {
            "immediate_consequences": {
                "success": {
                    "title": f"Aftermath of {completed_arc.title}",
                    "description": "Deal with the immediate consequences of your success",
                    "emotional_tone": "triumph",
                    "themes": ["victory", "responsibility"]
                },
                "failure": {
                    "title": f"Rising from the Ashes",
                    "description": "Recover from the setback and find a new path forward",
                    "emotional_tone": "determination",
                    "themes": ["redemption", "perseverance"]
                },
                "partial": {
                    "title": f"Unfinished Business",
                    "description": "Address the remaining challenges left by your partial success",
                    "emotional_tone": "resolve",
                    "themes": ["completion", "determination"]
                }
            },
            "long_term_implications": {
                "success": {
                    "title": f"The New Order",
                    "description": "Navigate the world changed by your actions",
                    "emotional_tone": "transformation",
                    "themes": ["change", "adaptation"]
                },
                "failure": {
                    "title": f"Seeds of Hope",
                    "description": "Work to rebuild what was lost",
                    "emotional_tone": "hope",
                    "themes": ["rebuilding", "hope"]
                },
                "partial": {
                    "title": f"The Ongoing Struggle",
                    "description": "Continue fighting for what you believe in",
                    "emotional_tone": "perseverance",
                    "themes": ["struggle", "conviction"]
                }
            }
        }
        
        branches = {}
        
        for category, templates in branch_templates.items():
            template = templates.get(success_level, templates.get("partial"))
            
            branch = {
                **template,
                "trigger_conditions": f"Arc completed with {success_level} success",
                "estimated_complexity": "medium",
                "key_npcs": [],
                "relationship_type": "sequel",
                "narrative_hook": template["description"],
                "source_arc_id": str(completed_arc.id),
                "generated_via": "template",
                "branch_category": category
            }
            
            branches[category] = [branch]
        
        # Add default branches for other categories
        for category in ["character_focused", "world_shaping", "conflict_resolution"]:
            branches[category] = [{
                "title": f"Personal Growth",
                "description": f"A character-focused continuation exploring personal development",
                "trigger_conditions": "Arc completion",
                "themes": ["growth", "development"],
                "estimated_complexity": "low",
                "key_npcs": [],
                "relationship_type": "character_arc",
                "emotional_tone": "introspection",
                "narrative_hook": "Focus on character development",
                "source_arc_id": str(completed_arc.id),
                "generated_via": "template",
                "branch_category": category
            }]
        
        return branches
    
    async def evaluate_branching_conditions(
        self,
        completed_arc: ArcModel,
        outcome_data: Dict[str, Any],
        available_branches: Dict[str, List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluate which branches should actually trigger based on specific conditions.
        
        Args:
            completed_arc: The completed arc
            outcome_data: How the arc was completed
            available_branches: All possible branches from generate_outcome_branches
            
        Returns:
            List of branches that should actually trigger
        """
        triggered_branches = []
        
        # Evaluate each branch's trigger conditions
        for category, branches in available_branches.items():
            for branch in branches:
                if self._evaluate_trigger_condition(branch, completed_arc, outcome_data):
                    # Add triggering probability and priority
                    branch.update({
                        "trigger_probability": self._calculate_trigger_probability(branch, outcome_data),
                        "priority": self._calculate_branch_priority(branch, completed_arc),
                        "category": category
                    })
                    triggered_branches.append(branch)
        
        # Sort by priority and probability
        triggered_branches.sort(key=lambda x: (x.get("priority", 0), x.get("trigger_probability", 0)), reverse=True)
        
        return triggered_branches[:5]  # Return top 5 most relevant branches
    
    def _evaluate_trigger_condition(
        self,
        branch: Dict[str, Any],
        completed_arc: ArcModel,
        outcome_data: Dict[str, Any]
    ) -> bool:
        """Evaluate whether a branch's trigger condition is met"""
        trigger = branch.get("trigger_conditions", "").lower()
        
        # Check outcome-based triggers
        outcome_type = outcome_data.get("outcome_type", "standard").lower()
        success_level = outcome_data.get("success_level", "partial").lower()
        
        if "success" in trigger and success_level in ["success", "triumph"]:
            return True
        elif "failure" in trigger and success_level in ["failure", "defeat"]:
            return True
        elif "partial" in trigger and success_level in ["partial", "mixed"]:
            return True
        elif "completion" in trigger:  # General completion trigger
            return True
        
        # Check theme-based triggers
        arc_themes = [theme.lower() for theme in (completed_arc.themes or [])]
        branch_themes = [theme.lower() for theme in branch.get("themes", [])]
        
        if any(theme in arc_themes for theme in branch_themes):
            return True
        
        return False
    
    def _calculate_trigger_probability(self, branch: Dict[str, Any], outcome_data: Dict[str, Any]) -> float:
        """Calculate the probability that this branch should trigger"""
        base_probability = 0.5
        
        # Adjust based on outcome match
        trigger = branch.get("trigger_conditions", "").lower()
        success_level = outcome_data.get("success_level", "partial").lower()
        
        if success_level in trigger:
            base_probability += 0.3
        
        # Adjust based on complexity
        complexity = branch.get("estimated_complexity", "medium").lower()
        if complexity == "low":
            base_probability += 0.1
        elif complexity == "high":
            base_probability -= 0.1
        
        return min(1.0, max(0.0, base_probability))
    
    def _calculate_branch_priority(self, branch: Dict[str, Any], completed_arc: ArcModel) -> int:
        """Calculate priority score for branch ordering"""
        priority = 0
        
        # High priority for immediate consequences
        if branch.get("branch_category") == "immediate_consequences":
            priority += 5
        
        # High priority for character-focused arcs
        if completed_arc.arc_type.value == "character" and branch.get("branch_category") == "character_focused":
            priority += 4
        
        # Medium priority for world-shaping if it's a global arc
        if completed_arc.arc_type.value == "global" and branch.get("branch_category") == "world_shaping":
            priority += 3
        
        # Bonus for emotional engagement
        emotional_tones = ["triumph", "tragedy", "mystery", "revelation"]
        if branch.get("emotional_tone") in emotional_tones:
            priority += 2
        
        return priority

class ArcRelationshipService:
    """Service for managing arc relationships and LLM-powered follow-up generation"""
    
    def __init__(self, llm_service=None):
        """
        Initialize the relationship service.
        
        Args:
            llm_service: Service for LLM interactions (Claude, etc.)
        """
        self.llm_service = llm_service
        self.branching_engine = OutcomeBranchingEngine(llm_service)
    
    async def generate_dynamic_follow_up_arcs(
        self,
        completed_arc: ArcModel,
        outcome_data: Dict[str, Any] = None,
        player_choices: List[Dict[str, Any]] = None,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate dynamic follow-up arcs with comprehensive branching logic.
        
        Args:
            completed_arc: The arc that was completed
            outcome_data: Data about how the arc was completed
            player_choices: Key choices made during the arc
            count: Number of follow-up arcs to generate
            
        Returns:
            List of suggested arc data with branching information
        """
        if not self.llm_service:
            logger.warning("LLM service not available for dynamic follow-up generation")
            return await self.generate_follow_up_arcs(completed_arc, outcome_data, count)
        
        try:
            # Generate all possible outcome branches
            outcome_branches = await self.branching_engine.generate_outcome_branches(
                completed_arc, outcome_data or {}, player_choices or []
            )
            
            # Evaluate which branches should actually trigger
            triggered_branches = await self.branching_engine.evaluate_branching_conditions(
                completed_arc, outcome_data or {}, outcome_branches
            )
            
            # Convert top branches to arc suggestions
            suggestions = []
            for i, branch in enumerate(triggered_branches[:count]):
                arc_suggestion = {
                    "id": f"follow_up_{completed_arc.id}_{i}",
                    "title": branch["title"],
                    "description": branch["description"],
                    "arc_type": self._determine_arc_type_from_branch(branch, completed_arc),
                    "themes": branch.get("themes", []),
                    "estimated_complexity": branch.get("estimated_complexity", "medium"),
                    "narrative_hook": branch.get("narrative_hook", ""),
                    "emotional_tone": branch.get("emotional_tone", "continuation"),
                    "relationship_type": branch.get("relationship_type", "sequel"),
                    "trigger_conditions": branch.get("trigger_conditions", ""),
                    "source_arc_id": str(completed_arc.id),
                    "branch_category": branch.get("branch_category", "unknown"),
                    "trigger_probability": branch.get("trigger_probability", 0.5),
                    "priority": branch.get("priority", 0),
                    "key_npcs": branch.get("key_npcs", []),
                    "generated_via": "dynamic_branching",
                    "generation_metadata": {
                        "outcome_data": outcome_data,
                        "player_choices_count": len(player_choices) if player_choices else 0,
                        "total_branches_evaluated": len(triggered_branches)
                    }
                }
                suggestions.append(arc_suggestion)
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Dynamic follow-up generation failed: {e}")
            # Fallback to original method
            return await self.generate_follow_up_arcs(completed_arc, outcome_data, count)
    
    def _determine_arc_type_from_branch(
        self,
        branch: Dict[str, Any],
        source_arc: ArcModel
    ) -> str:
        """Determine appropriate arc type based on branch characteristics"""
        category = branch.get("branch_category", "")
        
        if category == "character_focused":
            return "character"
        elif category == "world_shaping":
            return "global" if source_arc.arc_type.value in ["global", "regional"] else "regional"
        elif category == "conflict_resolution":
            return "faction" if source_arc.faction_ids else source_arc.arc_type.value
        else:
            # Default to same type as source arc
            return source_arc.arc_type.value

    def create_relationship(
        self,
        source_arc: ArcModel,
        target_arc: ArcModel,
        relationship_type: ArcRelationshipType,
        influence_level: ArcInfluenceLevel = ArcInfluenceLevel.MODERATE,
        influence_data: Dict[str, Any] = None,
        narrative_connection: str = None
    ) -> ArcRelationship:
        """
        Create a relationship between two arcs.
        
        Args:
            source_arc: The arc that influences another
            target_arc: The arc that is influenced
            relationship_type: Type of relationship
            influence_level: Level of influence
            influence_data: Specific influence details
            narrative_connection: Description of how arcs connect
            
        Returns:
            Created ArcRelationship
        """
        # Validate relationship makes sense
        validation_errors = self._validate_relationship(
            source_arc, target_arc, relationship_type
        )
        
        if validation_errors:
            raise ValueError(f"Invalid relationship: {'; '.join(validation_errors)}")
        
        relationship = ArcRelationship(
            source_arc_id=source_arc.id,
            target_arc_id=target_arc.id,
            relationship_type=relationship_type,
            influence_level=influence_level,
            influence_data=influence_data or {},
            narrative_connection=narrative_connection
        )
        
        # Update arc models with relationship references
        self._update_arc_relationships(source_arc, target_arc, relationship_type)
        
        return relationship
    
    def _validate_relationship(
        self,
        source_arc: ArcModel,
        target_arc: ArcModel,
        relationship_type: ArcRelationshipType
    ) -> List[str]:
        """Validate that a relationship between arcs makes sense."""
        errors = []
        
        # Basic validation
        if source_arc.id == target_arc.id:
            errors.append("Arc cannot have relationship with itself")
        
        # Type-specific validation
        if relationship_type == ArcRelationshipType.SEQUEL:
            if source_arc.status not in ["completed", "active"]:
                errors.append("Sequel relationships require source arc to be completed or active")
        
        elif relationship_type == ArcRelationshipType.PREQUEL:
            if target_arc.status == "completed":
                errors.append("Cannot create prequel to completed arc")
        
        elif relationship_type == ArcRelationshipType.PARALLEL:
            if source_arc.status == "completed" and target_arc.status == "completed":
                errors.append("Parallel relationships require at least one active arc")
        
        elif relationship_type == ArcRelationshipType.BRANCHING:
            if not source_arc.outcome_influences:
                errors.append("Branching relationships require defined outcome influences")
        
        # Scope compatibility
        if source_arc.arc_type.value == "character" and target_arc.arc_type.value == "global":
            errors.append("Character arcs should not directly influence global arcs")
        
        # Timeline validation
        if (source_arc.start_date and target_arc.end_date and 
            source_arc.start_date > target_arc.end_date):
            errors.append("Source arc cannot start after target arc ends")
        
        return errors
    
    def _update_arc_relationships(
        self,
        source_arc: ArcModel,
        target_arc: ArcModel,
        relationship_type: ArcRelationshipType
    ):
        """Update arc models with relationship references."""
        if relationship_type in [ArcRelationshipType.SEQUEL, ArcRelationshipType.CONTINUATION]:
            if target_arc.id not in source_arc.successor_arcs:
                source_arc.successor_arcs.append(target_arc.id)
            if source_arc.id not in target_arc.predecessor_arcs:
                target_arc.predecessor_arcs.append(source_arc.id)
        
        elif relationship_type == ArcRelationshipType.PREQUEL:
            if source_arc.id not in target_arc.successor_arcs:
                target_arc.successor_arcs.append(source_arc.id)
            if target_arc.id not in source_arc.predecessor_arcs:
                source_arc.predecessor_arcs.append(target_arc.id)
        
        else:  # PARALLEL, THEMATIC_LINK, etc.
            if target_arc.id not in source_arc.related_arcs:
                source_arc.related_arcs.append(target_arc.id)
            if source_arc.id not in target_arc.related_arcs:
                target_arc.related_arcs.append(source_arc.id)
    
    async def generate_follow_up_arcs(
        self,
        completed_arc: ArcModel,
        outcome_data: Dict[str, Any] = None,
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Use LLM to generate follow-up arc suggestions based on completed arc.
        
        Args:
            completed_arc: The arc that was completed
            outcome_data: Data about how the arc was completed
            count: Number of follow-up arcs to generate
            
        Returns:
            List of suggested arc data
        """
        if not self.llm_service:
            raise ValueError("LLM service not configured for follow-up generation")
        
        # Generate prompt
        prompt = self._build_follow_up_prompt(completed_arc, outcome_data, count)
        
        # Call LLM
        response = await self.llm_service.generate_content(
            prompt=prompt,
            temperature=0.7,  # Creative but consistent
            max_tokens=2000
        )
        
        # Parse response into structured arc suggestions
        suggestions = self._parse_llm_response(response, completed_arc)
        
        return suggestions
    
    def _build_follow_up_prompt(
        self,
        completed_arc: ArcModel,
        outcome_data: Dict[str, Any],
        count: int
    ) -> str:
        """Build a comprehensive prompt for follow-up arc generation"""
        
        # Get complexity analysis of the completed arc
        complexity_score, factors = calculate_arc_complexity_score(completed_arc.model_dump())
        
        # Start with arc's own follow-up prompt
        base_prompt = completed_arc.get_suggested_follow_up_prompt()
        
        # Add outcome-specific information
        if outcome_data:
            outcome_section = f"""

Specific Outcome Details:
- Final outcome: {outcome_data.get('final_outcome', 'Not specified')}
- Player choices: {outcome_data.get('player_choices', 'Not specified')}
- World state changes: {outcome_data.get('world_changes', 'Not specified')}
- Character developments: {outcome_data.get('character_changes', 'Not specified')}
- Unresolved elements: {outcome_data.get('unresolved', 'Not specified')}
"""
            base_prompt += outcome_section
        
        # Add complexity and constraints
        constraints_section = f"""

Generation Constraints:
- Generate exactly {count} follow-up arc suggestions
- Original arc complexity: {complexity_score}/100 ({', '.join(factors)})
- Maintain narrative consistency with established world/characters
- Each suggestion should be significantly different from the others
- Consider both immediate and long-term consequences

Format the response as a JSON array with objects containing:
- title: Suggested arc title
- description: Brief description (2-3 sentences)
- arc_type: One of [global, regional, character, npc, faction, quest]
- relationship_type: One of [sequel, consequence, branching, thematic_link]
- influence_level: One of [minimal, moderate, major, critical]
- themes: Array of 2-4 theme strings
- estimated_complexity: Integer 1-10
- objectives: Array of 2-4 objective strings
- reasoning: Why this follow-up makes narrative sense
"""
        
        return base_prompt + constraints_section
    
    def _parse_llm_response(
        self,
        response: str,
        source_arc: ArcModel
    ) -> List[Dict[str, Any]]:
        """Parse LLM response into structured arc suggestions."""
        
        try:
            # Try to extract JSON from response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                suggestions = json.loads(json_str)
            else:
                # Fallback: try to parse as direct JSON
                suggestions = json.loads(response)
            
            # Validate and enhance suggestions
            validated_suggestions = []
            for suggestion in suggestions:
                if self._validate_suggestion(suggestion):
                    # Add relationship context
                    suggestion['source_arc_id'] = str(source_arc.id)
                    suggestion['generated_at'] = datetime.utcnow().isoformat()
                    validated_suggestions.append(suggestion)
            
            return validated_suggestions
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # If parsing fails, create manual suggestions based on text
            return self._create_fallback_suggestions(response, source_arc)
    
    def _validate_suggestion(self, suggestion: Dict[str, Any]) -> bool:
        """Validate that an LLM suggestion has required fields."""
        required_fields = ['title', 'description', 'arc_type', 'relationship_type']
        return all(field in suggestion for field in required_fields)
    
    def _create_fallback_suggestions(
        self,
        response: str,
        source_arc: ArcModel
    ) -> List[Dict[str, Any]]:
        """Create fallback suggestions if LLM response parsing fails."""
        # Extract potential titles and descriptions from text
        lines = response.strip().split('\n')
        
        suggestions = []
        current_suggestion = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for title patterns
            if line.startswith(('1.', '2.', '3.', '-', '*')) or 'Title:' in line:
                if current_suggestion:
                    suggestions.append(current_suggestion)
                
                current_suggestion = {
                    'title': line.split(':', 1)[-1].strip() if ':' in line else line,
                    'description': '',
                    'arc_type': 'regional',  # Default
                    'relationship_type': 'sequel',  # Default
                    'influence_level': 'moderate',
                    'themes': source_arc.themes,
                    'estimated_complexity': 5,
                    'source_arc_id': str(source_arc.id),
                    'generated_at': datetime.utcnow().isoformat(),
                    'reasoning': 'Generated from fallback parsing'
                }
            
            elif current_suggestion and ('description' in line.lower() or len(line) > 50):
                current_suggestion['description'] = line
        
        if current_suggestion:
            suggestions.append(current_suggestion)
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def analyze_relationship_network(
        self,
        arcs: List[ArcModel],
        relationships: List[ArcRelationship]
    ) -> Dict[str, Any]:
        """
        Analyze the network of arc relationships for insights and potential issues.
        
        Args:
            arcs: List of all arcs
            relationships: List of all relationships
            
        Returns:
            Analysis results
        """
        arc_dict = {arc.id: arc for arc in arcs}
        
        # Build adjacency maps
        predecessor_map = {arc.id: [] for arc in arcs}
        successor_map = {arc.id: [] for arc in arcs}
        related_map = {arc.id: [] for arc in arcs}
        
        for rel in relationships:
            if rel.relationship_type in [ArcRelationshipType.SEQUEL, ArcRelationshipType.CONTINUATION]:
                successor_map[rel.source_arc_id].append(rel.target_arc_id)
                predecessor_map[rel.target_arc_id].append(rel.source_arc_id)
            elif rel.relationship_type == ArcRelationshipType.PREQUEL:
                successor_map[rel.target_arc_id].append(rel.source_arc_id)
                predecessor_map[rel.source_arc_id].append(rel.target_arc_id)
            else:
                related_map[rel.source_arc_id].append(rel.target_arc_id)
                related_map[rel.target_arc_id].append(rel.source_arc_id)
        
        # Detect potential issues
        issues = []
        
        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies(predecessor_map)
        if circular_deps:
            issues.extend([f"Circular dependency: {' -> '.join(map(str, cycle))}" for cycle in circular_deps])
        
        # Check for orphaned arcs
        orphaned = [arc.id for arc in arcs if not (
            predecessor_map[arc.id] or successor_map[arc.id] or related_map[arc.id]
        )]
        
        # Calculate network metrics
        total_relationships = len(relationships)
        avg_connections = total_relationships / len(arcs) if arcs else 0
        
        # Find most connected arcs
        connection_counts = {
            arc.id: len(predecessor_map[arc.id]) + len(successor_map[arc.id]) + len(related_map[arc.id])
            for arc in arcs
        }
        most_connected = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Identify narrative chains
        chains = self._identify_narrative_chains(predecessor_map, successor_map, arc_dict)
        
        return {
            "total_arcs": len(arcs),
            "total_relationships": total_relationships,
            "average_connections_per_arc": round(avg_connections, 2),
            "orphaned_arcs": orphaned,
            "circular_dependencies": circular_deps,
            "most_connected_arcs": [
                {"arc_id": arc_id, "title": arc_dict[arc_id].title, "connections": count}
                for arc_id, count in most_connected
            ],
            "narrative_chains": chains,
            "issues": issues,
            "network_health": "good" if not issues else "needs_attention"
        }
    
    def _detect_circular_dependencies(self, predecessor_map: Dict[UUID, List[UUID]]) -> List[List[UUID]]:
        """Detect circular dependencies in arc relationships."""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in predecessor_map.get(node, []):
                dfs(neighbor, path + [node])
            
            rec_stack.remove(node)
        
        for node in predecessor_map:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def _identify_narrative_chains(
        self,
        predecessor_map: Dict[UUID, List[UUID]],
        successor_map: Dict[UUID, List[UUID]],
        arc_dict: Dict[UUID, ArcModel]
    ) -> List[Dict[str, Any]]:
        """Identify chains of connected arcs."""
        visited = set()
        chains = []
        
        def trace_chain(start_arc_id, direction='forward'):
            """Trace a chain from a starting arc."""
            chain = [start_arc_id]
            current = start_arc_id
            
            if direction == 'forward':
                while successor_map.get(current):
                    next_arcs = successor_map[current]
                    if len(next_arcs) == 1 and next_arcs[0] not in chain:
                        current = next_arcs[0]
                        chain.append(current)
                    else:
                        break
            else:  # backward
                while predecessor_map.get(current):
                    prev_arcs = predecessor_map[current]
                    if len(prev_arcs) == 1 and prev_arcs[0] not in chain:
                        current = prev_arcs[0]
                        chain.insert(0, current)
                    else:
                        break
            
            return chain
        
        for arc_id in arc_dict:
            if arc_id not in visited:
                # Find chain starting points (arcs with no predecessors)
                if not predecessor_map.get(arc_id):
                    full_chain = trace_chain(arc_id, 'forward')
                    if len(full_chain) > 1:
                        chains.append({
                            "chain_id": f"chain_{len(chains) + 1}",
                            "arc_ids": full_chain,
                            "arc_titles": [arc_dict[aid].title for aid in full_chain],
                            "length": len(full_chain),
                            "total_estimated_duration": sum(
                                arc_dict[aid].estimated_duration_hours or 0 
                                for aid in full_chain
                            )
                        })
                        visited.update(full_chain)
        
        return chains
    
    def suggest_relationship_opportunities(
        self,
        arcs: List[ArcModel]
    ) -> List[Dict[str, Any]]:
        """
        Suggest potential relationships between existing arcs.
        
        Args:
            arcs: List of arcs to analyze
            
        Returns:
            List of relationship suggestions
        """
        suggestions = []
        
        for i, arc1 in enumerate(arcs):
            for arc2 in arcs[i+1:]:
                # Skip if already related
                if (arc2.id in arc1.predecessor_arcs or 
                    arc2.id in arc1.successor_arcs or 
                    arc2.id in arc1.related_arcs):
                    continue
                
                # Check for potential relationships
                potential_relationships = self._analyze_arc_compatibility(arc1, arc2)
                if potential_relationships:
                    suggestions.extend(potential_relationships)
        
        # Sort by confidence score
        suggestions.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return suggestions[:10]  # Return top 10 suggestions
    
    def _analyze_arc_compatibility(
        self,
        arc1: ArcModel,
        arc2: ArcModel
    ) -> List[Dict[str, Any]]:
        """Analyze if two arcs could have meaningful relationships."""
        suggestions = []
        
        # Theme overlap
        theme_overlap = set(arc1.themes) & set(arc2.themes)
        
        # Faction overlap
        faction_overlap = set(arc1.faction_ids) & set(arc2.faction_ids)
        
        # Region overlap
        region_match = arc1.region_id == arc2.region_id
        
        # Character connections
        character_connection = (
            arc1.character_id == arc2.character_id or
            arc1.character_id == arc2.npc_id or
            arc1.npc_id == arc2.character_id
        )
        
        # Time-based relationships
        temporal_relationship = None
        if arc1.end_date and arc2.start_date:
            if arc1.end_date <= arc2.start_date:
                temporal_relationship = "sequential"
            elif arc1.start_date and arc2.start_date and abs((arc1.start_date - arc2.start_date).days) < 30:
                temporal_relationship = "parallel"
        
        # Generate suggestions based on compatibility factors
        if theme_overlap and len(theme_overlap) >= 2:
            suggestions.append({
                "source_arc": arc1.id,
                "target_arc": arc2.id,
                "relationship_type": "thematic_link",
                "confidence": 0.7 + len(theme_overlap) * 0.1,
                "reasoning": f"Strong thematic overlap: {', '.join(theme_overlap)}",
                "themes": list(theme_overlap)
            })
        
        if faction_overlap:
            suggestions.append({
                "source_arc": arc1.id,
                "target_arc": arc2.id,
                "relationship_type": "parallel" if temporal_relationship == "parallel" else "consequence",
                "confidence": 0.8,
                "reasoning": f"Shared factions: {', '.join(faction_overlap)}",
                "factions": list(faction_overlap)
            })
        
        if character_connection:
            suggestions.append({
                "source_arc": arc1.id,
                "target_arc": arc2.id,
                "relationship_type": "continuation" if temporal_relationship == "sequential" else "thematic_link",
                "confidence": 0.9,
                "reasoning": "Character connection between arcs",
                "character_connection": True
            })
        
        if temporal_relationship == "sequential" and (faction_overlap or theme_overlap):
            suggestions.append({
                "source_arc": arc1.id,
                "target_arc": arc2.id,
                "relationship_type": "sequel",
                "confidence": 0.8,
                "reasoning": "Sequential timing with shared elements suggests sequel relationship",
                "temporal": True
            })
        
        return suggestions 