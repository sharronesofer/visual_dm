"""
Autonomous Rumor Spreading System

This module provides background processes that automatically spread rumors
over time through the population, simulating realistic rumor propagation.
"""

import asyncio
import random
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from backend.systems.rumor.services.rumor_mechanics import RumorSpreadEngine, RumorDecayEngine
from backend.systems.rumor.services.advanced_mutation import (
    AdvancedContentMutator, MutationContext
)

logger = logging.getLogger(__name__)


class SpreadMode(Enum):
    """Different modes for autonomous spreading"""
    PASSIVE = "passive"      # Natural organic spreading
    ACTIVE = "active"        # Intentional spreading by NPCs
    VIRAL = "viral"          # Rapid exponential spreading
    CONTROLLED = "controlled"  # Faction-controlled spreading


@dataclass
class SpreadAgent:
    """Represents an entity that can spread rumors"""
    agent_id: str
    agent_type: str  # npc, faction, player
    location: Optional[str] = None
    personality_traits: List[str] = field(default_factory=list)
    relationships: Dict[str, float] = field(default_factory=dict)  # agent_id -> trust_level
    activity_level: float = 0.5  # How active they are in spreading
    credibility: float = 0.5     # How credible they are perceived
    current_rumors: List[str] = field(default_factory=list)  # rumor_ids they know
    last_activity: Optional[datetime] = None


@dataclass
class SpreadEvent:
    """Represents a rumor spreading event"""
    rumor_id: str
    source_agent_id: str
    target_agent_id: str
    spread_probability: float
    mutation_applied: bool = False
    success: bool = False
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AutonomousRumorSpreader:
    """Manages autonomous rumor spreading background processes"""
    
    def __init__(self):
        self.spread_engine = RumorSpreadEngine()
        self.decay_engine = RumorDecayEngine()
        self.content_mutator = AdvancedContentMutator()
        
        # Agent management
        self.agents: Dict[str, SpreadAgent] = {}
        self.location_agents: Dict[str, List[str]] = {}  # location -> agent_ids
        
        # Spreading control
        self.is_running = False
        self.spread_interval = 30  # seconds between spread cycles
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.spread_thread = None
        
        # Statistics and monitoring
        self.spread_events: List[SpreadEvent] = []
        self.stats = {
            "total_spreads": 0,
            "successful_spreads": 0,
            "mutations_applied": 0,
            "cycles_completed": 0
        }
        
        # Configuration
        self.config = self._load_spread_config()
    
    def _load_spread_config(self) -> Dict[str, Any]:
        """Load configuration for autonomous spreading"""
        return {
            "spread_cycles": {
                "base_interval": 30,  # seconds
                "variance": 0.2,      # ±20% variance
                "accelerated_intervals": {
                    "crisis": 10,     # During crisis events
                    "festival": 45,   # During festivals (slower)
                    "war": 15        # During war (faster)
                }
            },
            
            "agent_behavior": {
                "activity_decay": 0.05,     # Activity decreases over time
                "credibility_impact": 0.1,   # Credibility affects spread rate
                "relationship_threshold": 0.3,  # Minimum relationship for spreading
                "personality_multipliers": {
                    "gossipy": 2.0,
                    "dramatic": 1.5,
                    "secretive": 0.3,
                    "trustworthy": 1.2,
                    "skeptical": 0.7
                }
            },
            
            "spread_mechanics": {
                "max_rumors_per_agent": 10,    # Memory limit per agent
                "mutation_probability": 0.3,   # Chance of mutation during spread
                "viral_threshold": 0.8,        # Spread probability for viral mode
                "decay_application_interval": 300,  # Apply decay every 5 minutes
                "batch_size": 50               # Process N agents per cycle
            },
            
            "environmental_factors": {
                "location_modifiers": {
                    "tavern": 1.5,
                    "market": 1.3,
                    "palace": 0.7,
                    "temple": 0.8,
                    "wilderness": 0.3
                },
                "time_of_day_modifiers": {
                    "morning": 0.8,
                    "afternoon": 1.2,
                    "evening": 1.5,
                    "night": 0.6
                }
            }
        }
    
    def register_agent(
        self, 
        agent_id: str, 
        agent_type: str,
        location: Optional[str] = None,
        **kwargs
    ) -> SpreadAgent:
        """Register a new agent for rumor spreading"""
        
        agent = SpreadAgent(
            agent_id=agent_id,
            agent_type=agent_type,
            location=location,
            personality_traits=kwargs.get("personality_traits", []),
            activity_level=kwargs.get("activity_level", 0.5),
            credibility=kwargs.get("credibility", 0.5)
        )
        
        self.agents[agent_id] = agent
        
        # Add to location index
        if location:
            if location not in self.location_agents:
                self.location_agents[location] = []
            self.location_agents[location].append(agent_id)
        
        logger.info(f"Registered spread agent: {agent_id} ({agent_type}) at {location}")
        return agent
    
    def unregister_agent(self, agent_id: str):
        """Remove an agent from the spreading system"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            
            # Remove from location index
            if agent.location and agent.location in self.location_agents:
                if agent_id in self.location_agents[agent.location]:
                    self.location_agents[agent.location].remove(agent_id)
            
            del self.agents[agent_id]
            logger.info(f"Unregistered spread agent: {agent_id}")
    
    def seed_rumor_to_agent(self, agent_id: str, rumor_id: str, rumor_data: Dict[str, Any]):
        """Give a rumor to a specific agent"""
        if agent_id not in self.agents:
            logger.warning(f"Cannot seed rumor - agent {agent_id} not found")
            return
        
        agent = self.agents[agent_id]
        
        # Add rumor to agent's knowledge
        if rumor_id not in agent.current_rumors:
            agent.current_rumors.append(rumor_id)
            
            # Respect memory limits
            max_rumors = self.config["spread_mechanics"]["max_rumors_per_agent"]
            if len(agent.current_rumors) > max_rumors:
                # Remove oldest rumors (simple FIFO)
                agent.current_rumors = agent.current_rumors[-max_rumors:]
        
        agent.last_activity = datetime.now()
        logger.debug(f"Seeded rumor {rumor_id} to agent {agent_id}")
    
    def start_autonomous_spreading(self):
        """Start the background spreading process"""
        if self.is_running:
            logger.warning("Autonomous spreading is already running")
            return
        
        self.is_running = True
        self.spread_thread = threading.Thread(
            target=self._spread_loop,
            daemon=True
        )
        self.spread_thread.start()
        logger.info("Started autonomous rumor spreading")
    
    def stop_autonomous_spreading(self):
        """Stop the background spreading process"""
        self.is_running = False
        
        if self.spread_thread and self.spread_thread.is_alive():
            self.spread_thread.join(timeout=5)
        
        logger.info("Stopped autonomous rumor spreading")
    
    def _spread_loop(self):
        """Main spreading loop that runs in background thread"""
        last_decay_time = time.time()
        decay_interval = self.config["spread_mechanics"]["decay_application_interval"]
        
        while self.is_running:
            try:
                cycle_start = time.time()
                
                # Perform spreading cycle
                self._perform_spread_cycle()
                
                # Apply decay periodically
                current_time = time.time()
                if current_time - last_decay_time >= decay_interval:
                    self._apply_time_decay()
                    last_decay_time = current_time
                
                # Calculate next cycle interval
                base_interval = self.config["spread_cycles"]["base_interval"]
                variance = self.config["spread_cycles"]["variance"]
                
                # Add randomness to interval
                interval_modifier = 1 + random.uniform(-variance, variance)
                sleep_time = base_interval * interval_modifier
                
                # Adjust for world events (if context available)
                # This would be enhanced with actual world state
                sleep_time = max(5, sleep_time)  # Minimum 5 seconds
                
                self.stats["cycles_completed"] += 1
                
                # Sleep for calculated interval
                time.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Error in spread loop: {e}")
                time.sleep(10)  # Wait before retrying
    
    def _perform_spread_cycle(self):
        """Perform one cycle of rumor spreading"""
        batch_size = self.config["spread_mechanics"]["batch_size"]
        
        # Get active agents (those with rumors)
        active_agents = [
            agent for agent in self.agents.values()
            if agent.current_rumors
        ]
        
        if not active_agents:
            return
        
        # Shuffle for randomness
        random.shuffle(active_agents)
        
        # Process in batches
        for i in range(0, len(active_agents), batch_size):
            batch = active_agents[i:i + batch_size]
            
            # Process batch in parallel
            futures = []
            for agent in batch:
                future = self.executor.submit(self._process_agent_spreading, agent)
                futures.append(future)
            
            # Wait for batch completion
            for future in futures:
                try:
                    future.result(timeout=30)  # 30 second timeout per agent
                except Exception as e:
                    logger.error(f"Error processing agent spreading: {e}")
    
    def _process_agent_spreading(self, agent: SpreadAgent):
        """Process rumor spreading for a single agent"""
        
        # Calculate agent's current activity level
        activity = self._calculate_agent_activity(agent)
        
        if activity <= 0:
            return
        
        # Find potential targets in same location
        targets = self._find_spread_targets(agent)
        
        if not targets:
            return
        
        # Attempt to spread each rumor
        for rumor_id in agent.current_rumors.copy():
            # Check if agent should attempt to spread this rumor
            if random.random() > activity:
                continue
            
            # Select target
            target = random.choice(targets)
            
            # Calculate spread probability
            spread_prob = self._calculate_spread_probability(agent, target, rumor_id)
            
            # Attempt spread
            success = random.random() < spread_prob
            
            # Create spread event
            spread_event = SpreadEvent(
                rumor_id=rumor_id,
                source_agent_id=agent.agent_id,
                target_agent_id=target.agent_id,
                spread_probability=spread_prob,
                success=success
            )
            
            self.stats["total_spreads"] += 1
            
            if success:
                self._execute_successful_spread(agent, target, rumor_id, spread_event)
                self.stats["successful_spreads"] += 1
            
            # Record event
            self.spread_events.append(spread_event)
            
            # Keep only recent events to manage memory
            if len(self.spread_events) > 1000:
                self.spread_events = self.spread_events[-500:]
    
    def _calculate_agent_activity(self, agent: SpreadAgent) -> float:
        """Calculate an agent's current activity level"""
        base_activity = agent.activity_level
        
        # Apply personality modifiers
        personality_multiplier = 1.0
        for trait in agent.personality_traits:
            multiplier = self.config["agent_behavior"]["personality_multipliers"].get(trait, 1.0)
            personality_multiplier *= multiplier
        
        # Time decay
        if agent.last_activity:
            time_since_activity = datetime.now() - agent.last_activity
            decay_rate = self.config["agent_behavior"]["activity_decay"]
            decay_factor = max(0.1, 1.0 - (time_since_activity.total_seconds() / 3600) * decay_rate)
        else:
            decay_factor = 1.0
        
        # Environmental factors
        env_modifier = self._get_environmental_modifier(agent.location)
        
        final_activity = base_activity * personality_multiplier * decay_factor * env_modifier
        return max(0, min(1, final_activity))
    
    def _find_spread_targets(self, agent: SpreadAgent) -> List[SpreadAgent]:
        """Find potential targets for rumor spreading"""
        targets = []
        
        # Same location targets
        if agent.location and agent.location in self.location_agents:
            location_agent_ids = self.location_agents[agent.location]
            
            for target_id in location_agent_ids:
                if target_id == agent.agent_id:
                    continue
                
                if target_id in self.agents:
                    target = self.agents[target_id]
                    
                    # Check relationship threshold
                    relationship_level = agent.relationships.get(target_id, 0.5)
                    threshold = self.config["agent_behavior"]["relationship_threshold"]
                    
                    if relationship_level >= threshold:
                        targets.append(target)
        
        return targets
    
    def _calculate_spread_probability(
        self, 
        source: SpreadAgent, 
        target: SpreadAgent, 
        rumor_id: str
    ) -> float:
        """Calculate probability of successful spread between agents"""
        
        # Base probability from relationship
        relationship = source.relationships.get(target.agent_id, 0.5)
        base_prob = relationship
        
        # Source credibility modifier
        credibility_impact = self.config["agent_behavior"]["credibility_impact"]
        credibility_modifier = 1 + (source.credibility - 0.5) * credibility_impact
        
        # Target personality modifiers
        target_modifier = 1.0
        if "skeptical" in target.personality_traits:
            target_modifier *= 0.7
        if "trusting" in target.personality_traits:
            target_modifier *= 1.3
        
        # Check if target already knows this rumor
        if rumor_id in target.current_rumors:
            return 0.0  # Don't spread rumors people already know
        
        final_prob = base_prob * credibility_modifier * target_modifier
        return max(0, min(1, final_prob))
    
    def _execute_successful_spread(
        self, 
        source: SpreadAgent, 
        target: SpreadAgent, 
        rumor_id: str,
        spread_event: SpreadEvent
    ):
        """Execute a successful rumor spread"""
        
        # Check if mutation should occur
        mutation_prob = self.config["spread_mechanics"]["mutation_probability"]
        should_mutate = random.random() < mutation_prob
        
        if should_mutate:
            # Apply content mutation
            mutation_context = MutationContext(
                spreader_personality=source.personality_traits[0] if source.personality_traits else None,
                receiver_personality=target.personality_traits[0] if target.personality_traits else None,
                social_pressure=0.5,  # Could be enhanced with actual social pressure
                mutation_count=len([e for e in self.spread_events if e.rumor_id == rumor_id and e.mutation_applied])
            )
            
            # This would need actual rumor content, which would come from the rumor system
            # For now, just mark that mutation occurred
            spread_event.mutation_applied = True
            self.stats["mutations_applied"] += 1
        
        # Add rumor to target's knowledge
        target.current_rumors.append(rumor_id)
        
        # Respect memory limits
        max_rumors = self.config["spread_mechanics"]["max_rumors_per_agent"]
        if len(target.current_rumors) > max_rumors:
            target.current_rumors = target.current_rumors[-max_rumors:]
        
        # Update activity timestamps
        source.last_activity = datetime.now()
        target.last_activity = datetime.now()
        
        logger.debug(
            f"Spread {rumor_id} from {source.agent_id} to {target.agent_id}"
            f"{' (mutated)' if spread_event.mutation_applied else ''}"
        )
    
    def _apply_time_decay(self):
        """Apply time-based decay to all rumors"""
        logger.debug("Applying time decay to rumors")
        
        # This would integrate with the main rumor system
        # For now, just simulate by removing old rumors from agents
        cutoff_time = datetime.now() - timedelta(days=7)
        
        for agent in self.agents.values():
            # Remove very old rumors (simplified decay)
            if agent.last_activity and agent.last_activity < cutoff_time:
                if agent.current_rumors:
                    # Remove 1-2 old rumors
                    remove_count = random.randint(1, min(2, len(agent.current_rumors)))
                    for _ in range(remove_count):
                        agent.current_rumors.pop(0)
    
    def _get_environmental_modifier(self, location: Optional[str]) -> float:
        """Get environmental modifier for spreading based on location"""
        if not location:
            return 1.0
        
        location_modifiers = self.config["environmental_factors"]["location_modifiers"]
        
        # Match location keywords to modifiers
        location_lower = location.lower()
        for keyword, modifier in location_modifiers.items():
            if keyword in location_lower:
                return modifier
        
        return 1.0  # Default modifier
    
    def get_spreading_statistics(self) -> Dict[str, Any]:
        """Get comprehensive spreading statistics"""
        total_agents = len(self.agents)
        active_agents = len([a for a in self.agents.values() if a.current_rumors])
        total_rumors = sum(len(a.current_rumors) for a in self.agents.values())
        
        # Recent activity (last hour)
        recent_events = [
            e for e in self.spread_events 
            if e.timestamp and (datetime.now() - e.timestamp).total_seconds() < 3600
        ]
        
        success_rate = (
            self.stats["successful_spreads"] / max(1, self.stats["total_spreads"])
        ) * 100
        
        mutation_rate = (
            self.stats["mutations_applied"] / max(1, self.stats["successful_spreads"])
        ) * 100
        
        return {
            "system_status": {
                "is_running": self.is_running,
                "cycles_completed": self.stats["cycles_completed"],
                "total_agents": total_agents,
                "active_agents": active_agents,
                "total_rumors_in_circulation": total_rumors
            },
            
            "spread_statistics": {
                "total_spread_attempts": self.stats["total_spreads"],
                "successful_spreads": self.stats["successful_spreads"],
                "success_rate_percent": round(success_rate, 2),
                "mutations_applied": self.stats["mutations_applied"],
                "mutation_rate_percent": round(mutation_rate, 2)
            },
            
            "recent_activity": {
                "events_last_hour": len(recent_events),
                "successful_spreads_last_hour": len([e for e in recent_events if e.success]),
                "mutations_last_hour": len([e for e in recent_events if e.mutation_applied])
            },
            
            "agent_distribution": {
                location: len(agents) 
                for location, agents in self.location_agents.items()
            }
        }
    
    def get_agent_rumor_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get rumor status for a specific agent"""
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        
        # Count spreading events involving this agent
        as_source = len([e for e in self.spread_events if e.source_agent_id == agent_id])
        as_target = len([e for e in self.spread_events if e.target_agent_id == agent_id])
        
        return {
            "agent_id": agent_id,
            "agent_type": agent.agent_type,
            "location": agent.location,
            "current_rumors": len(agent.current_rumors),
            "activity_level": agent.activity_level,
            "credibility": agent.credibility,
            "personality_traits": agent.personality_traits,
            "last_activity": agent.last_activity.isoformat() if agent.last_activity else None,
            "spreading_stats": {
                "rumors_shared": as_source,
                "rumors_received": as_target,
                "relationships": len(agent.relationships)
            }
        }
    
    def simulate_world_event_impact(self, event_type: str, intensity: float = 1.0):
        """Simulate the impact of world events on rumor spreading"""
        
        if event_type == "crisis":
            # Increase activity and reduce intervals
            for agent in self.agents.values():
                agent.activity_level = min(1.0, agent.activity_level * (1 + intensity * 0.5))
            
        elif event_type == "festival":
            # Increase social interactions but may decrease serious rumor credibility
            for agent in self.agents.values():
                if "social" in agent.personality_traits:
                    agent.activity_level = min(1.0, agent.activity_level * (1 + intensity * 0.3))
            
        elif event_type == "war":
            # Dramatically increase military and political rumor spreading
            for agent in self.agents.values():
                agent.activity_level = min(1.0, agent.activity_level * (1 + intensity * 0.8))
        
        logger.info(f"Applied world event impact: {event_type} (intensity: {intensity})")


# Factory function
def create_autonomous_rumor_spreader() -> AutonomousRumorSpreader:
    """Create autonomous rumor spreader instance"""
    return AutonomousRumorSpreader() 