"""
Event-Driven Rumor Generation System

This module automatically generates rumors based on game events, NPC actions,
faction activities, and world state changes for dynamic storytelling.
"""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging

from backend.systems.rumor.services.content_generator import (
    ProceduralRumorGenerator, RumorCategory, RumorContext
)

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of game events that can generate rumors"""
    NPC_DEATH = "npc_death"
    NPC_BIRTH = "npc_birth"
    FACTION_CONFLICT = "faction_conflict"
    ECONOMIC_CHANGE = "economic_change"
    POLITICAL_SHIFT = "political_shift"
    TRADE_DISRUPTION = "trade_disruption"
    NATURAL_DISASTER = "natural_disaster"
    CONSTRUCTION_PROJECT = "construction_project"
    DIPLOMATIC_EVENT = "diplomatic_event"
    CRIME_INCIDENT = "crime_incident"
    RELIGIOUS_EVENT = "religious_event"
    MILITARY_MOVEMENT = "military_movement"
    RESOURCE_DISCOVERY = "resource_discovery"
    SEASONAL_CHANGE = "seasonal_change"
    FESTIVAL_EVENT = "festival_event"


@dataclass 
class GameEvent:
    """Represents a game event that can generate rumors"""
    event_type: EventType
    severity: str  # trivial, minor, moderate, major, critical
    participants: List[str]  # NPCs, factions, locations involved
    location: Optional[str] = None
    description: str = ""
    metadata: Dict[str, Any] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RumorGenerationResult:
    """Result of event-driven rumor generation"""
    rumors: List[Tuple[str, Dict[str, Any]]]
    event: GameEvent
    generation_context: Dict[str, Any]


class EventDrivenRumorGenerator:
    """Generates rumors automatically from game events"""
    
    def __init__(self):
        self.procedural_generator = ProceduralRumorGenerator()
        self.event_templates = self._load_event_templates()
        self.rumor_probability_matrix = self._load_rumor_probabilities()
        self.active_event_memory = []  # Recent events that can influence rumors
        self.faction_relationships = {}  # Will be populated from game state
        
    def _load_event_templates(self) -> Dict[str, Dict]:
        """Load event-specific rumor generation templates"""
        return {
            EventType.NPC_DEATH.value: {
                "base_templates": [
                    "{npc_name} was found dead under mysterious circumstances",
                    "The sudden death of {npc_name} has shocked everyone",
                    "{npc_name} died unexpectedly, and people are asking questions",
                    "Something suspicious about {npc_name}'s death",
                    "They say {npc_name} was poisoned by {suspected_party}",
                    "{npc_name}'s death was no accident - someone wanted them gone"
                ],
                "severity_modifiers": {
                    "trivial": ["an old", "a sick", "a frail"],
                    "minor": ["a local", "a known", "a respected"],
                    "moderate": ["an important", "a influential", "a well-connected"],
                    "major": ["a powerful", "a leading", "a prominent"],
                    "critical": ["a legendary", "the most important", "the irreplaceable"]
                },
                "rumor_categories": [RumorCategory.CRIME, RumorCategory.POLITICAL, RumorCategory.SOCIAL],
                "probability_base": 0.8
            },
            
            EventType.FACTION_CONFLICT.value: {
                "base_templates": [
                    "War is brewing between {faction_a} and {faction_b}",
                    "Tensions are escalating between {faction_a} and {faction_b}",
                    "{faction_a} is preparing to attack {faction_b}",
                    "Secret negotiations between {faction_a} and {faction_b} have failed",
                    "A spy from {faction_a} was caught in {faction_b} territory",
                    "{faction_a} has been sabotaging {faction_b} operations"
                ],
                "severity_modifiers": {
                    "trivial": ["minor disputes", "small disagreements", "petty squabbles"],
                    "minor": ["growing tensions", "diplomatic issues", "border skirmishes"],
                    "moderate": ["serious conflicts", "major disputes", "military buildup"],
                    "major": ["open warfare", "full-scale conflict", "devastating battles"],
                    "critical": ["total war", "existential threats", "civilization-ending conflict"]
                },
                "rumor_categories": [RumorCategory.MILITARY, RumorCategory.POLITICAL],
                "probability_base": 0.9
            },
            
            EventType.ECONOMIC_CHANGE.value: {
                "base_templates": [
                    "Prices of {commodity} are going to {change_direction} dramatically",
                    "The {merchant_guild} is manipulating {commodity} prices",
                    "A shortage of {commodity} is coming to {location}",
                    "New trade opportunities with {commodity} have opened up",
                    "The {commodity} market is about to collapse",
                    "Secret deals are controlling the {commodity} trade"
                ],
                "severity_modifiers": {
                    "trivial": ["slight", "minor", "small"],
                    "minor": ["noticeable", "significant", "considerable"],
                    "moderate": ["major", "substantial", "dramatic"],
                    "major": ["massive", "unprecedented", "shocking"],
                    "critical": ["catastrophic", "world-changing", "economy-destroying"]
                },
                "rumor_categories": [RumorCategory.ECONOMIC, RumorCategory.TRADE],
                "probability_base": 0.7
            },
            
            EventType.POLITICAL_SHIFT.value: {
                "base_templates": [
                    "{leader} is losing power and {rival} is taking over",
                    "New laws will soon change everything for {affected_group}",
                    "The government is planning secret changes to {policy_area}",
                    "{leader} made a deal with {external_party} behind closed doors",
                    "A coup is being planned against {current_authority}",
                    "Elections are being rigged to favor {political_faction}"
                ],
                "severity_modifiers": {
                    "trivial": ["minor policy", "small administrative", "routine procedural"],
                    "minor": ["local political", "regional governance", "municipal law"],
                    "moderate": ["significant policy", "major governmental", "important legal"],
                    "major": ["revolutionary", "regime-changing", "constitution-altering"],
                    "critical": ["civilization-defining", "world-order-changing", "history-making"]
                },
                "rumor_categories": [RumorCategory.POLITICAL],
                "probability_base": 0.85
            },
            
            EventType.CRIME_INCIDENT.value: {
                "base_templates": [
                    "A {crime_type} happened at {location} and they're covering it up",
                    "The {authority_figure} is involved in the {crime_type} at {location}",
                    "{perpetrator} was caught doing {crime_type} but escaped",
                    "There's been a string of {crime_type} incidents targeting {victim_group}",
                    "Someone saw {suspicious_person} near {crime_location} that night",
                    "The {crime_type} was an inside job - someone with access did it"
                ],
                "severity_modifiers": {
                    "trivial": ["petty", "minor", "small-time"],
                    "minor": ["local", "neighborhood", "common"],
                    "moderate": ["serious", "organized", "professional"],
                    "major": ["major", "high-profile", "shocking"],
                    "critical": ["legendary", "unprecedented", "city-shaking"]
                },
                "rumor_categories": [RumorCategory.CRIME, RumorCategory.SOCIAL],
                "probability_base": 0.75
            },
            
            EventType.MILITARY_MOVEMENT.value: {
                "base_templates": [
                    "Troops are being moved to {location} for a secret operation",
                    "The military is preparing for something big near {location}",
                    "New weapons have been seen with the {military_unit}",
                    "Foreign soldiers were spotted disguised as {cover_identity}",
                    "The {military_leader} is planning a surprise attack on {target}",
                    "Military supplies are being secretly stockpiled at {storage_location}"
                ],
                "severity_modifiers": {
                    "trivial": ["routine", "standard", "regular"],
                    "minor": ["unusual", "notable", "concerning"],
                    "moderate": ["significant", "major", "alarming"],
                    "major": ["massive", "unprecedented", "war-preparation"],
                    "critical": ["invasion-scale", "world-war", "apocalyptic"]
                },
                "rumor_categories": [RumorCategory.MILITARY, RumorCategory.POLITICAL],
                "probability_base": 0.8
            }
        }
    
    def _load_rumor_probabilities(self) -> Dict[str, Dict]:
        """Load probability matrices for event-rumor generation"""
        return {
            "event_type_multipliers": {
                EventType.NPC_DEATH.value: 1.2,
                EventType.FACTION_CONFLICT.value: 1.5,
                EventType.POLITICAL_SHIFT.value: 1.3,
                EventType.CRIME_INCIDENT.value: 1.1,
                EventType.ECONOMIC_CHANGE.value: 0.9,
                EventType.MILITARY_MOVEMENT.value: 1.4,
                EventType.NATURAL_DISASTER.value: 1.6,
                EventType.DIPLOMATIC_EVENT.value: 1.0,
                EventType.RELIGIOUS_EVENT.value: 0.8,
                EventType.TRADE_DISRUPTION.value: 0.9
            },
            
            "severity_multipliers": {
                "trivial": 0.3,
                "minor": 0.6,
                "moderate": 1.0,
                "major": 1.5,
                "critical": 2.0
            },
            
            "location_multipliers": {
                "capital": 1.3,
                "major_city": 1.1,
                "town": 1.0,
                "village": 0.8,
                "remote": 0.5
            },
            
            "time_decay_factors": {
                "immediate": 1.0,    # Within 1 hour
                "recent": 0.8,       # Within 1 day
                "old": 0.5,          # Within 1 week
                "ancient": 0.2       # Older than 1 week
            }
        }
    
    def generate_rumors_from_event(
        self, 
        event: GameEvent,
        world_context: Optional[Dict[str, Any]] = None,
        max_rumors: int = 3
    ) -> RumorGenerationResult:
        """
        Generate rumors from a specific game event
        
        Args:
            event: The game event that triggered rumor generation
            world_context: Current world state context
            max_rumors: Maximum number of rumors to generate
            
        Returns:
            RumorGenerationResult with generated rumors and metadata
        """
        
        # Calculate base probability for rumor generation
        base_probability = self._calculate_event_rumor_probability(event, world_context)
        
        # Determine number of rumors to generate
        num_rumors = self._determine_rumor_count(event, base_probability, max_rumors)
        
        generated_rumors = []
        generation_context = {
            "event_type": event.event_type.value,
            "severity": event.severity,
            "base_probability": base_probability,
            "world_context_applied": world_context is not None
        }
        
        for i in range(num_rumors):
            # Create rumor context from event
            rumor_context = self._create_rumor_context_from_event(event, world_context)
            
            # Generate rumor content
            rumor_content, rumor_metadata = self._generate_event_rumor(
                event, rumor_context, i
            )
            
            if rumor_content:
                # Add event metadata to rumor
                rumor_metadata.update({
                    "source_event": {
                        "type": event.event_type.value,
                        "severity": event.severity,
                        "timestamp": event.timestamp.isoformat() if event.timestamp else None,
                        "participants": event.participants,
                        "location": event.location
                    },
                    "generation_index": i,
                    "believability": self._calculate_initial_believability(event, rumor_context)
                })
                
                generated_rumors.append((rumor_content, rumor_metadata))
        
        # Store event in memory for future rumor generation
        self._add_event_to_memory(event)
        
        return RumorGenerationResult(
            rumors=generated_rumors,
            event=event,
            generation_context=generation_context
        )
    
    def _calculate_event_rumor_probability(
        self, 
        event: GameEvent, 
        world_context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate probability of generating rumors from an event"""
        
        # Get base probability for event type
        event_template = self.event_templates.get(event.event_type.value, {})
        base_prob = event_template.get("probability_base", 0.5)
        
        # Apply multipliers
        probabilities = self.rumor_probability_matrix
        
        type_multiplier = probabilities["event_type_multipliers"].get(
            event.event_type.value, 1.0
        )
        severity_multiplier = probabilities["severity_multipliers"].get(
            event.severity, 1.0
        )
        
        # Calculate time decay
        if event.timestamp:
            time_since = datetime.now() - event.timestamp
            if time_since.total_seconds() < 3600:  # 1 hour
                time_factor = probabilities["time_decay_factors"]["immediate"]
            elif time_since.days < 1:
                time_factor = probabilities["time_decay_factors"]["recent"]
            elif time_since.days < 7:
                time_factor = probabilities["time_decay_factors"]["old"]
            else:
                time_factor = probabilities["time_decay_factors"]["ancient"]
        else:
            time_factor = 1.0
        
        # Location multiplier
        location_type = self._classify_location(event.location)
        location_multiplier = probabilities["location_multipliers"].get(location_type, 1.0)
        
        # Context multipliers
        context_multiplier = 1.0
        if world_context:
            # High tension increases rumor probability
            if world_context.get("political_tension", 0) > 0.7:
                context_multiplier *= 1.3
            
            # War increases military rumor probability
            if event.event_type in [EventType.MILITARY_MOVEMENT, EventType.FACTION_CONFLICT]:
                if world_context.get("at_war", False):
                    context_multiplier *= 1.5
        
        final_probability = (
            base_prob * 
            type_multiplier * 
            severity_multiplier * 
            time_factor * 
            location_multiplier * 
            context_multiplier
        )
        
        return min(1.0, final_probability)
    
    def _determine_rumor_count(
        self, 
        event: GameEvent, 
        probability: float, 
        max_rumors: int
    ) -> int:
        """Determine how many rumors to generate"""
        
        # Base count from probability
        if probability < 0.3:
            base_count = 0
        elif probability < 0.6:
            base_count = 1
        elif probability < 0.8:
            base_count = 2
        else:
            base_count = 3
        
        # Adjust for severity
        severity_bonus = {
            "trivial": 0,
            "minor": 0,
            "moderate": 1,
            "major": 2,
            "critical": 3
        }
        
        total_count = base_count + severity_bonus.get(event.severity, 0)
        
        return min(max_rumors, max(0, total_count))
    
    def _create_rumor_context_from_event(
        self, 
        event: GameEvent, 
        world_context: Optional[Dict[str, Any]]
    ) -> RumorContext:
        """Create rumor generation context from event data"""
        
        context = RumorContext(
            location=event.location,
            time_period=self._get_time_period_from_event(event),
            current_events=[event.description] if event.description else []
        )
        
        # Add participants as prominent figures
        if event.participants:
            context.prominent_figures = event.participants[:3]  # Limit to avoid overwhelming
        
        # Add world context if available
        if world_context:
            context.economic_state = world_context.get("economic_state", "stable")
            context.political_climate = world_context.get("political_climate", "stable")
            
            # Infer faction from participants if available
            if event.participants and world_context.get("factions"):
                for participant in event.participants:
                    for faction_name, faction_data in world_context["factions"].items():
                        if participant in faction_data.get("members", []):
                            context.faction = faction_name
                            break
        
        return context
    
    def _generate_event_rumor(
        self, 
        event: GameEvent, 
        context: RumorContext,
        variation_index: int
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate a specific rumor from an event"""
        
        event_template = self.event_templates.get(event.event_type.value)
        if not event_template:
            # Fallback to procedural generation
            return self.procedural_generator.generate_rumor(
                context=context, 
                severity=event.severity
            )
        
        # Select base template
        base_templates = event_template["base_templates"]
        template = base_templates[variation_index % len(base_templates)]
        
        # Fill template with event data
        rumor_content = self._fill_event_template(template, event, context)
        
        # Apply severity modifiers
        severity_modifiers = event_template.get("severity_modifiers", {})
        if event.severity in severity_modifiers:
            modifier = random.choice(severity_modifiers[event.severity])
            # Simple modifier injection (can be enhanced)
            rumor_content = rumor_content.replace("a ", f"a {modifier} ", 1)
            rumor_content = rumor_content.replace("the ", f"the {modifier} ", 1)
        
        # Create metadata
        metadata = {
            "category": random.choice(event_template.get("rumor_categories", [RumorCategory.SOCIAL])).value,
            "template_used": template,
            "generation_method": "event_driven",
            "event_type": event.event_type.value,
            "variation_index": variation_index,
            "severity_modified": event.severity in severity_modifiers
        }
        
        return rumor_content, metadata
    
    def _fill_event_template(
        self, 
        template: str, 
        event: GameEvent, 
        context: RumorContext
    ) -> str:
        """Fill template with event-specific data"""
        
        content = template
        
        # Basic participant substitution
        if event.participants:
            content = content.replace("{npc_name}", event.participants[0] if event.participants else "someone")
            if len(event.participants) > 1:
                content = content.replace("{faction_a}", event.participants[0])
                content = content.replace("{faction_b}", event.participants[1])
                content = content.replace("{rival}", event.participants[1])
                content = content.replace("{suspected_party}", event.participants[1])
        
        # Location substitution
        if event.location:
            content = content.replace("{location}", event.location)
            content = content.replace("{crime_location}", event.location)
            content = content.replace("{storage_location}", event.location)
        
        # Event-specific substitutions from metadata
        if event.metadata:
            for key, value in event.metadata.items():
                placeholder = f"{{{key}}}"
                if placeholder in content and isinstance(value, str):
                    content = content.replace(placeholder, value)
        
        # Fallback substitutions for common placeholders
        fallback_substitutions = {
            "{commodity}": "grain",
            "{change_direction}": "increase",
            "{merchant_guild}": "the Traders Union",
            "{leader}": "the ruler",
            "{current_authority}": "the current government",
            "{affected_group}": "citizens",
            "{policy_area}": "taxation",
            "{external_party}": "foreign interests",
            "{political_faction}": "opposition forces",
            "{crime_type}": "theft",
            "{authority_figure}": "a guard captain",
            "{perpetrator}": "the criminal",
            "{victim_group}": "merchants",
            "{suspicious_person}": "a hooded figure",
            "{military_unit}": "the Royal Guard",
            "{military_leader}": "the general",
            "{target}": "the enemy",
            "{cover_identity}": "merchants"
        }
        
        for placeholder, fallback in fallback_substitutions.items():
            content = content.replace(placeholder, fallback)
        
        return content
    
    def _calculate_initial_believability(
        self, 
        event: GameEvent, 
        context: RumorContext
    ) -> float:
        """Calculate initial believability for event-generated rumors"""
        
        # Base believability depends on event type and severity
        base_believability = {
            "trivial": 0.4,
            "minor": 0.5,
            "moderate": 0.6,
            "major": 0.7,
            "critical": 0.8
        }
        
        believability = base_believability.get(event.severity, 0.5)
        
        # Event type modifiers
        type_modifiers = {
            EventType.NPC_DEATH.value: 0.1,    # Death is usually verifiable
            EventType.FACTION_CONFLICT.value: 0.05,  # Military events often visible
            EventType.CRIME_INCIDENT.value: -0.1,   # Crime rumors often exaggerated
            EventType.ECONOMIC_CHANGE.value: -0.05,  # Economic rumors often speculation
            EventType.POLITICAL_SHIFT.value: -0.15   # Political rumors often conspiracy
        }
        
        believability += type_modifiers.get(event.event_type.value, 0)
        
        # Recent events are more believable
        if event.timestamp:
            time_since = datetime.now() - event.timestamp
            if time_since.total_seconds() < 3600:  # Within 1 hour
                believability += 0.1
            elif time_since.days > 7:  # Over a week old
                believability -= 0.2
        
        return max(0.1, min(0.9, believability))
    
    def _get_time_period_from_event(self, event: GameEvent) -> Optional[str]:
        """Extract time period description from event"""
        if not event.timestamp:
            return None
            
        now = datetime.now()
        time_since = now - event.timestamp
        
        if time_since.total_seconds() < 3600:
            return "just happened"
        elif time_since.days < 1:
            return "today"
        elif time_since.days < 7:
            return "this week"
        else:
            return "recently"
    
    def _classify_location(self, location: Optional[str]) -> str:
        """Classify location type for probability calculations"""
        if not location:
            return "town"
        
        location_lower = location.lower()
        
        if any(keyword in location_lower for keyword in ["capital", "city center", "palace"]):
            return "capital"
        elif any(keyword in location_lower for keyword in ["city", "metropolis", "urban"]):
            return "major_city"
        elif any(keyword in location_lower for keyword in ["village", "hamlet", "settlement"]):
            return "village"
        elif any(keyword in location_lower for keyword in ["remote", "wilderness", "forest", "mountain"]):
            return "remote"
        else:
            return "town"
    
    def _add_event_to_memory(self, event: GameEvent):
        """Add event to memory for future rumor generation influence"""
        self.active_event_memory.append(event)
        
        # Keep only recent events (last 30)
        if len(self.active_event_memory) > 30:
            self.active_event_memory.pop(0)
    
    def generate_contextual_rumors(
        self, 
        world_context: Dict[str, Any],
        event_filter: Optional[List[EventType]] = None,
        max_rumors: int = 5
    ) -> List[RumorGenerationResult]:
        """
        Generate rumors based on recent events and world context
        
        Args:
            world_context: Current world state
            event_filter: Only generate rumors for these event types
            max_rumors: Maximum number of rumors to generate
            
        Returns:
            List of RumorGenerationResults
        """
        results = []
        
        # Filter events based on criteria
        eligible_events = self.active_event_memory
        if event_filter:
            eligible_events = [
                event for event in eligible_events 
                if event.event_type in event_filter
            ]
        
        # Sort by recency and importance
        eligible_events.sort(
            key=lambda e: (
                e.timestamp or datetime.min, 
                self.rumor_probability_matrix["severity_multipliers"].get(e.severity, 0)
            ),
            reverse=True
        )
        
        # Generate rumors from top events
        generated_count = 0
        for event in eligible_events:
            if generated_count >= max_rumors:
                break
                
            result = self.generate_rumors_from_event(
                event, world_context, max_rumors=2
            )
            
            if result.rumors:
                results.append(result)
                generated_count += len(result.rumors)
        
        return results
    
    def get_event_memory_summary(self) -> Dict[str, Any]:
        """Get summary of events in memory"""
        if not self.active_event_memory:
            return {"total_events": 0}
        
        summary = {
            "total_events": len(self.active_event_memory),
            "event_types": {},
            "severity_distribution": {},
            "recent_events": []
        }
        
        for event in self.active_event_memory:
            # Count event types
            event_type = event.event_type.value
            summary["event_types"][event_type] = summary["event_types"].get(event_type, 0) + 1
            
            # Count severity levels
            severity = event.severity
            summary["severity_distribution"][severity] = summary["severity_distribution"].get(severity, 0) + 1
        
        # Get 5 most recent events
        recent_events = sorted(
            self.active_event_memory, 
            key=lambda e: e.timestamp or datetime.min, 
            reverse=True
        )[:5]
        
        summary["recent_events"] = [
            {
                "type": event.event_type.value,
                "severity": event.severity,
                "participants": event.participants,
                "location": event.location,
                "timestamp": event.timestamp.isoformat() if event.timestamp else None
            }
            for event in recent_events
        ]
        
        return summary


# Factory function
def create_event_driven_rumor_generator() -> EventDrivenRumorGenerator:
    """Create event-driven rumor generator instance"""
    return EventDrivenRumorGenerator() 