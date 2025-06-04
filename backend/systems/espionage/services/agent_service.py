"""
Espionage Agent Service

Specialized service for managing espionage agents including recruitment,
training, assignment, and risk management. Handles the lifecycle of
espionage agents from recruitment to retirement or burn.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta

from backend.systems.espionage.models import (
    EspionageOperationType,
    AgentRole,
    EspionageAgent
)
from backend.infrastructure.config_loaders.espionage_config_loader import get_espionage_config


class EspionageAgentService:
    """Service for managing espionage agents"""

    def __init__(self):
        """Initialize the agent service"""
        self.config = get_espionage_config()

    def recommend_agents_for_operation(
        self,
        available_agents: List[Dict[str, Any]],
        operation_type: EspionageOperationType,
        operation_difficulty: int,
        max_agents: int = 3
    ) -> List[Dict[str, Any]]:
        """Recommend the best agents for a specific operation"""
        
        # Score each agent for this operation
        scored_agents = []
        for agent in available_agents:
            validation = self.validate_agent_assignment(agent, operation_type, operation_difficulty)
            if not validation["can_assign"]:
                continue
            
            # Calculate agent score
            skill_level = agent.get("skill_level", 1)
            burn_risk = agent.get("burn_risk", 0.0)
            agent_role = agent.get("role", "informant")
            effectiveness = self.config.get_agent_effectiveness(agent_role, operation_type.value)
            
            # Score calculation (higher is better)
            score = (
                skill_level * 10 +  # Skill contributes heavily
                effectiveness * 20 +  # Role effectiveness is important
                (1.0 - burn_risk) * 15 +  # Lower burn risk is better
                len(validation["warnings"]) * -5  # Warnings reduce score
            )
            
            scored_agents.append({
                "agent": agent,
                "score": score,
                "validation": validation,
                "effectiveness": effectiveness,
                "risk_assessment": self._assess_agent_risk_for_operation(agent, operation_type)
            })
        
        # Sort by score and return top agents
        scored_agents.sort(key=lambda x: x["score"], reverse=True)
        return scored_agents[:max_agents]

    def validate_agent_assignment(
        self,
        agent_data: Dict[str, Any],
        operation_type: EspionageOperationType,
        operation_difficulty: int
    ) -> Dict[str, Any]:
        """Validate if an agent can be assigned to an operation"""
        validation_result = {
            "can_assign": True,
            "warnings": [],
            "blocking_issues": []
        }
        
        # Check agent status
        agent_status = agent_data.get("status", "active")
        if agent_status != "active":
            validation_result["can_assign"] = False
            validation_result["blocking_issues"].append(f"Agent status is {agent_status}")
        
        # Check burn risk
        burn_risk = agent_data.get("burn_risk", 0.0)
        restriction_threshold = self.config.get_risk_threshold("operation_restriction")
        retirement_threshold = self.config.get_risk_threshold("agent_retirement")
        
        if burn_risk > retirement_threshold:
            validation_result["can_assign"] = False
            validation_result["blocking_issues"].append(f"Agent burn risk too high: {burn_risk:.2f}")
        elif burn_risk > restriction_threshold:
            validation_result["warnings"].append(f"Agent has elevated burn risk: {burn_risk:.2f}")
        
        # Check if agent is already assigned
        current_assignment = agent_data.get("current_assignment")
        if current_assignment:
            validation_result["can_assign"] = False
            validation_result["blocking_issues"].append("Agent is already assigned to another operation")
        
        # Check skill level vs operation difficulty
        skill_level = agent_data.get("skill_level", 1)
        if skill_level < (operation_difficulty - 3):  # Allow up to 3 levels below
            validation_result["warnings"].append(f"Agent skill ({skill_level}) may be too low for difficulty {operation_difficulty}")
        
        # Check agent effectiveness for operation type
        agent_role = agent_data.get("role", "informant")
        effectiveness = self.config.get_agent_effectiveness(agent_role, operation_type.value)
        if effectiveness < 0.8:  # Less than 80% effective
            validation_result["warnings"].append(f"Agent role {agent_role} not well-suited for {operation_type.value}")
        
        # Check heat level
        heat_level = agent_data.get("heat_level", 0)
        if heat_level >= 8:
            validation_result["warnings"].append(f"Agent has high heat level: {heat_level}")
        elif heat_level >= 6:
            validation_result["warnings"].append(f"Agent has moderate heat level: {heat_level}")
        
        return validation_result

    def assess_recruitment_potential(
        self,
        npc_data: Dict[str, Any],
        recruiting_faction: Dict[str, Any],
        target_role: AgentRole
    ) -> Dict[str, Any]:
        """Assess how likely an NPC is to be recruited as an agent"""
        
        recruitment_assessment = {
            "recruitment_chance": 0.0,
            "factors": {},
            "recommended_approach": "",
            "estimated_cost": 0,
            "risk_factors": []
        }
        
        # Base recruitment chance by NPC characteristics
        base_chance = 0.3  # 30% base chance
        
        # Loyalty to current faction affects recruitment
        current_loyalty = npc_data.get("loyalty_score", 50)
        loyalty_modifier = (100 - current_loyalty) / 200.0  # 0.0 to 0.5
        
        # Financial situation affects recruitment
        wealth_level = npc_data.get("wealth_level", 5)
        if wealth_level <= 3:
            financial_modifier = 0.2  # Desperate for money
        elif wealth_level <= 6:
            financial_modifier = 0.1  # Could use extra income
        else:
            financial_modifier = -0.1  # Financially secure
        
        # Personality traits affect recruitment
        personality_modifier = 0.0
        personality_traits = npc_data.get("personality_traits", [])
        
        if "ambitious" in personality_traits:
            personality_modifier += 0.15
        if "greedy" in personality_traits:
            personality_modifier += 0.1
        if "loyal" in personality_traits:
            personality_modifier -= 0.2
        if "honest" in personality_traits:
            personality_modifier -= 0.15
        if "pragmatic" in personality_traits:
            personality_modifier += 0.05
        
        # Access level affects value and difficulty
        access_level = npc_data.get("access_level", 1)
        access_modifier = access_level * 0.02  # Higher access = slightly easier to recruit
        
        # Calculate final recruitment chance
        final_chance = base_chance + loyalty_modifier + financial_modifier + personality_modifier + access_modifier
        final_chance = max(0.0, min(1.0, final_chance))
        
        recruitment_assessment["recruitment_chance"] = final_chance
        recruitment_assessment["factors"] = {
            "base_chance": base_chance,
            "loyalty_modifier": loyalty_modifier,
            "financial_modifier": financial_modifier,
            "personality_modifier": personality_modifier,
            "access_modifier": access_modifier
        }
        
        # Determine recommended approach
        if financial_modifier > 0.1:
            recruitment_assessment["recommended_approach"] = "Financial incentives"
        elif "ambitious" in personality_traits:
            recruitment_assessment["recommended_approach"] = "Promise of advancement"
        elif loyalty_modifier > 0.2:
            recruitment_assessment["recommended_approach"] = "Exploit dissatisfaction"
        else:
            recruitment_assessment["recommended_approach"] = "Gradual cultivation"
        
        # Estimate cost
        base_cost = 1000
        loyalty_cost_multiplier = 1.0 + (current_loyalty / 50.0)  # Higher loyalty = more expensive
        access_cost_multiplier = 1.0 + (access_level * 0.2)  # Higher access = more expensive
        
        recruitment_assessment["estimated_cost"] = int(base_cost * loyalty_cost_multiplier * access_cost_multiplier)
        
        # Identify risk factors
        if current_loyalty > 70:
            recruitment_assessment["risk_factors"].append("High loyalty to current faction")
        if "honest" in personality_traits:
            recruitment_assessment["risk_factors"].append("Strong moral principles")
        if access_level > 7:
            recruitment_assessment["risk_factors"].append("High-profile target - increased scrutiny")
        
        return recruitment_assessment

    def manage_agent_heat_and_burnout(
        self,
        agent_data: Dict[str, Any],
        time_since_last_operation: int = 0
    ) -> Dict[str, Any]:
        """Manage agent heat levels and burnout recovery"""
        
        current_heat = agent_data.get("heat_level", 0)
        current_burn_risk = agent_data.get("burn_risk", 0.0)
        
        # Heat naturally decreases over time
        heat_decay_rate = 0.1 * (time_since_last_operation / 24)  # Decreases based on hours since last op
        new_heat = max(0, current_heat - heat_decay_rate)
        
        # Burn risk decreases slowly over time if agent is inactive
        burn_decay_rate = 0.01 * (time_since_last_operation / 168)  # Weekly decay when inactive
        new_burn_risk = max(0.0, current_burn_risk - burn_decay_rate)
        
        # Determine agent status recommendations
        recommendations = []
        status_changes = {}
        
        retirement_threshold = self.config.get_risk_threshold("agent_retirement")
        restriction_threshold = self.config.get_risk_threshold("operation_restriction")
        
        if new_burn_risk > retirement_threshold:
            recommendations.append("Agent should be retired immediately")
            status_changes["recommended_status"] = "retired"
        elif new_burn_risk > restriction_threshold:
            recommendations.append("Agent should be restricted to low-risk operations only")
            status_changes["recommended_status"] = "restricted"
        elif new_heat > 7:
            recommendations.append("Agent should lay low for several weeks")
            status_changes["cooling_off_period"] = 14  # days
        
        return {
            "new_heat_level": int(new_heat),
            "new_burn_risk": new_burn_risk,
            "heat_change": current_heat - new_heat,
            "burn_risk_change": current_burn_risk - new_burn_risk,
            "recommendations": recommendations,
            "status_changes": status_changes
        }

    def train_agent(
        self,
        agent_data: Dict[str, Any],
        training_type: str,
        training_duration: int = 30  # days
    ) -> Dict[str, Any]:
        """Simulate agent training to improve capabilities"""
        
        current_skill = agent_data.get("skill_level", 1)
        training_cost_base = 500
        
        training_result = {
            "success": False,
            "skill_improvement": 0,
            "new_skill_level": current_skill,
            "cost": training_cost_base,
            "training_effects": {}
        }
        
        # Different training types have different effects
        training_effects = {
            "basic_tradecraft": {
                "skill_improvement": 1,
                "cost_multiplier": 1.0,
                "burn_risk_reduction": 0.05
            },
            "advanced_infiltration": {
                "skill_improvement": 2,
                "cost_multiplier": 2.0,
                "specialization_bonus": 0.1
            },
            "counter_surveillance": {
                "skill_improvement": 1,
                "cost_multiplier": 1.5,
                "heat_resistance": 2
            },
            "technical_skills": {
                "skill_improvement": 1,
                "cost_multiplier": 1.8,
                "tech_bonus": 0.15
            }
        }
        
        if training_type not in training_effects:
            training_result["error"] = f"Unknown training type: {training_type}"
            return training_result
        
        effects = training_effects[training_type]
        
        # Calculate success chance based on current skill and training type
        base_success_chance = 0.7
        skill_modifier = min(0.2, current_skill * 0.02)  # Easier for more skilled agents
        final_success_chance = base_success_chance + skill_modifier
        
        # Determine if training succeeds
        import random
        training_succeeds = random.random() < final_success_chance
        
        if training_succeeds:
            skill_improvement = effects["skill_improvement"]
            new_skill_level = min(10, current_skill + skill_improvement)
            
            training_result.update({
                "success": True,
                "skill_improvement": skill_improvement,
                "new_skill_level": new_skill_level,
                "cost": int(training_cost_base * effects["cost_multiplier"]),
                "training_effects": effects
            })
        else:
            # Partial improvement even on failure
            partial_improvement = max(0, effects["skill_improvement"] - 1)
            new_skill_level = min(10, current_skill + partial_improvement)
            
            training_result.update({
                "success": False,
                "skill_improvement": partial_improvement,
                "new_skill_level": new_skill_level,
                "cost": int(training_cost_base * effects["cost_multiplier"] * 0.7)  # Reduced cost on failure
            })
        
        return training_result

    def evaluate_agent_performance(
        self,
        agent_data: Dict[str, Any],
        recent_operations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Evaluate an agent's performance based on recent operations"""
        
        performance_metrics = {
            "overall_rating": "Average",
            "success_rate": 0.0,
            "reliability_score": 0.0,
            "risk_management": "Good",
            "specialization_effectiveness": {},
            "recommendations": []
        }
        
        if not recent_operations:
            performance_metrics["overall_rating"] = "Untested"
            return performance_metrics
        
        # Calculate success rate
        successful_ops = [op for op in recent_operations if op.get("success_level", 0) > 0.5]
        success_rate = len(successful_ops) / len(recent_operations)
        performance_metrics["success_rate"] = success_rate
        
        # Calculate reliability (consistency of performance)
        success_levels = [op.get("success_level", 0) for op in recent_operations]
        if success_levels:
            avg_success = sum(success_levels) / len(success_levels)
            variance = sum((x - avg_success) ** 2 for x in success_levels) / len(success_levels)
            reliability_score = max(0.0, 1.0 - variance)  # Lower variance = higher reliability
            performance_metrics["reliability_score"] = reliability_score
        
        # Evaluate risk management
        detection_levels = [op.get("detection_level", 0) for op in recent_operations]
        if detection_levels:
            avg_detection = sum(detection_levels) / len(detection_levels)
            if avg_detection < 0.3:
                performance_metrics["risk_management"] = "Excellent"
            elif avg_detection < 0.5:
                performance_metrics["risk_management"] = "Good"
            elif avg_detection < 0.7:
                performance_metrics["risk_management"] = "Fair"
            else:
                performance_metrics["risk_management"] = "Poor"
        
        # Analyze effectiveness by operation type
        agent_role = agent_data.get("role", "informant")
        operation_types = {}
        for op in recent_operations:
            op_type = op.get("operation_type", "unknown")
            if op_type not in operation_types:
                operation_types[op_type] = {"count": 0, "total_success": 0.0}
            operation_types[op_type]["count"] += 1
            operation_types[op_type]["total_success"] += op.get("success_level", 0)
        
        for op_type, data in operation_types.items():
            avg_success = data["total_success"] / data["count"]
            expected_effectiveness = self.config.get_agent_effectiveness(agent_role, op_type)
            performance_metrics["specialization_effectiveness"][op_type] = {
                "average_success": avg_success,
                "expected_effectiveness": expected_effectiveness,
                "performance_vs_expected": avg_success / max(0.1, expected_effectiveness)
            }
        
        # Generate recommendations
        if success_rate < 0.4:
            performance_metrics["recommendations"].append("Consider additional training or reassignment")
        if reliability_score < 0.5:
            performance_metrics["recommendations"].append("Inconsistent performance - review agent motivation")
        if avg_detection > 0.6:
            performance_metrics["recommendations"].append("High detection rate - needs stealth training")
        
        # Overall rating
        if success_rate > 0.8 and reliability_score > 0.7:
            performance_metrics["overall_rating"] = "Excellent"
        elif success_rate > 0.6 and reliability_score > 0.5:
            performance_metrics["overall_rating"] = "Good"
        elif success_rate > 0.4:
            performance_metrics["overall_rating"] = "Average"
        else:
            performance_metrics["overall_rating"] = "Poor"
        
        return performance_metrics

    def _assess_agent_risk_for_operation(
        self,
        agent_data: Dict[str, Any],
        operation_type: EspionageOperationType
    ) -> Dict[str, Any]:
        """Assess the risk profile of an agent for a specific operation"""
        
        current_burn_risk = agent_data.get("burn_risk", 0.0)
        heat_level = agent_data.get("heat_level", 0)
        
        # Base operation risk
        operation_risk = self.config.get_burn_risk_multiplier(operation_type.value)
        
        # Compound risks
        total_risk = current_burn_risk + operation_risk
        heat_risk = heat_level / 10.0
        
        return {
            "current_burn_risk": current_burn_risk,
            "operation_risk_increase": operation_risk,
            "heat_risk": heat_risk,
            "total_projected_risk": total_risk,
            "risk_category": self._categorize_agent_risk(total_risk)
        }

    def _categorize_agent_risk(self, risk_level: float) -> str:
        """Categorize agent risk level"""
        retirement_threshold = self.config.get_risk_threshold("agent_retirement")
        restriction_threshold = self.config.get_risk_threshold("operation_restriction")
        
        if risk_level > retirement_threshold:
            return "Critical - Retirement Recommended"
        elif risk_level > restriction_threshold:
            return "High - Restrict to Low-Risk Operations"
        elif risk_level > 0.3:
            return "Moderate - Monitor Closely"
        else:
            return "Low - Suitable for Operations" 