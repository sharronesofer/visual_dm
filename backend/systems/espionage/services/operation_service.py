"""
Espionage Operation Service

Specialized service for managing espionage operations including planning,
execution, and outcome determination. Handles the lifecycle of espionage
operations from conception to completion.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta

from backend.systems.espionage.models import (
    EspionageOperationType,
    EspionageOperationStatus,
    EspionageOperation
)
from backend.infrastructure.config_loaders.espionage_config_loader import get_espionage_config


class EspionageOperationService:
    """Service for managing espionage operations"""

    def __init__(self):
        """Initialize the operation service"""
        self.config = get_espionage_config()

    def plan_operation(
        self,
        operation_type: EspionageOperationType,
        initiator_id: UUID,
        initiator_type: str,
        target_id: UUID,
        target_type: str,
        initiator_capabilities: Dict[str, Any],
        target_defenses: Dict[str, Any],
        available_agents: List[Dict[str, Any]],
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Plan a new espionage operation with recommendations"""
        
        # Calculate difficulty based on operation type and target
        difficulty = self._calculate_operation_difficulty(
            operation_type, target_defenses, additional_params or {}
        )
        
        # Recommend agents for this operation
        from backend.systems.espionage.services.agent_service import EspionageAgentService
        agent_service = EspionageAgentService()
        
        recommended_agents = agent_service.recommend_agents_for_operation(
            available_agents, operation_type, difficulty
        )
        
        # Calculate expected success chance
        agent_data = [rec["agent"] for rec in recommended_agents]
        success_chance = self._calculate_success_chance(
            operation_type, initiator_capabilities, target_defenses, agent_data
        )
        
        # Estimate risks
        risk_assessment = self._assess_operation_risks(
            operation_type, target_defenses, agent_data
        )
        
        # Determine expected timeline
        timeline = self._estimate_operation_timeline(operation_type, difficulty)
        
        return {
            "operation_type": operation_type.value,
            "difficulty": difficulty,
            "success_chance": success_chance,
            "recommended_agents": recommended_agents,
            "risk_assessment": risk_assessment,
            "timeline": timeline,
            "resource_requirements": self._calculate_resource_requirements(
                operation_type, difficulty
            )
        }

    def execute_operation(
        self,
        operation_data: Dict[str, Any],
        assigned_agents: List[Dict[str, Any]],
        environmental_factors: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute an espionage operation and determine outcomes"""
        
        operation_type = EspionageOperationType(operation_data["operation_type"])
        initiator_capabilities = operation_data.get("initiator_capabilities", {})
        target_defenses = operation_data.get("target_defenses", {})
        
        # Calculate final success chance with environmental factors
        base_success = self._calculate_success_chance(
            operation_type, initiator_capabilities, target_defenses, assigned_agents
        )
        
        # Apply environmental modifiers
        environmental_modifier = self._apply_environmental_factors(
            environmental_factors or {}
        )
        final_success_chance = max(0.0, min(1.0, base_success + environmental_modifier))
        
        # Determine if operation succeeds
        import random
        success_roll = random.random()
        operation_succeeded = success_roll <= final_success_chance
        
        # Calculate success level (partial success possible)
        if operation_succeeded:
            success_level = min(1.0, success_roll + 0.3)  # Boost for successful ops
        else:
            success_level = success_roll * 0.7  # Partial results even on failure
        
        # Calculate detection level
        detection_level = self._calculate_detection_level(
            operation_type, target_defenses, assigned_agents, success_level
        )
        
        # Determine operation outcomes
        outcomes = self._determine_operation_outcomes(
            operation_type, success_level, detection_level, operation_data.get("target_data", {})
        )
        
        # Update agent burn risk
        agent_updates = []
        for agent in assigned_agents:
            new_burn_risk = self._calculate_agent_burn_risk(
                agent, detection_level, operation_type
            )
            agent_updates.append({
                "agent_id": agent.get("id"),
                "new_burn_risk": new_burn_risk,
                "heat_increase": self._calculate_heat_increase(operation_type, detection_level)
            })
        
        return {
            "success": operation_succeeded,
            "success_level": success_level,
            "detection_level": detection_level,
            "outcomes": outcomes,
            "agent_updates": agent_updates,
            "completion_time": datetime.utcnow(),
            "final_success_chance": final_success_chance
        }

    def validate_operation_feasibility(
        self,
        operation_type: EspionageOperationType,
        initiator_capabilities: Dict[str, Any],
        target_defenses: Dict[str, Any],
        available_agents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate if an operation is feasible with current resources"""
        
        validation_result = {
            "feasible": True,
            "confidence": 1.0,
            "issues": [],
            "recommendations": []
        }
        
        # Check if we have suitable agents
        suitable_agents = []
        for agent in available_agents:
            if agent.get("status") == "active":
                burn_risk = agent.get("burn_risk", 0.0)
                if burn_risk < self.config.get_risk_threshold("operation_restriction"):
                    suitable_agents.append(agent)
        
        if not suitable_agents:
            validation_result["feasible"] = False
            validation_result["issues"].append("No suitable agents available")
        
        # Check success probability
        success_chance = self._calculate_success_chance(
            operation_type, initiator_capabilities, target_defenses, suitable_agents[:3]
        )
        
        if success_chance < 0.2:
            validation_result["confidence"] *= 0.5
            validation_result["issues"].append(f"Low success probability: {success_chance:.1%}")
            validation_result["recommendations"].append("Consider improving agent skills or waiting for better opportunity")
        
        # Check target security level
        target_security = target_defenses.get("security_level", 5)
        max_agent_skill = max((agent.get("skill_level", 1) for agent in suitable_agents), default=1)
        
        if target_security > max_agent_skill + 3:
            validation_result["confidence"] *= 0.7
            validation_result["issues"].append("Target security significantly exceeds agent capabilities")
            validation_result["recommendations"].append("Recruit higher-skilled agents or choose easier target")
        
        return validation_result

    def _calculate_operation_difficulty(
        self,
        operation_type: EspionageOperationType,
        target_defenses: Dict[str, Any],
        additional_params: Dict[str, Any]
    ) -> int:
        """Calculate operation difficulty on a scale of 1-10"""
        
        # Base difficulty by operation type
        base_difficulties = {
            EspionageOperationType.PRICE_INTELLIGENCE: 3,
            EspionageOperationType.ROUTE_SURVEILLANCE: 4,
            EspionageOperationType.SUPPLIER_INTELLIGENCE: 5,
            EspionageOperationType.TRADE_SECRET_THEFT: 6,
            EspionageOperationType.AGENT_RECRUITMENT: 6,
            EspionageOperationType.SHIPMENT_SABOTAGE: 7,
            EspionageOperationType.COUNTER_ESPIONAGE: 7,
            EspionageOperationType.REPUTATION_SABOTAGE: 8,
            EspionageOperationType.FACILITY_SABOTAGE: 8,
            EspionageOperationType.MARKET_MANIPULATION: 9,
            EspionageOperationType.NETWORK_INFILTRATION: 10
        }
        
        base_difficulty = base_difficulties.get(operation_type, 5)
        
        # Adjust for target security
        target_security = target_defenses.get("security_level", 5)
        security_modifier = (target_security - 5) * 0.5
        
        # Adjust for additional factors
        time_pressure = additional_params.get("time_pressure", 1.0)
        complexity_modifier = additional_params.get("complexity_modifier", 0)
        
        final_difficulty = base_difficulty + security_modifier + complexity_modifier
        if time_pressure > 1.5:  # Rush jobs are harder
            final_difficulty += 1
        
        return max(1, min(10, int(final_difficulty)))

    def _calculate_success_chance(
        self,
        operation_type: EspionageOperationType,
        initiator_capabilities: Dict[str, Any],
        target_defenses: Dict[str, Any],
        assigned_agents: List[Dict[str, Any]]
    ) -> float:
        """Calculate success chance using the main espionage service"""
        from backend.systems.espionage.services.espionage_service import EspionageService
        
        main_service = EspionageService()
        return main_service.calculate_operation_success_chance(
            operation_type, initiator_capabilities, target_defenses, assigned_agents
        )

    def _assess_operation_risks(
        self,
        operation_type: EspionageOperationType,
        target_defenses: Dict[str, Any],
        assigned_agents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess risks associated with an operation"""
        
        # Base risk by operation type
        base_risk = self.config.get_burn_risk_multiplier(operation_type.value)
        
        # Agent risk accumulation
        total_agent_risk = sum(agent.get("burn_risk", 0.0) for agent in assigned_agents)
        avg_agent_risk = total_agent_risk / len(assigned_agents) if assigned_agents else 0.0
        
        # Target security risk
        target_security = target_defenses.get("security_level", 5)
        security_risk = target_security / 10.0
        
        return {
            "operation_risk": base_risk,
            "agent_exposure_risk": avg_agent_risk,
            "target_security_risk": security_risk,
            "overall_risk": (base_risk + avg_agent_risk + security_risk) / 3.0,
            "risk_level": self._categorize_risk_level(base_risk + avg_agent_risk + security_risk)
        }

    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize risk level for human-readable assessment"""
        if risk_score < 0.3:
            return "Low"
        elif risk_score < 0.6:
            return "Moderate"
        elif risk_score < 0.8:
            return "High"
        else:
            return "Extreme"

    def _estimate_operation_timeline(
        self,
        operation_type: EspionageOperationType,
        difficulty: int
    ) -> Dict[str, Any]:
        """Estimate how long an operation will take"""
        
        # Base duration in hours by operation type
        base_durations = {
            EspionageOperationType.PRICE_INTELLIGENCE: 4,
            EspionageOperationType.ROUTE_SURVEILLANCE: 8,
            EspionageOperationType.SUPPLIER_INTELLIGENCE: 12,
            EspionageOperationType.TRADE_SECRET_THEFT: 24,
            EspionageOperationType.AGENT_RECRUITMENT: 48,
            EspionageOperationType.SHIPMENT_SABOTAGE: 6,
            EspionageOperationType.COUNTER_ESPIONAGE: 72,
            EspionageOperationType.REPUTATION_SABOTAGE: 48,
            EspionageOperationType.FACILITY_SABOTAGE: 12,
            EspionageOperationType.MARKET_MANIPULATION: 96,
            EspionageOperationType.NETWORK_INFILTRATION: 168  # 1 week
        }
        
        base_duration = base_durations.get(operation_type, 24)
        
        # Difficulty modifier (harder operations take longer)
        difficulty_modifier = 1.0 + (difficulty - 5) * 0.2
        
        estimated_hours = int(base_duration * difficulty_modifier)
        
        return {
            "estimated_hours": estimated_hours,
            "estimated_days": estimated_hours / 24,
            "base_duration": base_duration,
            "difficulty_modifier": difficulty_modifier
        }

    def _calculate_resource_requirements(
        self,
        operation_type: EspionageOperationType,
        difficulty: int
    ) -> Dict[str, Any]:
        """Calculate resources needed for an operation"""
        
        # Base resource costs by operation type
        base_costs = {
            EspionageOperationType.PRICE_INTELLIGENCE: 100,
            EspionageOperationType.ROUTE_SURVEILLANCE: 200,
            EspionageOperationType.SUPPLIER_INTELLIGENCE: 300,
            EspionageOperationType.TRADE_SECRET_THEFT: 800,
            EspionageOperationType.AGENT_RECRUITMENT: 1000,
            EspionageOperationType.SHIPMENT_SABOTAGE: 500,
            EspionageOperationType.COUNTER_ESPIONAGE: 1200,
            EspionageOperationType.REPUTATION_SABOTAGE: 600,
            EspionageOperationType.FACILITY_SABOTAGE: 1500,
            EspionageOperationType.MARKET_MANIPULATION: 2000,
            EspionageOperationType.NETWORK_INFILTRATION: 3000
        }
        
        base_cost = base_costs.get(operation_type, 500)
        difficulty_multiplier = 1.0 + (difficulty - 5) * 0.3
        
        return {
            "funding_required": int(base_cost * difficulty_multiplier),
            "equipment_level": min(10, max(1, difficulty)),
            "intelligence_access_required": difficulty >= 7,
            "high_risk_clearance": difficulty >= 8
        }

    def _apply_environmental_factors(self, factors: Dict[str, Any]) -> float:
        """Apply environmental factors to success chance"""
        modifier = 0.0
        
        # Weather conditions
        weather = factors.get("weather", "normal")
        if weather == "favorable":
            modifier += 0.1
        elif weather == "poor":
            modifier -= 0.1
        
        # Political climate
        political_tension = factors.get("political_tension", 0.5)
        modifier -= (political_tension - 0.5) * 0.2
        
        # Economic conditions
        economic_stability = factors.get("economic_stability", 0.5)
        modifier += (economic_stability - 0.5) * 0.1
        
        # Random events
        random_modifier = factors.get("random_events", 0.0)
        modifier += random_modifier
        
        return modifier

    def _calculate_detection_level(
        self,
        operation_type: EspionageOperationType,
        target_defenses: Dict[str, Any],
        assigned_agents: List[Dict[str, Any]],
        success_level: float
    ) -> float:
        """Calculate how much the operation was detected"""
        
        import random
        
        # Base detection chance
        base_detection = 0.3
        
        # Operation type modifier
        stealth_multipliers = {
            EspionageOperationType.ROUTE_SURVEILLANCE: 0.5,
            EspionageOperationType.PRICE_INTELLIGENCE: 0.6,
            EspionageOperationType.SUPPLIER_INTELLIGENCE: 0.7,
            EspionageOperationType.TRADE_SECRET_THEFT: 0.8,
            EspionageOperationType.AGENT_RECRUITMENT: 0.9,
            EspionageOperationType.COUNTER_ESPIONAGE: 0.7,
            EspionageOperationType.FACILITY_SABOTAGE: 1.5,
            EspionageOperationType.SHIPMENT_SABOTAGE: 1.3,
            EspionageOperationType.REPUTATION_SABOTAGE: 1.2,
            EspionageOperationType.MARKET_MANIPULATION: 1.1,
            EspionageOperationType.NETWORK_INFILTRATION: 0.9
        }
        
        stealth_modifier = stealth_multipliers.get(operation_type, 1.0)
        
        # Target security
        security_level = target_defenses.get("security_level", 5)
        security_modifier = security_level / 10.0
        
        # Agent skill reduces detection
        if assigned_agents:
            avg_skill = sum(agent.get("skill_level", 1) for agent in assigned_agents) / len(assigned_agents)
            skill_modifier = 1.0 - (avg_skill / 15.0)  # Better agents are stealthier
        else:
            skill_modifier = 1.2  # No agents = more obvious
        
        # Success affects detection (more successful ops might be noticed more)
        success_modifier = 1.0 + (success_level * 0.3)
        
        final_detection = base_detection * stealth_modifier * security_modifier * skill_modifier * success_modifier
        
        # Add some randomness
        random_factor = random.uniform(0.7, 1.3)
        final_detection *= random_factor
        
        return max(0.0, min(1.0, final_detection))

    def _determine_operation_outcomes(
        self,
        operation_type: EspionageOperationType,
        success_level: float,
        detection_level: float,
        target_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine operation outcomes using the main espionage service"""
        from backend.systems.espionage.services.espionage_service import EspionageService
        
        main_service = EspionageService()
        return main_service.determine_operation_outcomes(
            operation_type, success_level, detection_level, target_data
        )

    def _calculate_agent_burn_risk(
        self,
        agent_data: Dict[str, Any],
        detection_level: float,
        operation_type: EspionageOperationType
    ) -> float:
        """Calculate new agent burn risk using the main espionage service"""
        from backend.systems.espionage.services.espionage_service import EspionageService
        
        main_service = EspionageService()
        return main_service.calculate_agent_burn_risk(
            agent_data, detection_level, operation_type
        )

    def _calculate_heat_increase(
        self,
        operation_type: EspionageOperationType,
        detection_level: float
    ) -> int:
        """Calculate how much an agent's heat level increases"""
        
        base_heat = {
            EspionageOperationType.PRICE_INTELLIGENCE: 1,
            EspionageOperationType.ROUTE_SURVEILLANCE: 1,
            EspionageOperationType.SUPPLIER_INTELLIGENCE: 2,
            EspionageOperationType.TRADE_SECRET_THEFT: 3,
            EspionageOperationType.AGENT_RECRUITMENT: 2,
            EspionageOperationType.COUNTER_ESPIONAGE: 2,
            EspionageOperationType.FACILITY_SABOTAGE: 5,
            EspionageOperationType.SHIPMENT_SABOTAGE: 4,
            EspionageOperationType.REPUTATION_SABOTAGE: 3,
            EspionageOperationType.MARKET_MANIPULATION: 3,
            EspionageOperationType.NETWORK_INFILTRATION: 4
        }
        
        base = base_heat.get(operation_type, 2)
        detection_multiplier = 1.0 + detection_level
        
        return int(base * detection_multiplier) 