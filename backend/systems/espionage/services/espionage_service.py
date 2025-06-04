"""
Espionage Business Service

Main service for the Economic Espionage System. Provides business logic,
domain rules, and high-level orchestration for all espionage activities.
This service contains only pure business logic without technical dependencies.
"""

from typing import List, Optional, Dict, Any, Protocol, Tuple
from uuid import UUID
from datetime import datetime

from backend.systems.espionage.models import (
    EspionageOperationType,
    AgentRole,
    IntelligenceType,
    NetworkStatus
)
from backend.infrastructure.config_loaders.espionage_config_loader import get_espionage_config


# Business Logic Protocols (dependency injection)
class EspionageRepository(Protocol):
    """Protocol for espionage data access"""
    
    def get_operation_by_id(self, operation_id: UUID) -> Optional[Dict[str, Any]]:
        """Get operation by ID"""
        ...
    
    def create_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new operation"""
        ...
    
    def update_operation(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing operation"""
        ...
    
    def list_operations(self, 
                       page: int = 1, 
                       size: int = 50, 
                       status: Optional[str] = None,
                       faction_id: Optional[UUID] = None) -> Tuple[List[Dict[str, Any]], int]:
        """List operations with pagination"""
        ...
    
    def get_faction_networks(self, faction_id: UUID) -> List[Dict[str, Any]]:
        """Get spy networks for faction"""
        ...
    
    def get_faction_agents(self, faction_id: UUID) -> List[Dict[str, Any]]:
        """Get agents for faction"""
        ...


class EspionageValidationService(Protocol):
    """Protocol for espionage validation"""
    
    def validate_operation_data(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate operation creation/update data"""
        ...
    
    def validate_agent_assignment(self, agent_data: Dict[str, Any], operation_type: str) -> bool:
        """Validate agent assignment to operation"""
        ...
    
    def validate_security_clearance(self, agent_data: Dict[str, Any], operation_sensitivity: int) -> bool:
        """Validate agent security clearance"""
        ...


class EspionageConfigService(Protocol):
    """Protocol for espionage configuration access"""
    
    def get_calculation_parameter(self, parameter_name: str) -> float:
        """Get calculation parameter from config"""
        ...
    
    def get_operation_success_rate(self, operation_type: str) -> float:
        """Get base success rate for operation type"""
        ...
    
    def get_agent_effectiveness(self, role: str, operation_type: str) -> float:
        """Get agent role effectiveness for operation type"""
        ...
    
    def get_intelligence_rewards(self, operation_type: str) -> List[str]:
        """Get potential intelligence rewards for operation type"""
        ...
    
    def get_operation_damage(self, operation_type: str) -> float:
        """Get base damage for operation type"""
        ...
    
    def get_burn_risk_multiplier(self, operation_type: str) -> float:
        """Get burn risk multiplier for operation type"""
        ...
    
    def get_risk_threshold(self, threshold_type: str) -> float:
        """Get risk threshold value"""
        ...


class EventDispatcher(Protocol):
    """Protocol for event system integration"""
    
    def dispatch_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Dispatch an event to other systems"""
        ...


class EspionageService:
    """Business service for espionage domain logic and orchestration"""

    def __init__(self, 
                 espionage_repository: EspionageRepository,
                 validation_service: EspionageValidationService,
                 config_service: EspionageConfigService,
                 event_dispatcher: EventDispatcher):
        """Initialize with injected dependencies"""
        self.repository = espionage_repository
        self.validation_service = validation_service
        self.config = config_service
        self.event_dispatcher = event_dispatcher

    def calculate_faction_espionage_capabilities(
        self, 
        faction_id: UUID
    ) -> Dict[str, Any]:
        """Calculate a faction's overall espionage capabilities from business data"""
        # Get data via repository
        networks = self.repository.get_faction_networks(faction_id)
        agents = self.repository.get_faction_agents(faction_id)
        
        intelligence_capacity = sum(network.get("intelligence_capacity", 0) for network in networks)
        sabotage_capacity = sum(network.get("sabotage_capacity", 0) for network in networks)
        infiltration_capacity = sum(network.get("infiltration_capacity", 0) for network in networks)
        
        # Agent skill bonus - now configurable
        skill_bonus_multiplier = self.config.get_calculation_parameter("agent_skill_bonus_multiplier")
        agent_skill_bonus = sum(agent.get("skill_level", 1) for agent in agents) * skill_bonus_multiplier
        
        capabilities = {
            "intelligence_capacity": intelligence_capacity + agent_skill_bonus,
            "sabotage_capacity": sabotage_capacity + agent_skill_bonus,
            "infiltration_capacity": infiltration_capacity + agent_skill_bonus,
            "active_networks": len([n for n in networks if n.get("status") == "active"]),
            "active_agents": len([a for a in agents if a.get("status") == "active"]),
            "total_skill_level": sum(agent.get("skill_level", 1) for agent in agents)
        }
        
        # Publish event for capability assessment
        self.event_dispatcher.dispatch_event("espionage_capabilities_assessed", {
            "faction_id": str(faction_id),
            "capabilities": capabilities,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return capabilities

    def assess_espionage_threat_level(
        self, 
        target_faction_id: UUID,
        active_operations: List[Dict[str, Any]], 
        targeting_agents: List[Dict[str, Any]],
        target_defenses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess the espionage threat level against a target using business rules"""
        threat_level = 0.0
        
        # Calculate threat from active operations
        operation_threat = len(active_operations) * 0.1
        
        # Calculate threat from agent quality
        agent_threat = sum(agent.get("skill_level", 1) for agent in targeting_agents) * 0.05
        
        # Adjust for target defenses
        defense_modifier = target_defenses.get("security_level", 1) * 0.1
        
        threat_level = min(1.0, max(0.0, operation_threat + agent_threat - defense_modifier))
        
        # Determine threat sources
        threat_sources = []
        for operation in active_operations:
            initiator_id = operation.get("initiator_id")
            if initiator_id and initiator_id not in threat_sources:
                threat_sources.append(initiator_id)
        
        # Recommend security level based on threat
        recommended_security = max(1, min(10, int(threat_level * 10) + 1))
        
        return {
            "threat_level": threat_level,
            "active_threats": len(active_operations),
            "threat_sources": threat_sources,
            "recommended_security_level": recommended_security
        }

    def calculate_operation_success_chance(
        self,
        operation_type: EspionageOperationType,
        initiator_capabilities: Dict[str, Any],
        target_defenses: Dict[str, Any],
        assigned_agents: List[Dict[str, Any]]
    ) -> float:
        """Calculate the success chance for an espionage operation using business rules"""
        
        # Base success chance from configuration
        base_chance = self.config.get_operation_success_rate(operation_type.value)
        
        # Agent skill modifier - average skill level of assigned agents
        if assigned_agents:
            avg_skill = sum(agent.get("skill_level", 1) for agent in assigned_agents) / len(assigned_agents)
            skill_base = self.config.get_calculation_parameter("skill_modifier_base")
            skill_multiplier = self.config.get_calculation_parameter("skill_modifier_multiplier")
            agent_modifier = (avg_skill - skill_base) * skill_multiplier
            
            # Apply agent role effectiveness
            role_modifier = 0.0
            for agent in assigned_agents:
                role = agent.get("role", "informant")
                effectiveness = self.config.get_agent_effectiveness(role, operation_type.value)
                role_modifier += (effectiveness - 1.0) / len(assigned_agents)
            
            agent_modifier += role_modifier
        else:
            agent_modifier = -0.2  # Penalty for no agents
        
        # Target defense modifier
        target_security = target_defenses.get("security_level", 5)
        security_base = self.config.get_calculation_parameter("security_modifier_base")
        security_multiplier = self.config.get_calculation_parameter("security_modifier_multiplier")
        defense_modifier = (target_security - security_base) * security_multiplier
        
        # Initiator capability modifier
        expertise_multiplier = self.config.get_calculation_parameter("expertise_bonus_multiplier")
        initiator_bonus = initiator_capabilities.get("espionage_expertise", 5) * expertise_multiplier
        
        # Combine all factors
        final_chance = base_chance + agent_modifier - defense_modifier + initiator_bonus
        return max(0.0, min(1.0, final_chance))

    def determine_operation_outcomes(
        self,
        operation_type: EspionageOperationType,
        success_level: float,
        detection_level: float,
        target_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine operation outcomes based on business rules"""
        
        # Intelligence gained based on operation type and success - now from config
        intelligence_gained = []
        success_threshold = self.config.get_calculation_parameter("success_threshold_for_intelligence")
        
        if success_level > success_threshold:
            potential_intel = self.config.get_intelligence_rewards(operation_type.value)
            # More successful operations gain more intelligence
            intel_count = int(success_level * len(potential_intel)) if potential_intel else 0
            intelligence_gained = potential_intel[:intel_count]
        
        # Economic damage calculation - now from config
        max_damage_multiplier = self.config.get_calculation_parameter("max_damage_multiplier")
        damage_multiplier = success_level * max_damage_multiplier
        base_damage = self.config.get_operation_damage(operation_type.value)
        
        damage_dealt = {}
        if base_damage > 0:
            damage_dealt["economic_loss"] = base_damage * damage_multiplier
        
        # Relationship impact based on detection
        relationship_changes = {}
        detection_threshold = self.config.get_risk_threshold("detection_consequence")
        if detection_level > 0.5:  # High detection causes relationship damage
            relationship_changes["trust_loss"] = detection_level * 10
            relationship_changes["reputation_damage"] = detection_level * 5
        
        outcomes = {
            "intelligence_gained": intelligence_gained,
            "damage_dealt": damage_dealt,
            "relationship_changes": relationship_changes,
            "detection_consequences": detection_level > detection_threshold
        }
        
        # Publish event for operation completion
        self.event_dispatcher.dispatch_event("espionage_operation_completed", {
            "operation_type": operation_type.value,
            "success_level": success_level,
            "detection_level": detection_level,
            "outcomes": outcomes,
            "target_data": target_data,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Publish event for intelligence gathered if any
        if intelligence_gained:
            self.event_dispatcher.dispatch_event("intelligence_gathered", {
                "operation_type": operation_type.value,
                "intelligence_types": intelligence_gained,
                "success_level": success_level,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Publish event for economic damage if any
        if damage_dealt:
            self.event_dispatcher.dispatch_event("economic_sabotage_damage", {
                "operation_type": operation_type.value,
                "damage_dealt": damage_dealt,
                "target_data": target_data,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return outcomes

    def calculate_agent_burn_risk(
        self,
        agent_data: Dict[str, Any],
        operation_detection: float,
        operation_type: EspionageOperationType
    ) -> float:
        """Calculate how much an operation increases an agent's burn risk"""
        
        current_burn_risk = agent_data.get("burn_risk", 0.0)
        current_heat = agent_data.get("heat_level", 0)
        
        # Risk multiplier from configuration
        operation_risk = self.config.get_burn_risk_multiplier(operation_type.value)
        
        # Detection and heat bonuses from configuration
        detection_multiplier = self.config.get_calculation_parameter("detection_bonus_multiplier")
        heat_multiplier = self.config.get_calculation_parameter("heat_bonus_multiplier")
        
        detection_bonus = operation_detection * detection_multiplier
        heat_bonus = current_heat * heat_multiplier
        
        new_burn_risk = current_burn_risk + operation_risk + detection_bonus + heat_bonus
        final_burn_risk = min(1.0, new_burn_risk)
        
        # Publish event for agent burn risk increase if significant
        if final_burn_risk > current_burn_risk + 0.1:  # 10% increase threshold
            self.event_dispatcher.dispatch_event("agent_burn_risk_increased", {
                "agent_id": agent_data.get("id"),
                "agent_role": agent_data.get("role"),
                "operation_type": operation_type.value,
                "previous_burn_risk": current_burn_risk,
                "new_burn_risk": final_burn_risk,
                "detection_level": operation_detection,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Publish critical event if agent is approaching retirement threshold
        retirement_threshold = self.config.get_risk_threshold("agent_retirement")
        if final_burn_risk > retirement_threshold:
            self.event_dispatcher.dispatch_event("agent_retirement_required", {
                "agent_id": agent_data.get("id"),
                "agent_role": agent_data.get("role"),
                "burn_risk": final_burn_risk,
                "retirement_threshold": retirement_threshold,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return final_burn_risk

    def get_espionage_statistics_summary(
        self, 
        faction_id: Optional[UUID] = None,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """Get comprehensive espionage statistics summary"""
        # Get operations for the time period
        operations, total = self.repository.list_operations(
            page=1, 
            size=1000, 
            faction_id=faction_id
        )
        
        # Filter by time period if needed
        # This would need additional repository method for date filtering
        
        successful_ops = [op for op in operations if op.get("success", False)]
        failed_ops = [op for op in operations if not op.get("success", False)]
        
        return {
            "total_operations": len(operations),
            "successful_operations": len(successful_ops),
            "failed_operations": len(failed_ops),
            "success_rate": len(successful_ops) / len(operations) if operations else 0.0,
            "average_detection_level": sum(op.get("detection_level", 0) for op in operations) / len(operations) if operations else 0.0,
            "intelligence_gathered": sum(len(op.get("intelligence_gained", [])) for op in successful_ops),
            "operations_by_type": self._group_operations_by_type(operations)
        }

    def validate_agent_assignment(
        self,
        agent_data: Dict[str, Any],
        operation_type: EspionageOperationType,
        operation_difficulty: int
    ) -> Dict[str, Any]:
        """Validate if an agent can be assigned to an operation"""
        validation_result = {
            "valid": True,
            "confidence": 1.0,
            "issues": [],
            "recommendations": []
        }
        
        # Basic validation via service
        if not self.validation_service.validate_agent_assignment(agent_data, operation_type.value):
            validation_result["valid"] = False
            validation_result["issues"].append("Agent fails basic assignment validation")
        
        # Burn risk check
        burn_risk = agent_data.get("burn_risk", 0.0)
        burn_threshold = self.config.get_risk_threshold("operation_restriction")
        
        if burn_risk > burn_threshold:
            validation_result["valid"] = False
            validation_result["issues"].append(f"Agent burn risk too high: {burn_risk:.1%}")
            validation_result["recommendations"].append("Allow agent to cool down or use safer operations")
        
        # Skill vs difficulty check
        agent_skill = agent_data.get("skill_level", 1)
        if operation_difficulty > agent_skill + 2:
            validation_result["confidence"] *= 0.6
            validation_result["issues"].append("Operation difficulty exceeds agent capabilities")
            validation_result["recommendations"].append("Assign additional agents or choose easier target")
        
        # Security clearance check
        operation_sensitivity = self.config.get_calculation_parameter("operation_sensitivity_mapping").get(operation_type.value, 5)
        if not self.validation_service.validate_security_clearance(agent_data, operation_sensitivity):
            validation_result["valid"] = False
            validation_result["issues"].append("Insufficient security clearance")
        
        return validation_result

    def recommend_agents_for_operation(
        self,
        available_agents: List[Dict[str, Any]],
        operation_type: EspionageOperationType,
        operation_difficulty: int,
        max_agents: int = 3
    ) -> List[Dict[str, Any]]:
        """Recommend the best agents for an operation"""
        recommendations = []
        
        for agent in available_agents:
            validation = self.validate_agent_assignment(agent, operation_type, operation_difficulty)
            
            if validation["valid"]:
                # Calculate agent score for this operation
                score = self._calculate_agent_operation_score(agent, operation_type, operation_difficulty)
                
                recommendations.append({
                    "agent": agent,
                    "score": score,
                    "confidence": validation["confidence"],
                    "validation": validation
                })
        
        # Sort by score and take top agents
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:max_agents]

    def _calculate_agent_operation_score(
        self,
        agent: Dict[str, Any],
        operation_type: EspionageOperationType,
        difficulty: int
    ) -> float:
        """Calculate how well an agent fits an operation"""
        base_score = agent.get("skill_level", 1) / 10.0
        
        # Role effectiveness bonus
        role = agent.get("role", "informant")
        role_effectiveness = self.config.get_agent_effectiveness(role, operation_type.value)
        role_bonus = (role_effectiveness - 1.0) * 0.3
        
        # Burn risk penalty
        burn_risk = agent.get("burn_risk", 0.0)
        burn_penalty = burn_risk * 0.4
        
        # Experience bonus
        experience = agent.get("completed_operations", 0)
        experience_bonus = min(0.2, experience * 0.02)
        
        return max(0.0, base_score + role_bonus - burn_penalty + experience_bonus)

    def _group_operations_by_type(self, operations: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group operations by type for statistics"""
        type_counts = {}
        for op in operations:
            op_type = op.get("operation_type", "unknown")
            type_counts[op_type] = type_counts.get(op_type, 0) + 1
        return type_counts


def create_espionage_business_service(
    espionage_repository: EspionageRepository,
    validation_service: EspionageValidationService,
    config_service: EspionageConfigService,
    event_dispatcher: EventDispatcher
) -> EspionageService:
    """Factory function to create espionage business service"""
    return EspionageService(espionage_repository, validation_service, config_service, event_dispatcher) 