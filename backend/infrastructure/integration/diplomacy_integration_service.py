"""
Diplomacy Integration Service

Infrastructure service that handles cross-system integration for the diplomacy system,
connecting with faction, economy, combat, and other game systems through event-driven
architecture and service interfaces.
"""

from typing import Dict, List, Any, Optional, Callable
from uuid import UUID
from datetime import datetime
import asyncio

# Infrastructure imports
from backend.infrastructure.events import get_event_bus, EventBase
from backend.infrastructure.analytics.diplomacy_analytics_service import create_diplomacy_analytics_service
from backend.infrastructure.llm.services.diplomatic_narrative_service import create_diplomatic_narrative_service

# Business system imports (interfaces only)
from backend.systems.diplomacy.services.core_services import DiplomacyService, TensionService


class DiplomacyIntegrationService:
    """
    Infrastructure service for diplomacy system integrations.
    
    Manages cross-system communication, event handling, and data synchronization
    between the diplomacy system and other game systems.
    """
    
    def __init__(self):
        self.event_bus = get_event_bus()
        self.analytics_service = create_diplomacy_analytics_service()
        self.narrative_service = create_diplomatic_narrative_service()
        
        # Service references (lazy-loaded)
        self._diplomacy_service = None
        self._tension_service = None
        
        # Integration handlers
        self.integration_handlers = {
            "faction": {},
            "economy": {},
            "combat": {},
            "population": {},
            "espionage": {}
        }
        
        # Event subscriptions
        self._setup_event_subscriptions()
    
    @property
    def diplomacy_service(self) -> DiplomacyService:
        """Lazy-loaded diplomacy service."""
        if self._diplomacy_service is None:
            self._diplomacy_service = DiplomacyService()
        return self._diplomacy_service
    
    @property
    def tension_service(self) -> TensionService:
        """Lazy-loaded tension service."""
        if self._tension_service is None:
            self._tension_service = TensionService()
        return self._tension_service
    
    def _setup_event_subscriptions(self):
        """Set up event subscriptions for cross-system integration."""
        
        # Faction system events
        self.event_bus.subscribe("faction_created", self._handle_faction_created)
        self.event_bus.subscribe("faction_destroyed", self._handle_faction_destroyed)
        self.event_bus.subscribe("faction_leadership_changed", self._handle_faction_leadership_changed)
        self.event_bus.subscribe("faction_ideology_changed", self._handle_faction_ideology_changed)
        
        # Economy system events
        self.event_bus.subscribe("trade_route_established", self._handle_trade_route_established)
        self.event_bus.subscribe("trade_route_disrupted", self._handle_trade_route_disrupted)
        self.event_bus.subscribe("resource_shortage", self._handle_resource_shortage)
        self.event_bus.subscribe("economic_crisis", self._handle_economic_crisis)
        self.event_bus.subscribe("trade_agreement_violated", self._handle_trade_agreement_violated)
        
        # Combat system events
        self.event_bus.subscribe("combat_initiated", self._handle_combat_initiated)
        self.event_bus.subscribe("combat_concluded", self._handle_combat_concluded)
        self.event_bus.subscribe("territory_captured", self._handle_territory_captured)
        self.event_bus.subscribe("military_buildup", self._handle_military_buildup)
        self.event_bus.subscribe("border_incident", self._handle_border_incident)
        
        # Population system events
        self.event_bus.subscribe("population_migrated", self._handle_population_migrated)
        self.event_bus.subscribe("civil_unrest", self._handle_civil_unrest)
        self.event_bus.subscribe("cultural_influence_changed", self._handle_cultural_influence_changed)
        
        # Espionage system events
        self.event_bus.subscribe("espionage_discovered", self._handle_espionage_discovered)
        self.event_bus.subscribe("intelligence_gathered", self._handle_intelligence_gathered)
        self.event_bus.subscribe("spy_captured", self._handle_spy_captured)
    
    # Faction System Integration
    
    async def _handle_faction_created(self, event_data: Dict[str, Any]):
        """Handle new faction creation."""
        faction_id = UUID(event_data["faction_id"])
        
        # Initialize diplomatic relationships for new faction
        existing_factions = event_data.get("existing_factions", [])
        for other_faction_id in existing_factions:
            await self.tension_service.initialize_relationship(
                faction_id, UUID(other_faction_id)
            )
        
        # Track analytics
        await self.analytics_service.track_websocket_activity("faction_created", faction_id)
        
        # Publish diplomatic event
        self.event_bus.publish("diplomatic_initialization", {
            "new_faction_id": str(faction_id),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _handle_faction_destroyed(self, event_data: Dict[str, Any]):
        """Handle faction destruction."""
        faction_id = UUID(event_data["faction_id"])
        destroyer_id = event_data.get("destroyer_id")
        
        # Terminate all treaties involving this faction
        treaties = self.diplomacy_service.list_treaties(faction_id=faction_id, active_only=True)
        for treaty in treaties:
            self.diplomacy_service.terminate_treaty(treaty.id, reason="Faction eliminated")
        
        # Cancel active negotiations
        negotiations = self.diplomacy_service.get_active_negotiations(faction_id)
        for negotiation in negotiations:
            self.diplomacy_service.cancel_negotiation(negotiation.id, reason="Faction eliminated")
        
        # Update tensions with destroyer
        if destroyer_id:
            destroyer_uuid = UUID(destroyer_id)
            # This would typically increase tensions with allied factions
            allied_factions = await self._get_allied_factions(faction_id)
            for ally_id in allied_factions:
                await self.tension_service.modify_tension(
                    ally_id, destroyer_uuid, 30, "Allied faction destroyed"
                )
    
    async def _handle_faction_leadership_changed(self, event_data: Dict[str, Any]):
        """Handle faction leadership changes."""
        faction_id = UUID(event_data["faction_id"])
        old_leader = event_data.get("old_leader")
        new_leader = event_data.get("new_leader")
        change_type = event_data.get("change_type", "succession")
        
        # Leadership changes can affect diplomatic relationships
        if change_type in ["coup", "revolution"]:
            # Violent leadership changes increase tensions
            await self._apply_tension_to_neighbors(faction_id, 10, "Political instability")
        elif change_type == "election":
            # Democratic transitions might improve relationships
            await self._apply_tension_to_neighbors(faction_id, -5, "Democratic transition")
        
        # Generate diplomatic incident if violent
        if change_type in ["coup", "assassination"]:
            await self._create_diplomatic_incident(
                faction_id, None, "POLITICAL_CRISIS",
                f"Leadership change in faction: {change_type}",
                severity="MAJOR"
            )
    
    # Economy System Integration
    
    async def _handle_trade_route_established(self, event_data: Dict[str, Any]):
        """Handle new trade route establishment."""
        faction_a = UUID(event_data["faction_a"])
        faction_b = UUID(event_data["faction_b"])
        trade_value = event_data.get("trade_value", 0)
        
        # Trade relationships improve diplomatic relations
        tension_reduction = min(15, int(trade_value / 1000))  # Scale with trade value
        await self.tension_service.modify_tension(
            faction_a, faction_b, -tension_reduction, "Trade route established"
        )
        
        # Update relationship trade volume
        relationship = await self.tension_service.get_relationship(faction_a, faction_b)
        if relationship:
            new_volume = relationship.trade_volume + trade_value
            await self.tension_service.update_trade_volume(faction_a, faction_b, new_volume)
    
    async def _handle_trade_route_disrupted(self, event_data: Dict[str, Any]):
        """Handle trade route disruption."""
        faction_a = UUID(event_data["faction_a"])
        faction_b = UUID(event_data["faction_b"])
        disruptor_id = event_data.get("disruptor_id")
        reason = event_data.get("reason", "Unknown disruption")
        
        # Trade disruption increases tensions
        await self.tension_service.modify_tension(
            faction_a, faction_b, 10, f"Trade route disrupted: {reason}"
        )
        
        # If disrupted by third party, increase tensions with disruptor
        if disruptor_id:
            disruptor_uuid = UUID(disruptor_id)
            await self.tension_service.modify_tension(
                faction_a, disruptor_uuid, 15, "Trade route disruption"
            )
            await self.tension_service.modify_tension(
                faction_b, disruptor_uuid, 15, "Trade route disruption"
            )
    
    async def _handle_trade_agreement_violated(self, event_data: Dict[str, Any]):
        """Handle trade agreement violations."""
        violator_id = UUID(event_data["violator_id"])
        victim_id = UUID(event_data["victim_id"])
        violation_type = event_data.get("violation_type", "TRADE_EMBARGO")
        severity = event_data.get("severity", "MINOR")
        
        # Check if this violates any treaties
        treaties = self.diplomacy_service.list_treaties(faction_id=violator_id, active_only=True)
        for treaty in treaties:
            if victim_id in treaty.parties and "trade" in treaty.terms:
                # Report treaty violation
                await self.diplomacy_service.report_treaty_violation(
                    treaty_id=treaty.id,
                    violator_faction_id=violator_id,
                    violation_type="TRADE_VIOLATION",
                    description=f"Trade agreement violation: {violation_type}",
                    affected_faction_id=victim_id
                )
    
    # Combat System Integration
    
    async def _handle_combat_initiated(self, event_data: Dict[str, Any]):
        """Handle combat initiation."""
        aggressor_id = UUID(event_data["aggressor_id"])
        defender_id = UUID(event_data["defender_id"])
        combat_type = event_data.get("combat_type", "SKIRMISH")
        location = event_data.get("location")
        
        # Combat dramatically increases tensions
        tension_increase = 50 if combat_type == "MAJOR_BATTLE" else 25
        await self.tension_service.modify_tension(
            aggressor_id, defender_id, tension_increase, f"Combat initiated: {combat_type}"
        )
        
        # Check for treaty violations
        await self._check_combat_treaty_violations(aggressor_id, defender_id, combat_type)
        
        # Create diplomatic incident
        await self._create_diplomatic_incident(
            aggressor_id, defender_id, "BORDER_VIOLATION",
            f"Combat initiated: {combat_type}",
            severity="MAJOR" if combat_type == "MAJOR_BATTLE" else "MODERATE"
        )
        
        # Allies might get involved
        await self._handle_alliance_obligations(aggressor_id, defender_id, "combat_defense")
    
    async def _handle_combat_concluded(self, event_data: Dict[str, Any]):
        """Handle combat conclusion."""
        winner_id = event_data.get("winner_id")
        loser_id = event_data.get("loser_id")
        outcome = event_data.get("outcome", "DECISIVE")
        casualties = event_data.get("casualties", {})
        
        if winner_id and loser_id:
            winner_uuid = UUID(winner_id)
            loser_uuid = UUID(loser_id)
            
            # Winner gains prestige, loser loses face
            if outcome == "DECISIVE":
                await self._apply_tension_to_neighbors(winner_uuid, -5, "Military victory")
                await self._apply_tension_to_neighbors(loser_uuid, 10, "Military defeat")
    
    async def _handle_territory_captured(self, event_data: Dict[str, Any]):
        """Handle territory capture."""
        captor_id = UUID(event_data["captor_id"])
        former_owner_id = UUID(event_data["former_owner_id"])
        territory_value = event_data.get("territory_value", 1)
        
        # Territory capture is a major diplomatic event
        tension_increase = 40 + (territory_value * 10)
        await self.tension_service.modify_tension(
            former_owner_id, captor_id, tension_increase, "Territory captured"
        )
        
        # Allies of the victim are also affected
        allied_factions = await self._get_allied_factions(former_owner_id)
        for ally_id in allied_factions:
            await self.tension_service.modify_tension(
                ally_id, captor_id, 20, "Allied territory captured"
            )
    
    async def _handle_border_incident(self, event_data: Dict[str, Any]):
        """Handle border incidents."""
        faction_a = UUID(event_data["faction_a"])
        faction_b = UUID(event_data["faction_b"])
        incident_type = event_data.get("incident_type", "BORDER_CROSSING")
        severity = event_data.get("severity", "MINOR")
        
        # Border incidents create diplomatic tensions
        tension_map = {"MINOR": 5, "MODERATE": 15, "MAJOR": 25}
        tension_increase = tension_map.get(severity, 10)
        
        await self.tension_service.modify_tension(
            faction_a, faction_b, tension_increase, f"Border incident: {incident_type}"
        )
        
        # Create diplomatic incident
        await self._create_diplomatic_incident(
            faction_a, faction_b, "BORDER_VIOLATION",
            f"Border incident: {incident_type}",
            severity=severity
        )
    
    # Population System Integration
    
    async def _handle_population_migrated(self, event_data: Dict[str, Any]):
        """Handle population migration."""
        source_faction = UUID(event_data["source_faction"])
        destination_faction = UUID(event_data["destination_faction"])
        migration_size = event_data.get("migration_size", 0)
        migration_type = event_data.get("migration_type", "VOLUNTARY")
        
        if migration_type == "REFUGEE":
            # Refugee movements can strain relationships
            await self.tension_service.modify_tension(
                destination_faction, source_faction, 5, "Refugee crisis burden"
            )
        elif migration_type == "ECONOMIC":
            # Economic migration might improve relationships
            await self.tension_service.modify_tension(
                source_faction, destination_faction, -2, "Economic cooperation"
            )
    
    async def _handle_civil_unrest(self, event_data: Dict[str, Any]):
        """Handle civil unrest events."""
        faction_id = UUID(event_data["faction_id"])
        unrest_level = event_data.get("unrest_level", "MODERATE")
        cause = event_data.get("cause", "Economic hardship")
        
        # Civil unrest affects diplomatic relationships
        if unrest_level in ["HIGH", "EXTREME"]:
            await self._apply_tension_to_neighbors(
                faction_id, 5, f"Political instability: {cause}"
            )
            
            # Create diplomatic incident
            await self._create_diplomatic_incident(
                faction_id, None, "POLITICAL_CRISIS",
                f"Civil unrest: {cause}",
                severity="MODERATE" if unrest_level == "HIGH" else "MAJOR"
            )
    
    # Espionage System Integration
    
    async def _handle_espionage_discovered(self, event_data: Dict[str, Any]):
        """Handle discovered espionage activities."""
        spy_faction = UUID(event_data["spy_faction"])
        target_faction = UUID(event_data["target_faction"])
        espionage_type = event_data.get("espionage_type", "INTELLIGENCE")
        severity = event_data.get("severity", "MODERATE")
        
        # Espionage discovery creates significant diplomatic incidents
        tension_map = {"MINOR": 15, "MODERATE": 25, "MAJOR": 40}
        tension_increase = tension_map.get(severity, 25)
        
        await self.tension_service.modify_tension(
            target_faction, spy_faction, tension_increase, f"Espionage discovered: {espionage_type}"
        )
        
        # Create diplomatic incident
        await self._create_diplomatic_incident(
            spy_faction, target_faction, "ESPIONAGE_DISCOVERY",
            f"Espionage activity discovered: {espionage_type}",
            severity=severity
        )
        
        # Check for treaty violations
        treaties = self.diplomacy_service.list_treaties(faction_id=spy_faction, active_only=True)
        for treaty in treaties:
            if target_faction in treaty.parties:
                await self.diplomacy_service.report_treaty_violation(
                    treaty_id=treaty.id,
                    violator_faction_id=spy_faction,
                    violation_type="ESPIONAGE",
                    description=f"Espionage activity: {espionage_type}",
                    affected_faction_id=target_faction
                )
    
    # Helper Methods
    
    async def _get_allied_factions(self, faction_id: UUID) -> List[UUID]:
        """Get list of allied factions."""
        treaties = self.diplomacy_service.list_treaties(faction_id=faction_id, active_only=True)
        allies = []
        
        for treaty in treaties:
            if treaty.type in ["ALLIANCE", "MUTUAL_DEFENSE"]:
                for party in treaty.parties:
                    if party != faction_id:
                        allies.append(party)
        
        return allies
    
    async def _apply_tension_to_neighbors(self, faction_id: UUID, tension_change: int, reason: str):
        """Apply tension change to all neighboring factions."""
        # This would typically get neighboring factions from a geography service
        # For now, we'll apply to all factions with existing relationships
        relationships = await self.tension_service.get_faction_relationships(faction_id)
        
        for relationship in relationships:
            other_faction = (relationship.faction_b_id 
                           if relationship.faction_a_id == faction_id 
                           else relationship.faction_a_id)
            
            await self.tension_service.modify_tension(
                faction_id, other_faction, tension_change, reason
            )
    
    async def _create_diplomatic_incident(self, perpetrator_id: UUID, victim_id: UUID, 
                                        incident_type: str, description: str, 
                                        severity: str = "MODERATE"):
        """Create a diplomatic incident."""
        incident_data = {
            "perpetrator_faction_id": perpetrator_id,
            "victim_faction_id": victim_id,
            "type": incident_type,
            "description": description,
            "severity": severity,
            "location": None,  # Would be filled in by specific handlers
            "evidence": {},
            "witnesses": []
        }
        
        incident = await self.diplomacy_service.create_diplomatic_incident(incident_data)
        
        # Publish incident event
        self.event_bus.publish("diplomatic_incident", {
            "incident_id": str(incident.id),
            "perpetrator_id": str(perpetrator_id),
            "victim_id": str(victim_id) if victim_id else None,
            "type": incident_type,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def _check_combat_treaty_violations(self, aggressor_id: UUID, defender_id: UUID, 
                                            combat_type: str):
        """Check if combat violates any treaties."""
        # Check non-aggression pacts
        treaties = self.diplomacy_service.list_treaties(faction_id=aggressor_id, active_only=True)
        
        for treaty in treaties:
            if (defender_id in treaty.parties and 
                treaty.type in ["NON_AGGRESSION", "PEACE_TREATY"]):
                
                await self.diplomacy_service.report_treaty_violation(
                    treaty_id=treaty.id,
                    violator_faction_id=aggressor_id,
                    violation_type="AGGRESSION",
                    description=f"Initiated combat despite {treaty.type}: {combat_type}",
                    affected_faction_id=defender_id
                )
    
    async def _handle_alliance_obligations(self, aggressor_id: UUID, defender_id: UUID, 
                                         obligation_type: str):
        """Handle alliance obligations when combat occurs."""
        # Get allies of the defender
        defender_allies = await self._get_allied_factions(defender_id)
        
        for ally_id in defender_allies:
            # Check if alliance includes mutual defense
            treaties = self.diplomacy_service.list_treaties(faction_id=ally_id, active_only=True)
            
            for treaty in treaties:
                if (defender_id in treaty.parties and 
                    treaty.type == "MUTUAL_DEFENSE" and
                    "automatic_activation" in treaty.terms):
                    
                    # Ally is now at war with aggressor
                    await self.tension_service.modify_tension(
                        ally_id, aggressor_id, 75, "Alliance obligation - mutual defense"
                    )
                    
                    # Publish alliance activation event
                    self.event_bus.publish("alliance_activated", {
                        "ally_id": str(ally_id),
                        "defender_id": str(defender_id),
                        "aggressor_id": str(aggressor_id),
                        "treaty_id": str(treaty.id),
                        "timestamp": datetime.utcnow().isoformat()
                    })
    
    # Public Integration Methods
    
    async def synchronize_faction_data(self, faction_id: UUID, faction_data: Dict[str, Any]):
        """Synchronize faction data across systems."""
        # Update diplomatic system's understanding of faction capabilities
        # This would typically update faction power ratings, resources, etc.
        pass
    
    async def get_diplomatic_context_for_faction(self, faction_id: UUID) -> Dict[str, Any]:
        """Get comprehensive diplomatic context for a faction."""
        relationships = await self.tension_service.get_faction_relationships(faction_id)
        treaties = self.diplomacy_service.list_treaties(faction_id=faction_id, active_only=True)
        active_negotiations = self.diplomacy_service.get_active_negotiations(faction_id)
        
        return {
            "faction_id": str(faction_id),
            "relationships": [self._serialize_relationship(r) for r in relationships],
            "active_treaties": [self._serialize_treaty(t) for t in treaties],
            "active_negotiations": [self._serialize_negotiation(n) for n in active_negotiations],
            "diplomatic_incidents": await self._get_recent_incidents(faction_id),
            "alliance_obligations": await self._get_alliance_obligations(faction_id)
        }
    
    def _serialize_relationship(self, relationship) -> Dict[str, Any]:
        """Serialize relationship for external consumption."""
        return {
            "other_faction_id": str(relationship.faction_b_id),
            "status": relationship.status,
            "tension_level": relationship.tension_level,
            "trust_level": relationship.trust_level,
            "trade_volume": relationship.trade_volume
        }
    
    def _serialize_treaty(self, treaty) -> Dict[str, Any]:
        """Serialize treaty for external consumption."""
        return {
            "id": str(treaty.id),
            "name": treaty.name,
            "type": treaty.type,
            "parties": [str(p) for p in treaty.parties],
            "status": treaty.status
        }
    
    def _serialize_negotiation(self, negotiation) -> Dict[str, Any]:
        """Serialize negotiation for external consumption."""
        return {
            "id": str(negotiation.id),
            "parties": [str(p) for p in negotiation.parties],
            "treaty_type": negotiation.treaty_type,
            "status": negotiation.status
        }
    
    async def _get_recent_incidents(self, faction_id: UUID) -> List[Dict[str, Any]]:
        """Get recent diplomatic incidents involving a faction."""
        # This would query the database for recent incidents
        return []
    
    async def _get_alliance_obligations(self, faction_id: UUID) -> List[Dict[str, Any]]:
        """Get current alliance obligations for a faction."""
        treaties = self.diplomacy_service.list_treaties(faction_id=faction_id, active_only=True)
        obligations = []
        
        for treaty in treaties:
            if treaty.type in ["ALLIANCE", "MUTUAL_DEFENSE"]:
                obligations.append({
                    "treaty_id": str(treaty.id),
                    "treaty_name": treaty.name,
                    "allies": [str(p) for p in treaty.parties if p != faction_id],
                    "obligations": treaty.terms.get("obligations", [])
                })
        
        return obligations


def create_diplomacy_integration_service() -> DiplomacyIntegrationService:
    """Factory function to create diplomacy integration service."""
    return DiplomacyIntegrationService() 