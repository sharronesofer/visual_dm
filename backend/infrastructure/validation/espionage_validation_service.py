"""
Espionage Validation Service

Implements validation logic for the espionage system including
JSON schema validation, data integrity checks, and business rule validation.
"""

import json
import jsonschema
from typing import Dict, Any, List, Optional
from pathlib import Path

from backend.systems.espionage.models import EspionageOperationType


class EspionageValidationServiceImpl:
    """Implementation of espionage validation service with JSON schema support"""
    
    def __init__(self, schema_path: Optional[str] = None):
        """Initialize with optional custom schema path"""
        if schema_path:
            self.schema_path = Path(schema_path)
        else:
            # Default to the schema we created
            self.schema_path = Path("data/systems/espionage/espionage_config_schema.json")
        
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema for espionage configuration"""
        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Return a basic schema if the file doesn't exist
            return {
                "type": "object",
                "properties": {},
                "additionalProperties": True
            }
    
    def validate_operation_data(self, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate operation creation/update data"""
        validated_data = operation_data.copy()
        validation_errors = []
        
        # Required fields validation
        required_fields = ["operation_type", "initiator_id", "target_id"]
        for field in required_fields:
            if field not in operation_data:
                validation_errors.append(f"Missing required field: {field}")
        
        # Operation type validation
        if "operation_type" in operation_data:
            op_type = operation_data["operation_type"]
            if isinstance(op_type, str):
                try:
                    EspionageOperationType(op_type)
                except ValueError:
                    validation_errors.append(f"Invalid operation type: {op_type}")
            else:
                validation_errors.append("Operation type must be a string")
        
        # Success level validation (if present)
        if "success_level" in operation_data:
            success_level = operation_data["success_level"]
            if not isinstance(success_level, (int, float)) or not (0.0 <= success_level <= 1.0):
                validation_errors.append("Success level must be a number between 0.0 and 1.0")
        
        # Detection level validation (if present)
        if "detection_level" in operation_data:
            detection_level = operation_data["detection_level"]
            if not isinstance(detection_level, (int, float)) or not (0.0 <= detection_level <= 1.0):
                validation_errors.append("Detection level must be a number between 0.0 and 1.0")
        
        # Add validation status to result
        validated_data["validation_errors"] = validation_errors
        validated_data["is_valid"] = len(validation_errors) == 0
        
        return validated_data
    
    def validate_agent_assignment(self, agent_data: Dict[str, Any], operation_type: str) -> bool:
        """Validate agent assignment to operation"""
        # Check agent status
        if agent_data.get("status") != "active":
            return False
        
        # Check burn risk
        burn_risk = agent_data.get("burn_risk", 0.0)
        if burn_risk > 0.8:  # High burn risk threshold
            return False
        
        # Check if agent role exists
        agent_role = agent_data.get("role")
        valid_roles = ["spymaster", "infiltrator", "informant", "saboteur", 
                      "courier", "analyst", "handler", "sleeper"]
        if agent_role not in valid_roles:
            return False
        
        # Check operation type validity
        try:
            EspionageOperationType(operation_type)
        except ValueError:
            return False
        
        return True
    
    def validate_security_clearance(self, agent_data: Dict[str, Any], operation_sensitivity: int) -> bool:
        """Validate agent security clearance"""
        agent_clearance = agent_data.get("security_clearance", 1)
        
        # Agent must have clearance >= operation sensitivity
        return agent_clearance >= operation_sensitivity
    
    def validate_config_data(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration data against JSON schema"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            jsonschema.validate(config_data, self.schema)
        except jsonschema.ValidationError as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append({
                "message": e.message,
                "path": list(e.absolute_path),
                "failed_value": e.instance
            })
        except jsonschema.SchemaError as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append({
                "message": f"Schema error: {e.message}",
                "path": [],
                "failed_value": None
            })
        
        # Additional business rule validation
        self._validate_business_rules(config_data, validation_result)
        
        return validation_result
    
    def _validate_business_rules(self, config_data: Dict[str, Any], validation_result: Dict[str, Any]):
        """Validate business rules for configuration data"""
        
        # Check that operation success rates are reasonable
        if "operation_success_rates" in config_data:
            success_rates = config_data["operation_success_rates"]
            for op_type, rate in success_rates.items():
                if rate < 0.1:
                    validation_result["warnings"].append(
                        f"Very low success rate for {op_type}: {rate:.1%}"
                    )
                elif rate > 0.9:
                    validation_result["warnings"].append(
                        f"Very high success rate for {op_type}: {rate:.1%}"
                    )
        
        # Check that burn risk multipliers are sensible
        if "burn_risk_multipliers" in config_data:
            risk_multipliers = config_data["burn_risk_multipliers"]
            for op_type, multiplier in risk_multipliers.items():
                if multiplier > 0.5:
                    validation_result["warnings"].append(
                        f"High burn risk for {op_type}: {multiplier:.1%} per operation"
                    )
        
        # Check that risk thresholds are ordered correctly
        if "risk_thresholds" in config_data:
            thresholds = config_data["risk_thresholds"]
            
            # Operation restriction should be less than retirement
            if ("operation_restriction" in thresholds and 
                "agent_retirement" in thresholds):
                
                if thresholds["operation_restriction"] >= thresholds["agent_retirement"]:
                    validation_result["errors"].append({
                        "message": "Operation restriction threshold must be less than retirement threshold",
                        "path": ["risk_thresholds"],
                        "failed_value": thresholds
                    })
                    validation_result["is_valid"] = False
        
        # Check agent effectiveness balance
        if "agent_effectiveness" in config_data:
            effectiveness = config_data["agent_effectiveness"]
            
            # Check that each role has some operations where they're effective
            for role, operations in effectiveness.items():
                max_effectiveness = max(operations.values()) if operations else 0
                if max_effectiveness < 1.2:
                    validation_result["warnings"].append(
                        f"Role {role} may not be specialized enough (max effectiveness: {max_effectiveness:.1f})"
                    )
    
    def validate_operation_feasibility(
        self, 
        operation_data: Dict[str, Any], 
        available_agents: List[Dict[str, Any]],
        config_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate if an operation is feasible with current resources"""
        
        feasibility_result = {
            "feasible": True,
            "confidence": 1.0,
            "issues": [],
            "recommendations": []
        }
        
        operation_type = operation_data.get("operation_type")
        if not operation_type:
            feasibility_result["feasible"] = False
            feasibility_result["issues"].append("No operation type specified")
            return feasibility_result
        
        # Check if we have suitable agents
        suitable_agents = []
        for agent in available_agents:
            if self.validate_agent_assignment(agent, operation_type):
                suitable_agents.append(agent)
        
        if not suitable_agents:
            feasibility_result["feasible"] = False
            feasibility_result["issues"].append("No suitable agents available")
            feasibility_result["recommendations"].append("Recruit additional agents or wait for existing agents to cool down")
        
        # Check success probability if we have config data
        if suitable_agents and config_data:
            base_success_rate = config_data.get("operation_success_rates", {}).get(operation_type, 0.5)
            
            # Adjust for agent quality
            avg_skill = sum(agent.get("skill_level", 1) for agent in suitable_agents[:3]) / min(3, len(suitable_agents))
            adjusted_success = base_success_rate * (avg_skill / 5.0)  # Assuming skill 5 is baseline
            
            if adjusted_success < 0.3:
                feasibility_result["confidence"] *= 0.5
                feasibility_result["issues"].append(f"Low success probability: {adjusted_success:.1%}")
                feasibility_result["recommendations"].append("Consider improving agent skills or choosing easier target")
        
        return feasibility_result 