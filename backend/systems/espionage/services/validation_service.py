"""
Espionage Validation Service

Specialized service for validating business rules and ensuring data integrity
within the espionage system. Handles complex validation scenarios beyond
basic Pydantic validation.
"""

from typing import List, Dict, Any, Set, Optional
from uuid import UUID
from datetime import datetime

from backend.systems.espionage.models import (
    EspionageOperationType,
    AgentRole,
    EspionageOperationStatus,
    NetworkStatus
)
from backend.infrastructure.config_loaders.espionage_config_loader import get_espionage_config


class EspionageValidationService:
    """Service for validating complex business rules in the espionage system"""

    def __init__(self):
        """Initialize the validation service"""
        self.config = get_espionage_config()

    def validate_operation_business_rules(
        self,
        operation_data: Dict[str, Any],
        agents: List[Dict[str, Any]],
        initiator_data: Dict[str, Any],
        target_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate all business rules for an espionage operation"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Validate operation timing
        timing_validation = self._validate_operation_timing(operation_data)
        validation_result = self._merge_validation_results(validation_result, timing_validation)
        
        # Validate agent assignments
        agent_validation = self._validate_agent_assignments(
            operation_data, agents, initiator_data
        )
        validation_result = self._merge_validation_results(validation_result, agent_validation)
        
        # Validate faction relationships
        faction_validation = self._validate_faction_relationships(
            initiator_data, target_data, operation_data
        )
        validation_result = self._merge_validation_results(validation_result, faction_validation)
        
        # Validate resource requirements
        resource_validation = self._validate_resource_requirements(
            operation_data, initiator_data
        )
        validation_result = self._merge_validation_results(validation_result, resource_validation)
        
        # Validate operational security
        opsec_validation = self._validate_operational_security(
            operation_data, agents, target_data
        )
        validation_result = self._merge_validation_results(validation_result, opsec_validation)
        
        return validation_result

    def validate_agent_status_consistency(
        self,
        agent_data: Dict[str, Any],
        recent_operations: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate that agent status fields are consistent with each other"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        status = agent_data.get("status", "active")
        burn_risk = agent_data.get("burn_risk", 0.0)
        heat_level = agent_data.get("heat_level", 0)
        
        # Check status vs burn risk consistency
        retirement_threshold = self.config.get_risk_threshold("agent_retirement")
        restriction_threshold = self.config.get_risk_threshold("operation_restriction")
        
        if status == "active" and burn_risk > retirement_threshold:
            validation_result["errors"].append(
                f"Agent has 'active' status but burn risk ({burn_risk:.2f}) exceeds retirement threshold ({retirement_threshold})"
            )
            validation_result["valid"] = False
        
        if status == "active" and burn_risk > restriction_threshold:
            validation_result["warnings"].append(
                f"Agent has 'active' status but burn risk ({burn_risk:.2f}) suggests restricted operations only"
            )
        
        # Check heat level consistency
        if heat_level > 8 and status == "active":
            validation_result["warnings"].append(
                f"Agent has high heat level ({heat_level}) but is still active - consider cooling off period"
            )
        
        # Validate against recent operation activity
        if recent_operations:
            last_operation_time = max(
                (op.get("completion_time", 0) for op in recent_operations),
                default=0
            )
            
            if last_operation_time:
                hours_since_last_op = (datetime.utcnow().timestamp() - last_operation_time) / 3600
                
                if heat_level > 5 and hours_since_last_op < 48:
                    validation_result["warnings"].append(
                        f"Agent has high heat ({heat_level}) with recent operation activity - consider rest period"
                    )
        
        return validation_result

    def validate_network_agent_relationships(
        self,
        networks: List[Dict[str, Any]],
        agents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate consistency between spy networks and their agents"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Track agents claimed by networks vs actual agent network assignments
        network_claimed_agents = {}
        agent_network_assignments = {}
        
        # Collect network claims
        for network in networks:
            network_id = network.get("id")
            agent_count = network.get("agent_count", 0)
            network_claimed_agents[network_id] = agent_count
        
        # Collect agent assignments
        for agent in agents:
            network_id = agent.get("network_id")
            if network_id:
                if network_id not in agent_network_assignments:
                    agent_network_assignments[network_id] = 0
                agent_network_assignments[network_id] += 1
        
        # Compare claimed vs actual counts
        for network_id, claimed_count in network_claimed_agents.items():
            actual_count = agent_network_assignments.get(network_id, 0)
            
            if claimed_count != actual_count:
                validation_result["errors"].append(
                    f"Network {network_id} claims {claimed_count} agents but actually has {actual_count}"
                )
                validation_result["valid"] = False
        
        # Check for orphaned agents
        for network_id, actual_count in agent_network_assignments.items():
            if network_id not in network_claimed_agents:
                validation_result["errors"].append(
                    f"Agents assigned to non-existent network {network_id}"
                )
                validation_result["valid"] = False
        
        return validation_result

    def validate_operation_overlaps(
        self,
        pending_operations: List[Dict[str, Any]],
        agents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate that agents aren't double-booked for operations"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Track agent assignments across operations
        agent_assignments = {}
        
        for operation in pending_operations:
            operation_id = operation.get("id")
            assigned_agent_ids = operation.get("assigned_agent_ids", [])
            planned_start = operation.get("planned_start_time")
            estimated_duration = operation.get("estimated_duration_hours", 24)
            
            if not planned_start:
                continue
                
            planned_end = planned_start + (estimated_duration * 3600)  # Convert to seconds
            
            for agent_id in assigned_agent_ids:
                if agent_id not in agent_assignments:
                    agent_assignments[agent_id] = []
                
                # Check for overlaps with existing assignments
                for existing_assignment in agent_assignments[agent_id]:
                    existing_start = existing_assignment["start"]
                    existing_end = existing_assignment["end"]
                    
                    # Check for time overlap
                    if (planned_start < existing_end and planned_end > existing_start):
                        validation_result["errors"].append(
                            f"Agent {agent_id} assigned to overlapping operations {operation_id} and {existing_assignment['operation_id']}"
                        )
                        validation_result["valid"] = False
                
                agent_assignments[agent_id].append({
                    "operation_id": operation_id,
                    "start": planned_start,
                    "end": planned_end
                })
        
        return validation_result

    def validate_faction_espionage_ethics(
        self,
        initiator_faction: Dict[str, Any],
        target_faction: Dict[str, Any],
        operation_type: EspionageOperationType
    ) -> Dict[str, Any]:
        """Validate that espionage operations align with faction ethics and relationships"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Check faction relationship status
        relationship_status = initiator_faction.get("relationships", {}).get(
            target_faction.get("id"), "neutral"
        )
        
        # Check if factions are allied
        if relationship_status == "allied":
            # Friendly espionage might be acceptable for some operation types
            acceptable_allied_ops = [
                EspionageOperationType.COUNTER_ESPIONAGE,
                EspionageOperationType.PRICE_INTELLIGENCE  # Market research
            ]
            
            if operation_type not in acceptable_allied_ops:
                validation_result["errors"].append(
                    f"Operation type {operation_type.value} not appropriate against allied faction"
                )
                validation_result["valid"] = False
        
        # Check faction ethics constraints
        initiator_ethics = initiator_faction.get("ethics", {})
        
        # Pacifist factions shouldn't do sabotage
        if initiator_ethics.get("pacifist", False):
            sabotage_ops = [
                EspionageOperationType.FACILITY_SABOTAGE,
                EspionageOperationType.SHIPMENT_SABOTAGE,
                EspionageOperationType.REPUTATION_SABOTAGE
            ]
            
            if operation_type in sabotage_ops:
                validation_result["errors"].append(
                    f"Pacifist faction cannot perform sabotage operation {operation_type.value}"
                )
                validation_result["valid"] = False
        
        # Honorable factions shouldn't do certain operations
        if initiator_ethics.get("honorable", False):
            dishonorable_ops = [
                EspionageOperationType.REPUTATION_SABOTAGE,
                EspionageOperationType.MARKET_MANIPULATION
            ]
            
            if operation_type in dishonorable_ops:
                validation_result["warnings"].append(
                    f"Operation {operation_type.value} conflicts with faction honor code"
                )
        
        return validation_result

    def _validate_operation_timing(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate operation timing constraints"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        planned_start = operation_data.get("planned_start_time")
        actual_start = operation_data.get("actual_start_time")
        status = operation_data.get("status")
        
        # Validate start time logic
        if actual_start and not planned_start:
            validation_result["errors"].append("Operation has actual start time but no planned start time")
            validation_result["valid"] = False
        
        if actual_start and planned_start and actual_start < planned_start:
            validation_result["warnings"].append("Operation started before planned time")
        
        # Validate status consistency with timing
        current_time = datetime.utcnow().timestamp()
        
        if status == "in_progress" and not actual_start:
            validation_result["errors"].append("Operation marked in progress but has no actual start time")
            validation_result["valid"] = False
        
        if status == "pending" and actual_start:
            validation_result["errors"].append("Operation marked pending but already has start time")
            validation_result["valid"] = False
        
        if planned_start and planned_start < current_time and status == "pending":
            validation_result["warnings"].append("Operation past planned start time but still pending")
        
        return validation_result

    def _validate_agent_assignments(
        self,
        operation_data: Dict[str, Any],
        agents: List[Dict[str, Any]],
        initiator_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate agent assignment business rules"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        operation_type = EspionageOperationType(operation_data.get("operation_type"))
        assigned_agent_ids = operation_data.get("assigned_agent_ids", [])
        
        # Validate each assigned agent
        for agent_id in assigned_agent_ids:
            agent = next((a for a in agents if a.get("id") == agent_id), None)
            if not agent:
                validation_result["errors"].append(f"Assigned agent {agent_id} not found")
                validation_result["valid"] = False
                continue
            
            # Check if agent belongs to initiating faction
            agent_faction_id = agent.get("faction_id")
            initiator_faction_id = initiator_data.get("faction_id")
            
            if agent_faction_id != initiator_faction_id:
                validation_result["errors"].append(
                    f"Agent {agent_id} belongs to different faction than operation initiator"
                )
                validation_result["valid"] = False
            
            # Use agent service for detailed validation
            from backend.systems.espionage.services.agent_service import EspionageAgentService
            agent_service = EspionageAgentService()
            
            agent_validation = agent_service.validate_agent_assignment(
                agent, operation_type, operation_data.get("difficulty", 5)
            )
            
            if not agent_validation["can_assign"]:
                validation_result["errors"].extend(agent_validation["blocking_issues"])
                validation_result["valid"] = False
            
            validation_result["warnings"].extend(agent_validation["warnings"])
        
        return validation_result

    def _validate_faction_relationships(
        self,
        initiator_data: Dict[str, Any],
        target_data: Dict[str, Any],
        operation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate faction relationship constraints"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        initiator_id = initiator_data.get("faction_id") or initiator_data.get("id")
        target_id = target_data.get("faction_id") or target_data.get("id")
        
        # Can't spy on yourself
        if initiator_id == target_id:
            validation_result["errors"].append("Cannot conduct espionage operations against own faction")
            validation_result["valid"] = False
        
        # Check specific faction ethics
        operation_type = EspionageOperationType(operation_data.get("operation_type"))
        faction_validation = self.validate_faction_espionage_ethics(
            initiator_data, target_data, operation_type
        )
        
        validation_result = self._merge_validation_results(validation_result, faction_validation)
        
        return validation_result

    def _validate_resource_requirements(
        self,
        operation_data: Dict[str, Any],
        initiator_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that initiator has required resources for operation"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Calculate resource requirements
        from backend.systems.espionage.services.operation_service import EspionageOperationService
        operation_service = EspionageOperationService()
        
        operation_type = EspionageOperationType(operation_data.get("operation_type"))
        difficulty = operation_data.get("difficulty", 5)
        
        requirements = operation_service._calculate_resource_requirements(operation_type, difficulty)
        
        # Check funding
        required_funding = requirements["funding_required"]
        available_funding = initiator_data.get("available_funding", 0)
        
        if available_funding < required_funding:
            validation_result["errors"].append(
                f"Insufficient funding: need {required_funding}, have {available_funding}"
            )
            validation_result["valid"] = False
        
        # Check equipment level
        required_equipment = requirements["equipment_level"]
        available_equipment = initiator_data.get("equipment_level", 1)
        
        if available_equipment < required_equipment:
            validation_result["warnings"].append(
                f"Equipment level may be insufficient: need level {required_equipment}, have {available_equipment}"
            )
        
        return validation_result

    def _validate_operational_security(
        self,
        operation_data: Dict[str, Any],
        agents: List[Dict[str, Any]],
        target_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate operational security considerations"""
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Check cumulative agent burn risk
        total_burn_risk = sum(agent.get("burn_risk", 0.0) for agent in agents)
        avg_burn_risk = total_burn_risk / len(agents) if agents else 0.0
        
        if avg_burn_risk > 0.6:
            validation_result["warnings"].append(
                f"High average agent burn risk ({avg_burn_risk:.2f}) - operation may be compromised"
            )
        
        # Check target security vs agent capabilities
        target_security = target_data.get("security_level", 5)
        max_agent_skill = max((agent.get("skill_level", 1) for agent in agents), default=1)
        
        if target_security > max_agent_skill + 2:
            validation_result["warnings"].append(
                f"Target security ({target_security}) significantly exceeds agent capabilities ({max_agent_skill})"
            )
            validation_result["recommendations"].append("Consider recruiting higher-skilled agents or choosing different target")
        
        return validation_result

    def _merge_validation_results(
        self,
        result1: Dict[str, Any],
        result2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge two validation results"""
        
        merged = {
            "valid": result1["valid"] and result2["valid"],
            "errors": result1["errors"] + result2["errors"],
            "warnings": result1["warnings"] + result2["warnings"],
            "recommendations": result1["recommendations"] + result2["recommendations"]
        }
        
        return merged 