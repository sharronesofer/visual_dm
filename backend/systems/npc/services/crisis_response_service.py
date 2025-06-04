"""
Crisis Response Service

Handles how NPCs respond to crises and disasters based on their personality,
resources, and circumstances. Integrates with personality evolution and 
emotional state systems.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID

from backend.infrastructure.systems.npc.models.personality_evolution_models import (
    NpcCrisisResponse, PersonalityChangeType
)
from backend.infrastructure.systems.npc.models.models import NpcEntity
from backend.infrastructure.systems.npc.models.autonomous_lifecycle_models import (
    NpcGoal, NpcWealth, NpcLifeEvent
)

logger = logging.getLogger(__name__)


class CrisisResponseService:
    """Service for managing NPC responses to crisis events"""
    
    def __init__(self, db_session, personality_service=None, emotional_service=None):
        self.db_session = db_session
        self.personality_service = personality_service
        self.emotional_service = emotional_service
        
        # Crisis response patterns by personality type
        self.response_patterns = {
            "flee": {
                "personality_factors": ["hidden_impulsivity", "hidden_pragmatism"],
                "required_resources": ["wealth", "mobility"],
                "effectiveness_base": 6.0
            },
            "fight": {
                "personality_factors": ["hidden_ambition", "hidden_resilience", "hidden_integrity"],
                "required_resources": ["social_connections", "physical_capability"],
                "effectiveness_base": 5.0
            },
            "hide": {
                "personality_factors": ["hidden_pragmatism"],
                "required_resources": ["safe_location", "supplies"],
                "effectiveness_base": 7.0
            },
            "adapt": {
                "personality_factors": ["hidden_resilience", "hidden_discipline", "hidden_pragmatism"],
                "required_resources": ["knowledge", "flexibility"],
                "effectiveness_base": 8.0
            },
            "help_others": {
                "personality_factors": ["hidden_integrity", "hidden_resilience"],
                "required_resources": ["social_connections", "resources"],
                "effectiveness_base": 6.0
            },
            "exploit": {
                "personality_factors": ["hidden_ambition", "hidden_pragmatism"],
                "required_resources": ["knowledge", "resources"],
                "effectiveness_base": 7.0,
                "integrity_penalty": True
            }
        }
        
        # Crisis types and their characteristics
        self.crisis_types = {
            "war": {
                "duration_range": (30, 365),
                "severity_factors": ["scope", "proximity", "duration"],
                "common_responses": ["flee", "fight", "hide"],
                "resource_threats": ["physical_safety", "property", "family"]
            },
            "plague": {
                "duration_range": (60, 180),
                "severity_factors": ["lethality", "spread_rate", "medical_knowledge"],
                "common_responses": ["hide", "flee", "help_others"],
                "resource_threats": ["health", "social_connections", "livelihood"]
            },
            "famine": {
                "duration_range": (90, 300),
                "severity_factors": ["food_scarcity", "duration", "alternative_sources"],
                "common_responses": ["adapt", "flee", "exploit"],
                "resource_threats": ["food_security", "wealth", "social_stability"]
            },
            "economic_collapse": {
                "duration_range": (180, 730),
                "severity_factors": ["scope", "recovery_prospects", "social_safety_net"],
                "common_responses": ["adapt", "exploit", "help_others"],
                "resource_threats": ["wealth", "livelihood", "social_status"]
            },
            "natural_disaster": {
                "duration_range": (1, 30),
                "severity_factors": ["destruction_level", "warning_time", "recovery_support"],
                "common_responses": ["flee", "hide", "help_others"],
                "resource_threats": ["property", "safety", "community"]
            }
        }
    
    def trigger_crisis_response(self, npc_id: UUID, crisis_type: str, 
                              crisis_description: str, crisis_severity: float,
                              crisis_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Trigger a crisis response for an NPC"""
        
        npc = self.db_session.query(NpcEntity).filter_by(id=npc_id).first()
        if not npc:
            return {"success": False, "error": "npc_not_found"}
        
        # Determine NPC's response based on personality and circumstances
        response_analysis = self._analyze_crisis_response_options(npc, crisis_type, crisis_severity, crisis_context)
        chosen_response = self._choose_response(npc, response_analysis, crisis_type)
        
        # Calculate response effectiveness
        effectiveness = self._calculate_response_effectiveness(
            npc, chosen_response, crisis_type, crisis_severity, crisis_context
        )
        
        # Determine crisis duration
        crisis_duration = self._calculate_crisis_duration(crisis_type, crisis_severity)
        
        # Create crisis response record
        crisis_response = NpcCrisisResponse(
            npc_id=npc_id,
            crisis_type=crisis_type,
            crisis_description=crisis_description,
            crisis_severity=crisis_severity,
            crisis_duration_days=crisis_duration,
            response_type=chosen_response["type"],
            response_description=chosen_response["description"],
            response_effectiveness=effectiveness,
            key_personality_factors=chosen_response.get("key_factors", []),
            crisis_start_date=datetime.utcnow()
        )
        
        # Trigger emotional response
        if self.emotional_service:
            self.emotional_service.process_emotional_trigger(
                npc_id, "crisis_event", crisis_description, crisis_severity,
                related_entity_type="crisis", location=crisis_context.get("location") if crisis_context else None
            )
        
        self.db_session.add(crisis_response)
        self.db_session.commit()
        
        # Process immediate response actions
        immediate_results = self._process_immediate_response(npc, crisis_response, crisis_context)
        
        return {
            "success": True,
            "crisis_response_id": str(crisis_response.id),
            "response_type": chosen_response["type"],
            "response_description": chosen_response["description"],
            "estimated_effectiveness": effectiveness,
            "crisis_duration_days": crisis_duration,
            "immediate_results": immediate_results
        }
    
    def _analyze_crisis_response_options(self, npc: NpcEntity, crisis_type: str, 
                                       crisis_severity: float, context: Dict[str, Any] = None) -> Dict[str, Dict]:
        """Analyze all possible response options for an NPC"""
        
        crisis_info = self.crisis_types.get(crisis_type, {})
        available_responses = crisis_info.get("common_responses", list(self.response_patterns.keys()))
        
        response_scores = {}
        
        for response_type in available_responses:
            pattern = self.response_patterns[response_type]
            score = self._calculate_response_score(npc, response_type, pattern, crisis_severity, context)
            
            response_scores[response_type] = {
                "score": score,
                "pattern": pattern,
                "feasible": score > 3.0  # Minimum feasibility threshold
            }
        
        return response_scores
    
    def _calculate_response_score(self, npc: NpcEntity, response_type: str, 
                                pattern: Dict[str, Any], crisis_severity: float,
                                context: Dict[str, Any] = None) -> float:
        """Calculate how suitable a response is for an NPC"""
        
        base_score = pattern["effectiveness_base"]
        
        # Personality alignment
        personality_score = 0.0
        for factor in pattern["personality_factors"]:
            attribute_value = getattr(npc, factor, 5.0) or 5.0
            personality_score += attribute_value
        
        personality_score = personality_score / len(pattern["personality_factors"])
        personality_multiplier = personality_score / 5.0  # Normalize to 1.0 baseline
        
        # Resource availability
        resource_score = self._assess_resource_availability(npc, pattern["required_resources"], context)
        
        # Crisis severity adjustment
        severity_adjustment = 1.0
        if crisis_severity > 8.0:  # Extreme crisis may force suboptimal responses
            severity_adjustment = 0.8
        elif crisis_severity < 3.0:  # Mild crisis allows for more choices
            severity_adjustment = 1.2
        
        # Integrity penalty for morally questionable responses
        integrity_penalty = 1.0
        if pattern.get("integrity_penalty", False):
            integrity_value = getattr(npc, 'hidden_integrity', 5.0) or 5.0
            integrity_penalty = max(0.3, (11.0 - integrity_value) / 10.0)
        
        final_score = base_score * personality_multiplier * resource_score * severity_adjustment * integrity_penalty
        
        return max(0.0, min(10.0, final_score))
    
    def _assess_resource_availability(self, npc: NpcEntity, required_resources: List[str], 
                                    context: Dict[str, Any] = None) -> float:
        """Assess how well an NPC can meet resource requirements"""
        
        resource_scores = {}
        
        for resource in required_resources:
            if resource == "wealth":
                wealth = self.db_session.query(NpcWealth).filter_by(npc_id=npc.id).first()
                if wealth:
                    # Score based on total wealth
                    total_wealth = wealth.liquid_wealth + (wealth.property_value or 0) + (wealth.business_value or 0)
                    resource_scores[resource] = min(10.0, total_wealth / 1000.0)  # Rough scaling
                else:
                    resource_scores[resource] = 3.0  # Default modest wealth
            
            elif resource == "social_connections":
                # Could integrate with relationship system
                resource_scores[resource] = 5.0  # Default for now
            
            elif resource == "mobility":
                # Based on age, health, family obligations
                age = getattr(npc, 'age', 30)
                mobility_score = 10.0 - (age / 10.0) if age > 50 else 8.0
                resource_scores[resource] = max(2.0, mobility_score)
            
            elif resource == "knowledge":
                # Could integrate with education/intelligence traits
                pragmatism = getattr(npc, 'hidden_pragmatism', 5.0) or 5.0
                discipline = getattr(npc, 'hidden_discipline', 5.0) or 5.0
                resource_scores[resource] = (pragmatism + discipline) / 2.0
            
            else:
                resource_scores[resource] = 5.0  # Default moderate availability
        
        # Return average resource availability
        return sum(resource_scores.values()) / len(resource_scores) / 10.0  # Normalize to 0-1
    
    def _choose_response(self, npc: NpcEntity, response_analysis: Dict[str, Dict], 
                        crisis_type: str) -> Dict[str, Any]:
        """Choose the best response option for an NPC"""
        
        # Filter to feasible responses
        feasible_responses = {k: v for k, v in response_analysis.items() if v["feasible"]}
        
        if not feasible_responses:
            # If no responses are feasible, default to the most personality-aligned one
            best_response = max(response_analysis.keys(), 
                              key=lambda x: response_analysis[x]["score"])
        else:
            # Choose highest scoring feasible response with some randomness
            sorted_responses = sorted(feasible_responses.items(), 
                                    key=lambda x: x[1]["score"], reverse=True)
            
            # Add some randomness - top 3 responses have a chance to be chosen
            if len(sorted_responses) >= 3:
                weights = [0.6, 0.3, 0.1]
                choice_idx = random.choices(range(min(3, len(sorted_responses))), weights=weights)[0]
                best_response = sorted_responses[choice_idx][0]
            else:
                best_response = sorted_responses[0][0]
        
        # Generate response description
        description = self._generate_response_description(npc, best_response, crisis_type)
        
        return {
            "type": best_response,
            "description": description,
            "score": response_analysis[best_response]["score"],
            "key_factors": response_analysis[best_response]["pattern"]["personality_factors"]
        }
    
    def _generate_response_description(self, npc: NpcEntity, response_type: str, 
                                     crisis_type: str) -> str:
        """Generate a descriptive narrative of the NPC's response"""
        
        name = npc.name or "The NPC"
        
        descriptions = {
            "flee": f"{name} decides to evacuate the area, gathering essential belongings and seeking safety elsewhere.",
            "fight": f"{name} chooses to stand and resist, rallying others and preparing to defend their community.",
            "hide": f"{name} seeks shelter and safety, hunkering down to wait out the crisis.",
            "adapt": f"{name} focuses on adjusting to the new circumstances, finding innovative solutions to survive.",
            "help_others": f"{name} prioritizes helping neighbors and community members through the crisis.",
            "exploit": f"{name} sees opportunities in the chaos and works to benefit from the situation."
        }
        
        base_description = descriptions.get(response_type, f"{name} responds to the {crisis_type}.")
        
        # Add personality-based flavor
        personality_flavors = {
            "high_integrity": " They are motivated by a strong sense of duty and moral obligation.",
            "high_ambition": " They see this as a chance to prove their capabilities and leadership.",
            "high_pragmatism": " They focus on practical solutions and realistic outcomes.",
            "high_resilience": " They draw on their inner strength and determination.",
            "high_discipline": " They approach the situation methodically and systematically.",
            "high_impulsivity": " They act quickly on their instincts without extensive planning."
        }
        
        # Check for high personality traits
        for trait in ['hidden_integrity', 'hidden_ambition', 'hidden_pragmatism', 
                     'hidden_resilience', 'hidden_discipline', 'hidden_impulsivity']:
            value = getattr(npc, trait, 5.0) or 5.0
            if value >= 8.0:
                trait_key = f"high_{trait.replace('hidden_', '')}"
                if trait_key in personality_flavors:
                    base_description += personality_flavors[trait_key]
                    break
        
        return base_description
    
    def _calculate_response_effectiveness(self, npc: NpcEntity, chosen_response: Dict[str, Any],
                                        crisis_type: str, crisis_severity: float,
                                        context: Dict[str, Any] = None) -> float:
        """Calculate how effective the chosen response will be"""
        
        base_effectiveness = chosen_response["score"]
        
        # Crisis severity affects all responses
        severity_factor = 1.0 - (crisis_severity - 5.0) / 10.0  # Higher severity = lower effectiveness
        
        # Random factors (luck, circumstances, etc.)
        random_factor = random.uniform(0.7, 1.3)
        
        # Context-specific adjustments
        context_factor = 1.0
        if context:
            if context.get("community_support", False):
                context_factor += 0.2
            if context.get("resource_scarcity", False):
                context_factor -= 0.3
            if context.get("prior_warning", False):
                context_factor += 0.1
        
        final_effectiveness = base_effectiveness * severity_factor * random_factor * context_factor
        
        return max(1.0, min(10.0, final_effectiveness))
    
    def _calculate_crisis_duration(self, crisis_type: str, crisis_severity: float) -> int:
        """Calculate how long the crisis will last"""
        
        crisis_info = self.crisis_types.get(crisis_type, {"duration_range": (30, 90)})
        min_duration, max_duration = crisis_info["duration_range"]
        
        # Higher severity generally means longer duration
        severity_multiplier = 0.5 + (crisis_severity / 10.0)
        base_duration = random.randint(min_duration, max_duration)
        
        return int(base_duration * severity_multiplier)
    
    def _process_immediate_response(self, npc: NpcEntity, crisis_response: NpcCrisisResponse,
                                  context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process immediate consequences of the response"""
        
        results = {
            "resource_changes": {},
            "relationship_changes": {},
            "goal_changes": {},
            "new_memories": []
        }
        
        response_type = crisis_response.response_type
        effectiveness = crisis_response.response_effectiveness
        
        # Resource impacts
        if response_type == "flee":
            # May lose property, spend money on relocation
            results["resource_changes"]["liquid_wealth"] = -random.randint(100, 500)
            results["resource_changes"]["property_loss"] = True
        
        elif response_type == "fight":
            # Risk physical harm, may gain or lose social standing
            if effectiveness > 7.0:
                results["relationship_changes"]["community_reputation"] = 2
            else:
                results["resource_changes"]["health_impact"] = -random.randint(1, 3)
        
        elif response_type == "hide":
            # Consume resources, possible isolation
            results["resource_changes"]["supplies"] = -random.randint(50, 200)
            results["relationship_changes"]["social_isolation"] = 1
        
        elif response_type == "adapt":
            # May develop new skills or connections
            if effectiveness > 6.0:
                results["goal_changes"]["new_adaptive_skills"] = True
        
        elif response_type == "help_others":
            # Gain social connections, spend resources
            results["relationship_changes"]["community_bonds"] = 3
            results["resource_changes"]["liquid_wealth"] = -random.randint(200, 800)
        
        elif response_type == "exploit":
            # Potential gains but social costs
            if effectiveness > 6.0:
                results["resource_changes"]["liquid_wealth"] = random.randint(300, 1000)
            results["relationship_changes"]["moral_reputation"] = -2
        
        # Create life event
        life_event = NpcLifeEvent(
            npc_id=npc.id,
            event_type="crisis_response",
            event_description=f"Responded to {crisis_response.crisis_type}: {crisis_response.response_description}",
            event_impact_score=crisis_response.crisis_severity,
            related_entities=[crisis_response.crisis_type],
            event_date=datetime.utcnow()
        )
        
        self.db_session.add(life_event)
        self.db_session.commit()
        
        return results
    
    def process_ongoing_crisis(self, crisis_response_id: UUID) -> Dict[str, Any]:
        """Process ongoing effects of a crisis response"""
        
        crisis_response = self.db_session.query(NpcCrisisResponse).filter_by(id=crisis_response_id).first()
        if not crisis_response:
            return {"success": False, "error": "crisis_response_not_found"}
        
        if crisis_response.response_completed:
            return {"success": False, "error": "crisis_already_completed"}
        
        days_elapsed = (datetime.utcnow() - crisis_response.crisis_start_date).days
        
        # Check if crisis should end
        if days_elapsed >= crisis_response.crisis_duration_days:
            return self._complete_crisis_response(crisis_response)
        
        # Process daily effects
        daily_effects = self._calculate_daily_crisis_effects(crisis_response, days_elapsed)
        
        # Update emotional state
        if self.emotional_service and days_elapsed % 7 == 0:  # Weekly emotional updates
            stress_level = min(10.0, crisis_response.crisis_severity + (days_elapsed / 10.0))
            self.emotional_service.process_emotional_trigger(
                crisis_response.npc_id, "ongoing_crisis_stress", 
                f"Continued stress from {crisis_response.crisis_type}",
                stress_level
            )
        
        return {
            "success": True,
            "days_elapsed": days_elapsed,
            "days_remaining": crisis_response.crisis_duration_days - days_elapsed,
            "daily_effects": daily_effects,
            "crisis_ongoing": True
        }
    
    def _calculate_daily_crisis_effects(self, crisis_response: NpcCrisisResponse, 
                                      days_elapsed: int) -> Dict[str, Any]:
        """Calculate daily effects of ongoing crisis"""
        
        effects = {
            "stress_accumulation": 0.1 * crisis_response.crisis_severity / 10.0,
            "resource_drain": {},
            "adaptation_progress": 0.0
        }
        
        # Different response types have different daily effects
        if crisis_response.response_type == "hide":
            effects["resource_drain"]["supplies"] = -5 * (crisis_response.crisis_severity / 10.0)
        
        elif crisis_response.response_type == "adapt":
            # Gradual improvement as adaptation progresses
            adaptation_rate = crisis_response.response_effectiveness / 100.0
            effects["adaptation_progress"] = adaptation_rate * days_elapsed
        
        elif crisis_response.response_type == "help_others":
            effects["resource_drain"]["energy"] = -3
            effects["social_bonds_gain"] = 0.1
        
        return effects
    
    def _complete_crisis_response(self, crisis_response: NpcCrisisResponse) -> Dict[str, Any]:
        """Complete a crisis response and process final outcomes"""
        
        crisis_response.response_completed = True
        crisis_response.crisis_end_date = datetime.utcnow()
        
        # Calculate final outcomes
        outcomes = self._calculate_crisis_outcomes(crisis_response)
        
        # Update crisis response record with outcomes
        crisis_response.personal_losses = outcomes.get("losses", [])
        crisis_response.personal_gains = outcomes.get("gains", [])
        crisis_response.lessons_learned = outcomes.get("lessons", "")
        
        # Trigger personality changes if significant enough
        if (crisis_response.crisis_severity >= 7.0 and 
            self.personality_service and 
            crisis_response.response_effectiveness < 5.0):
            
            self.personality_service.evaluate_personality_change(
                crisis_response.npc_id, "crisis_survival",
                f"Survived {crisis_response.crisis_type} through {crisis_response.response_type}",
                crisis_response.crisis_severity,
                {"response_effectiveness": crisis_response.response_effectiveness}
            )
        
        # Create completion memory
        if self.personality_service:
            memory_content = f"I survived the {crisis_response.crisis_type} by choosing to {crisis_response.response_type}. "
            if crisis_response.response_effectiveness > 7.0:
                memory_content += "My response was effective and I learned valuable lessons about crisis management."
            else:
                memory_content += "It was challenging and I learned important lessons about my limitations and strengths."
            
            self.personality_service.create_learned_memory(
                crisis_response.npc_id, "crisis_survival",
                memory_content, importance=crisis_response.crisis_severity,
                learning_context=f"{crisis_response.crisis_type}_survival"
            )
        
        self.db_session.commit()
        
        return {
            "success": True,
            "crisis_completed": True,
            "final_effectiveness": crisis_response.response_effectiveness,
            "outcomes": outcomes
        }
    
    def _calculate_crisis_outcomes(self, crisis_response: NpcCrisisResponse) -> Dict[str, Any]:
        """Calculate final outcomes of a crisis response"""
        
        effectiveness = crisis_response.response_effectiveness
        severity = crisis_response.crisis_severity
        
        outcomes = {
            "losses": [],
            "gains": [],
            "lessons": ""
        }
        
        # Base outcomes on effectiveness vs severity
        if effectiveness >= severity:
            # Successful response
            outcomes["gains"].append("Increased confidence and resilience")
            outcomes["gains"].append("Valuable crisis management experience")
            
            if crisis_response.response_type == "help_others":
                outcomes["gains"].append("Strengthened community bonds")
            elif crisis_response.response_type == "adapt":
                outcomes["gains"].append("New adaptive skills and knowledge")
            elif crisis_response.response_type == "exploit":
                outcomes["gains"].append("Financial or material gains")
                
        else:
            # Challenging response
            outcomes["losses"].append("Stress and potential trauma")
            
            if effectiveness < 4.0:
                outcomes["losses"].append("Significant resource depletion")
                if crisis_response.response_type == "fight":
                    outcomes["losses"].append("Physical or emotional injuries")
        
        # Generate lessons learned
        if crisis_response.response_type == "flee" and effectiveness > 6.0:
            outcomes["lessons"] = "Sometimes strategic retreat is the wisest choice."
        elif crisis_response.response_type == "adapt" and effectiveness > 7.0:
            outcomes["lessons"] = "Flexibility and adaptation are key to surviving challenges."
        elif crisis_response.response_type == "help_others":
            outcomes["lessons"] = "Community support makes everyone stronger during difficult times."
        else:
            outcomes["lessons"] = f"Crisis response through {crisis_response.response_type} taught valuable lessons about personal limits and capabilities."
        
        return outcomes 