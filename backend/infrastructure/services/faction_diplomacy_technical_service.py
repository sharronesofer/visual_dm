"""
Faction Diplomacy Technical Service - Infrastructure

Technical service for faction diplomacy integration that handles:
- Configuration loading
- External service calls
- Async operations
- Logging

Extracted from backend/systems/faction/services/diplomacy_integration_service.py
"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Protocol
from uuid import UUID
from datetime import datetime, timedelta

from backend.infrastructure.config_loaders.faction_config_loader import get_faction_config
from backend.infrastructure.logging_setup.faction_logging import diplomacy_logger


class DiplomacyServiceProvider(Protocol):
    """Protocol for external diplomacy service"""
    
    def get_faction_relationship(self, faction_a_id: UUID, faction_b_id: UUID) -> Dict[str, Any]:
        """Get relationship data between factions"""
        ...
    
    def propose_treaty(self, proposer_id: UUID, target_id: UUID, terms: Dict[str, Any]) -> Dict[str, Any]:
        """Propose a treaty between factions"""
        ...


class FactionDataProvider(Protocol):
    """Protocol for faction data access"""
    
    def get_faction_by_id(self, faction_id: UUID) -> Optional[Any]:
        """Get faction data by ID"""
        ...


class FactionDiplomacyTechnicalService:
    """Technical service for faction diplomacy integration"""
    
    def __init__(self, 
                 faction_data_provider: FactionDataProvider,
                 diplomacy_service: DiplomacyServiceProvider):
        self.faction_data_provider = faction_data_provider
        self.diplomacy_service = diplomacy_service
        self.config = None
        self._load_configuration()
        diplomacy_logger.info("Initialized FactionDiplomacyTechnicalService")
    
    def _load_configuration(self):
        """Load faction configuration from infrastructure"""
        try:
            self.config = get_faction_config()
            diplomacy_logger.info("Faction configuration loaded successfully")
        except Exception as e:
            diplomacy_logger.error(f"Failed to load faction configuration: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Provide default configuration if loading fails"""
        return {
            "alliance_types": {
                "military": {
                    "name": "Military Alliance",
                    "description": "Military cooperation and defense pact",
                    "trust_requirements": 50,
                    "duration_modifier": 1.0
                },
                "economic": {
                    "name": "Economic Alliance", 
                    "description": "Trade and economic cooperation",
                    "trust_requirements": 40,
                    "duration_modifier": 1.2
                }
            },
            "compatibility_factors": {
                "military": {
                    "ambition_weight": 0.3,
                    "discipline_weight": 0.4,
                    "integrity_weight": 0.3
                },
                "economic": {
                    "pragmatism_weight": 0.4,
                    "integrity_weight": 0.3,
                    "discipline_weight": 0.3
                }
            }
        }
    
    async def evaluate_alliance_proposal(
        self, 
        proposer_id: UUID, 
        target_id: UUID, 
        alliance_type: str = "military"
    ) -> Dict[str, Any]:
        """
        Technical evaluation of alliance proposal with external service calls
        """
        try:
            # Get faction data through provider
            proposer = await self._get_faction_async(proposer_id)
            target = await self._get_faction_async(target_id)
            
            if not proposer or not target:
                return {"error": "One or both factions not found"}
            
            # Get alliance configuration
            alliance_config = self.config.get("alliance_types", {}).get(alliance_type, {})
            if not alliance_config:
                return {"error": f"Unknown alliance type: {alliance_type}"}
            
            # Get current diplomatic relationship through external service
            relationship = await self._get_diplomatic_relationship_async(proposer_id, target_id)
            current_tension = relationship.get('tension', 50)
            
            # Calculate compatibility using configuration
            compatibility = self._calculate_alliance_compatibility(
                proposer, target, alliance_type
            )
            
            # Calculate acceptance probability using business rules
            acceptance_probability = self._calculate_acceptance_probability(
                compatibility, current_tension, target, alliance_config
            )
            
            return {
                "acceptance_probability": round(acceptance_probability, 3),
                "compatibility_score": round(compatibility, 3),
                "current_tension": current_tension,
                "alliance_type": alliance_type,
                "trust_required": alliance_config.get('trust_requirements', 50),
                "reasoning": {
                    "compatibility": f"Faction compatibility: {compatibility:.2f}",
                    "tension": f"Current tension level: {current_tension}",
                    "recommendation": "Accept" if acceptance_probability > 0.6 else "Reject" if acceptance_probability < 0.4 else "Consider"
                }
            }
            
        except Exception as e:
            diplomacy_logger.error(f"Error evaluating alliance proposal: {e}")
            return {"error": f"Evaluation failed: {str(e)}"}
    
    async def propose_alliance(
        self, 
        proposer_id: UUID, 
        target_id: UUID, 
        alliance_type: str = "military",
        custom_terms: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Technical alliance proposal with external service integration
        """
        try:
            # First evaluate if the proposal makes sense
            evaluation = await self.evaluate_alliance_proposal(proposer_id, target_id, alliance_type)
            
            if "error" in evaluation:
                return evaluation
            
            # Get alliance configuration
            alliance_config = self.config.get("alliance_types", {}).get(alliance_type, {})
            
            # Create treaty type mapping
            treaty_type_map = {
                "military": "DEFENSIVE_PACT",
                "economic": "TRADE_AGREEMENT", 
                "temporary_truce": "CEASEFIRE",
                "mutual_defense": "MUTUAL_DEFENSE_PACT"
            }
            
            treaty_type = treaty_type_map.get(alliance_type, "DIPLOMATIC_PACT")
            
            # Prepare terms
            terms = {
                "alliance_type": alliance_type,
                "alliance_name": alliance_config.get('name', f'{alliance_type.title()} Alliance'),
                "description": alliance_config.get('description', ''),
                "duration_modifier": alliance_config.get('duration_modifier', 1.0),
                "trust_requirements": alliance_config.get('trust_requirements', 50),
                "compatibility_score": evaluation.get('compatibility_score'),
                "evaluation": evaluation,
                "treaty_type": treaty_type
            }
            
            if custom_terms:
                terms.update(custom_terms)
            
            # Start negotiation through external diplomacy service
            result = await self._propose_treaty_async(proposer_id, target_id, terms)
            
            diplomacy_logger.info(f"Alliance proposal sent from {proposer_id} to {target_id}: {alliance_type}")
            
            return result
            
        except Exception as e:
            diplomacy_logger.error(f"Error proposing alliance: {e}")
            return {"error": f"Proposal failed: {str(e)}"}
    
    async def calculate_betrayal_risk(
        self, 
        faction_id: UUID, 
        ally_id: UUID, 
        scenario: str = "opportunity"
    ) -> Dict[str, Any]:
        """
        Technical calculation of betrayal risk with data access
        """
        try:
            faction = await self._get_faction_async(faction_id)
            ally = await self._get_faction_async(ally_id)
            
            if not faction or not ally:
                return {"error": "One or both factions not found"}
            
            # Get relationship data
            relationship = await self._get_diplomatic_relationship_async(faction_id, ally_id)
            
            # Calculate betrayal risk using faction attributes and relationship
            hidden_attrs = faction.get_hidden_attributes() if hasattr(faction, 'get_hidden_attributes') else {}
            
            # Base betrayal calculation
            base_risk = self._calculate_base_betrayal_risk(hidden_attrs, relationship, scenario)
            
            return {
                "betrayal_risk": round(base_risk, 3),
                "risk_level": self._categorize_risk(base_risk),
                "scenario": scenario,
                "relationship_tension": relationship.get('tension', 50),
                "faction_attributes": hidden_attrs
            }
            
        except Exception as e:
            diplomacy_logger.error(f"Error calculating betrayal risk: {e}")
            return {"error": f"Calculation failed: {str(e)}"}
    
    async def get_faction_diplomatic_status(self, faction_id: UUID) -> Dict[str, Any]:
        """
        Get comprehensive diplomatic status for a faction
        """
        try:
            faction = await self._get_faction_async(faction_id)
            
            if not faction:
                return {"error": "Faction not found"}
            
            # This would integrate with multiple external services
            # For now, return basic status structure
            
            return {
                "faction_id": faction_id,
                "faction_name": getattr(faction, 'name', 'Unknown'),
                "diplomatic_stance": "neutral",  # Would be calculated from relationships
                "active_treaties": [],  # Would be fetched from diplomacy service
                "pending_negotiations": [],  # Would be fetched from diplomacy service
                "relationship_summary": {}  # Would be built from multiple relationships
            }
            
        except Exception as e:
            diplomacy_logger.error(f"Error getting diplomatic status: {e}")
            return {"error": f"Status retrieval failed: {str(e)}"}
    
    # Technical helper methods
    
    async def _get_faction_async(self, faction_id: UUID):
        """Async wrapper for faction data access"""
        # In a real implementation, this might involve database calls
        return self.faction_data_provider.get_faction_by_id(faction_id)
    
    async def _get_diplomatic_relationship_async(self, faction_a_id: UUID, faction_b_id: UUID) -> Dict[str, Any]:
        """Async wrapper for diplomatic relationship access"""
        try:
            return self.diplomacy_service.get_faction_relationship(faction_a_id, faction_b_id)
        except Exception as e:
            diplomacy_logger.warning(f"Failed to get relationship for {faction_a_id}-{faction_b_id}: {e}")
            return {"tension": 50}  # Default neutral tension
    
    async def _propose_treaty_async(self, proposer_id: UUID, target_id: UUID, terms: Dict[str, Any]) -> Dict[str, Any]:
        """Async wrapper for treaty proposal"""
        try:
            return self.diplomacy_service.propose_treaty(proposer_id, target_id, terms)
        except Exception as e:
            diplomacy_logger.error(f"Failed to propose treaty: {e}")
            return {"error": f"Treaty proposal failed: {str(e)}"}
    
    def _calculate_alliance_compatibility(self, faction_a: Any, faction_b: Any, alliance_type: str) -> float:
        """Calculate alliance compatibility using configuration"""
        factors = self.config.get("compatibility_factors", {}).get(alliance_type, {})
        if not factors:
            return 0.5  # Default neutral compatibility
        
        attrs_a = faction_a.get_hidden_attributes() if hasattr(faction_a, 'get_hidden_attributes') else {}
        attrs_b = faction_b.get_hidden_attributes() if hasattr(faction_b, 'get_hidden_attributes') else {}
        
        total_compatibility = 0.0
        total_weight = 0.0
        
        for factor, weight in factors.items():
            attr_name = factor.replace('_weight', '')
            full_attr_name = f"hidden_{attr_name}"
            
            if full_attr_name in attrs_a and full_attr_name in attrs_b:
                diff = abs(attrs_a[full_attr_name] - attrs_b[full_attr_name])
                attr_compatibility = 1.0 - (diff / 10.0)  # Assuming 0-10 scale
                
                total_compatibility += attr_compatibility * weight
                total_weight += weight
        
        return total_compatibility / total_weight if total_weight > 0 else 0.5
    
    def _calculate_acceptance_probability(self, compatibility: float, tension: int, target_faction: Any, alliance_config: Dict) -> float:
        """Calculate acceptance probability using business rules"""
        # Base acceptance probability
        base_acceptance = 0.5
        
        # Modify based on compatibility
        compatibility_modifier = (compatibility - 0.5) * 0.6
        
        # Modify based on tension (lower tension = higher acceptance)
        tension_modifier = (50 - tension) / 100.0
        
        # Modify based on target faction reliability
        target_attrs = target_faction.get_hidden_attributes() if hasattr(target_faction, 'get_hidden_attributes') else {}
        reliability = target_attrs.get('hidden_integrity', 5) / 10.0  # Normalize to 0-1
        reliability_modifier = (reliability - 0.5) * 0.4
        
        # Calculate final acceptance probability
        acceptance_probability = base_acceptance + compatibility_modifier + tension_modifier + reliability_modifier
        return max(0.0, min(1.0, acceptance_probability))
    
    def _calculate_base_betrayal_risk(self, hidden_attrs: Dict[str, int], relationship: Dict[str, Any], scenario: str) -> float:
        """Calculate base betrayal risk"""
        # Simple betrayal calculation
        ambition = hidden_attrs.get('hidden_ambition', 5)
        integrity = hidden_attrs.get('hidden_integrity', 5)
        tension = relationship.get('tension', 50)
        
        # High ambition + low integrity + high tension = higher betrayal risk
        risk = ((ambition / 10.0) + ((10 - integrity) / 10.0) + (tension / 100.0)) / 3.0
        
        # Scenario modifiers
        if scenario == "opportunity":
            risk *= 1.2
        elif scenario == "desperation":
            risk *= 1.5
        
        return min(1.0, risk)
    
    def _categorize_risk(self, risk: float) -> str:
        """Categorize risk level"""
        if risk < 0.2:
            return "very_low"
        elif risk < 0.4:
            return "low" 
        elif risk < 0.6:
            return "moderate"
        elif risk < 0.8:
            return "high"
        else:
            return "very_high"


def create_faction_diplomacy_technical_service(
    faction_data_provider: FactionDataProvider,
    diplomacy_service: DiplomacyServiceProvider
) -> FactionDiplomacyTechnicalService:
    """Factory function to create faction diplomacy technical service"""
    return FactionDiplomacyTechnicalService(faction_data_provider, diplomacy_service) 