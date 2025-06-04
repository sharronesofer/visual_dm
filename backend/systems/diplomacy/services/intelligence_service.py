"""
Diplomatic Intelligence and Espionage Service

This service handles all intelligence gathering, espionage operations, agent management,
information warfare, and counter-intelligence activities for the diplomatic system.

This is the pure business logic layer that delegates technical operations to infrastructure.
"""

import random
import math
from typing import List, Dict, Optional, Tuple, Union, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from ..models.intelligence_models import (
    IntelligenceAgent, IntelligenceNetwork, IntelligenceOperation, IntelligenceReport,
    CounterIntelligenceOperation, InformationWarfareOperation, IntelligenceAssessment,
    SecurityBreach, IntelligenceType, EspionageOperationType, InformationWarfareType,
    OperationStatus, IntelligenceQuality, AgentStatus, NetworkSecurityLevel
)
from ..models.core_models import DiplomaticEvent

# Import infrastructure components
from backend.infrastructure.databases.diplomacy.intelligence_database_adapter import IntelligenceDatabaseAdapter
from backend.infrastructure.utils.diplomacy.intelligence_utils import (
    IntelligenceCodeNameGenerator, IntelligenceCoverGenerator, IntelligenceOperationNameGenerator,
    IntelligenceCalculations, IntelligenceContentGenerators, IntelligenceAnalysis
)


class AgentManagementEngine:
    """Manages intelligence agents, recruitment, and operational assignments."""
    
    def __init__(self, db_adapter: IntelligenceDatabaseAdapter):
        self.db_adapter = db_adapter
    
    def recruit_agent(self, faction_id: UUID, specialization: IntelligenceType, 
                     skill_level: int = None) -> IntelligenceAgent:
        """Recruit a new intelligence agent for a faction."""
        if skill_level is None:
            skill_level = random.randint(30, 80)  # Random recruitment quality
        
        agent = IntelligenceAgent(
            code_name=IntelligenceCodeNameGenerator.generate_code_name(),
            faction_id=faction_id,
            specialization=specialization,
            skill_level=skill_level,
            cover_identity=IntelligenceCoverGenerator.generate_cover_identity(specialization),
            loyalty=random.randint(70, 95),
            stealth=random.randint(30, 80),
            infiltration=random.randint(30, 80),
            analysis=random.randint(30, 80)
        )
        
        return self.db_adapter.create_agent(agent)
    
    def assign_agent_to_operation(self, agent_id: UUID, operation_id: UUID) -> bool:
        """Assign an agent to an intelligence operation."""
        agent = self.db_adapter.get_agent(agent_id)
        if not agent or agent.status not in [AgentStatus.ACTIVE, AgentStatus.DEEP_COVER]:
            return False
        
        updates = {
            'current_assignment': operation_id,
            'updated_at': datetime.utcnow()
        }
        
        updated_agent = self.db_adapter.update_agent(agent_id, updates)
        return updated_agent is not None
    
    def evaluate_agent_performance(self, agent_id: UUID, operation_result: str) -> IntelligenceAgent:
        """Update agent stats based on operation results."""
        agent = self.db_adapter.get_agent(agent_id)
        if not agent:
            return None
        
        updates = {
            'operations_completed': agent.operations_completed + 1,
            'last_mission_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        if operation_result in ["success", "partial_success"]:
            updates['successful_operations'] = agent.successful_operations + 1
            # Boost skills based on success
            updates['skill_level'] = min(100, agent.skill_level + random.randint(1, 3))
        elif operation_result == "compromised":
            updates['compromised_count'] = agent.compromised_count + 1
            updates['cover_blown'] = True
            updates['status'] = AgentStatus.COMPROMISED
        
        return self.db_adapter.update_agent(agent_id, updates)
    
    def get_available_agents(self, faction_id: UUID, specialization: IntelligenceType = None) -> List[IntelligenceAgent]:
        """Get available agents for a faction, optionally filtered by specialization."""
        return self.db_adapter.get_available_agents(faction_id, specialization)


class IntelligenceGatheringEngine:
    """Handles intelligence gathering operations and analysis."""
    
    def __init__(self, db_adapter: IntelligenceDatabaseAdapter):
        self.db_adapter = db_adapter
    
    def plan_intelligence_operation(self, executing_faction: UUID, target_faction: UUID,
                                  operation_type: Union[IntelligenceType, EspionageOperationType],
                                  objectives: List[str]) -> IntelligenceOperation:
        """Plan a new intelligence gathering operation."""
        operation = IntelligenceOperation(
            operation_name=IntelligenceOperationNameGenerator.generate_operation_name(operation_type),
            operation_type=operation_type,
            description=f"Intelligence operation targeting {target_faction}",
            objectives=objectives,
            target_faction=target_faction,
            executing_faction=executing_faction,
            success_probability=IntelligenceCalculations.calculate_base_success_probability(operation_type),
            detection_risk=IntelligenceCalculations.calculate_base_detection_risk(operation_type),
            political_risk=IntelligenceCalculations.calculate_political_risk(operation_type)
        )
        
        return self.db_adapter.create_operation(operation)
    
    def execute_intelligence_operation(self, operation_id: UUID) -> Tuple[str, Optional[IntelligenceReport]]:
        """Execute an intelligence operation and generate results."""
        operation = self.db_adapter.get_operation(operation_id)
        if not operation:
            return "failed", None
        
        # Calculate operation success
        success_roll = random.randint(1, 100)
        detection_roll = random.randint(1, 100)
        
        # Determine outcome
        if success_roll <= operation.success_probability:
            if detection_roll <= operation.detection_risk:
                result = "compromised"
                intelligence_report = None
            else:
                result = "success"
                intelligence_report = self._generate_intelligence_report(operation)
        else:
            result = "failure"
            intelligence_report = None
        
        # Update operation
        updates = {
            'status': OperationStatus.COMPLETED,
            'operation_result': result,
            'actual_end': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        self.db_adapter.update_operation(operation_id, updates)
        
        return result, intelligence_report
    
    def analyze_intelligence_quality(self, report: IntelligenceReport) -> IntelligenceQuality:
        """Analyze and determine the quality of gathered intelligence."""
        base_quality_score = report.confidence_level
        
        # Adjust based on source reliability
        if report.corroboration_sources > 1:
            base_quality_score += 20
        
        # Determine quality level
        if base_quality_score >= 90:
            return IntelligenceQuality.CONFIRMED
        elif base_quality_score >= 70:
            return IntelligenceQuality.PROBABLE
        elif base_quality_score >= 50:
            return IntelligenceQuality.POSSIBLE
        elif base_quality_score >= 30:
            return IntelligenceQuality.DOUBTFUL
        else:
            return IntelligenceQuality.FABRICATED
    
    def _generate_intelligence_report(self, operation: IntelligenceOperation) -> IntelligenceReport:
        """Generate an intelligence report from a successful operation."""
        report = IntelligenceReport(
            operation_id=operation.id,
            intel_type=operation.operation_type if isinstance(operation.operation_type, IntelligenceType) else IntelligenceType.DIPLOMATIC_RECONNAISSANCE,
            content=IntelligenceContentGenerators.generate_intelligence_content(
                operation.operation_type if isinstance(operation.operation_type, IntelligenceType) else IntelligenceType.DIPLOMATIC_RECONNAISSANCE,
                operation.target_faction
            ),
            confidence_level=random.randint(60, 95),
            recipient_faction=operation.executing_faction,
            source_faction=operation.target_faction,
            corroboration_sources=random.randint(1, 3)
        )
        
        return self.db_adapter.create_report(report)


class CounterIntelligenceEngine:
    """Handles counter-intelligence and security operations."""
    
    def __init__(self, db_adapter: IntelligenceDatabaseAdapter):
        self.db_adapter = db_adapter
    
    def detect_hostile_operations(self, defending_faction: UUID) -> List[UUID]:
        """Detect hostile intelligence operations targeting a faction."""
        detected_operations = []
        
        # Get operations targeting this faction
        operations = self.db_adapter.get_operations_targeting_faction(defending_faction)
        
        for operation in operations:
            detection_probability = IntelligenceCalculations.calculate_detection_probability(operation, defending_faction)
            
            if random.randint(1, 100) <= detection_probability:
                detected_operations.append(operation.id)
                # Create security breach record
                self.db_adapter.create_security_breach(operation, defending_faction)
        
        return detected_operations
    
    def launch_counter_operation(self, defending_faction: UUID, threat_factions: List[UUID],
                                protection_scope: List[str]) -> CounterIntelligenceOperation:
        """Launch a counter-intelligence operation."""
        counter_op = CounterIntelligenceOperation(
            defending_faction=defending_faction,
            threat_factions=threat_factions,
            protection_scope=protection_scope,
            security_measures=IntelligenceContentGenerators.generate_security_measures(),
            surveillance_activities=IntelligenceContentGenerators.generate_surveillance_activities(),
            success_rate=random.randint(40, 80)
        )
        
        return self.db_adapter.create_counter_operation(counter_op)


class InformationWarfareEngine:
    """Handles information warfare and propaganda campaigns."""
    
    def __init__(self, db_adapter: IntelligenceDatabaseAdapter):
        self.db_adapter = db_adapter
    
    def launch_propaganda_campaign(self, executing_faction: UUID, target_factions: List[UUID],
                                 campaign_type: InformationWarfareType, primary_message: str) -> InformationWarfareOperation:
        """Launch an information warfare campaign."""
        campaign = InformationWarfareOperation(
            campaign_name=f"{campaign_type.value.title()} Campaign {random.randint(1000, 9999)}",
            campaign_type=campaign_type,
            executing_faction=executing_faction,
            target_factions=target_factions,
            primary_message=primary_message,
            narratives=IntelligenceContentGenerators.generate_narratives(campaign_type),
            media_channels=IntelligenceContentGenerators.generate_media_channels(),
            target_audiences=IntelligenceContentGenerators.generate_target_audiences(campaign_type)
        )
        
        return self.db_adapter.create_info_warfare_operation(campaign)
    
    def execute_information_campaign(self, campaign_id: UUID) -> Dict[str, Any]:
        """Execute an information warfare campaign."""
        campaign = self.db_adapter.get_info_warfare_operation(campaign_id)
        if not campaign:
            return {"status": "failed", "reason": "Campaign not found"}
        
        # Calculate effectiveness
        effectiveness = IntelligenceCalculations.calculate_campaign_effectiveness(campaign)
        reputation_impacts = IntelligenceCalculations.calculate_reputation_impacts(campaign, effectiveness)
        
        # Update campaign with results
        updates = {
            'status': OperationStatus.COMPLETED,
            'effectiveness_score': effectiveness,
            'actual_end': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        updated_campaign = self.db_adapter.update_info_warfare_operation(campaign_id, updates)
        
        return {
            "status": "success",
            "effectiveness": effectiveness,
            "reputation_impacts": reputation_impacts,
            "campaign": updated_campaign
        }


class IntelligenceService:
    """Main service for intelligence operations."""
    
    def __init__(self, db_adapter: IntelligenceDatabaseAdapter):
        self.db_adapter = db_adapter
        self.agent_manager = AgentManagementEngine(db_adapter)
        self.intelligence_gatherer = IntelligenceGatheringEngine(db_adapter)
        self.counter_intelligence = CounterIntelligenceEngine(db_adapter)
        self.info_warfare = InformationWarfareEngine(db_adapter)
    
    # Agent operations
    def recruit_agent(self, faction_id: UUID, specialization: IntelligenceType, 
                     skill_level: int = None) -> IntelligenceAgent:
        """Recruit a new intelligence agent."""
        return self.agent_manager.recruit_agent(faction_id, specialization, skill_level)
    
    def get_faction_agents(self, faction_id: UUID) -> List[IntelligenceAgent]:
        """Get all agents for a faction."""
        return self.db_adapter.get_faction_agents(faction_id)
    
    def assign_agent_to_operation(self, agent_id: UUID, operation_id: UUID) -> bool:
        """Assign an agent to an operation."""
        return self.agent_manager.assign_agent_to_operation(agent_id, operation_id)
    
    # Intelligence operations
    def plan_intelligence_operation(self, executing_faction: UUID, target_faction: UUID,
                                  operation_type: Union[IntelligenceType, EspionageOperationType],
                                  objectives: List[str]) -> IntelligenceOperation:
        """Plan a new intelligence operation."""
        return self.intelligence_gatherer.plan_intelligence_operation(
            executing_faction, target_faction, operation_type, objectives
        )
    
    def execute_intelligence_operation(self, operation_id: UUID) -> Tuple[str, Optional[IntelligenceReport]]:
        """Execute an intelligence operation."""
        return self.intelligence_gatherer.execute_intelligence_operation(operation_id)
    
    def get_faction_intelligence_reports(self, faction_id: UUID) -> List[IntelligenceReport]:
        """Get all intelligence reports for a faction."""
        return self.db_adapter.get_faction_reports(faction_id)
    
    # Counter-intelligence operations
    def run_security_sweep(self, defending_faction: UUID) -> List[UUID]:
        """Run a security sweep to detect hostile operations."""
        return self.counter_intelligence.detect_hostile_operations(defending_faction)
    
    def launch_counter_intelligence_operation(self, defending_faction: UUID, threat_factions: List[UUID],
                                            protection_scope: List[str]) -> CounterIntelligenceOperation:
        """Launch a counter-intelligence operation."""
        return self.counter_intelligence.launch_counter_operation(
            defending_faction, threat_factions, protection_scope
        )
    
    # Information warfare operations
    def launch_propaganda_campaign(self, executing_faction: UUID, target_factions: List[UUID],
                                 campaign_type: InformationWarfareType, primary_message: str) -> InformationWarfareOperation:
        """Launch a propaganda campaign."""
        return self.info_warfare.launch_propaganda_campaign(
            executing_faction, target_factions, campaign_type, primary_message
        )
    
    def execute_information_campaign(self, campaign_id: UUID) -> Dict[str, Any]:
        """Execute an information warfare campaign."""
        return self.info_warfare.execute_information_campaign(campaign_id)
    
    # Network operations
    def create_intelligence_network(self, faction_id: UUID, name: str, geographic_scope: List[str]) -> IntelligenceNetwork:
        """Create a new intelligence network."""
        network = IntelligenceNetwork(
            name=name,
            faction_id=faction_id,
            geographic_scope=geographic_scope,
            security_level=NetworkSecurityLevel.MODERATE,
            operational_capacity=random.randint(50, 90)
        )
        
        return self.db_adapter.create_network(network)
    
    def get_faction_networks(self, faction_id: UUID) -> List[IntelligenceNetwork]:
        """Get all intelligence networks for a faction."""
        return self.db_adapter.get_faction_networks(faction_id)
    
    # Assessment operations
    def generate_intelligence_assessment(self, faction_id: UUID, report_ids: List[UUID],
                                       assessment_focus: List[str] = None) -> IntelligenceAssessment:
        """Generate a comprehensive intelligence assessment."""
        reports = self.db_adapter.get_reports_by_ids(report_ids)
        
        assessment = IntelligenceAssessment(
            assessing_faction=faction_id,
            report_ids=report_ids,
            assessment_focus=assessment_focus or ["general"],
            key_insights=IntelligenceAnalysis.analyze_reports_for_insights(report_ids),
            confidence_level=IntelligenceAnalysis.calculate_assessment_confidence(report_ids),
            recommendations=["Continue monitoring", "Increase intelligence gathering", "Assess threat level"]
        )
        
        return self.db_adapter.create_assessment(assessment)
    
    def get_intelligence_statistics(self, faction_id: UUID) -> Dict[str, Any]:
        """Get intelligence statistics for a faction."""
        agents = self.get_faction_agents(faction_id)
        reports = self.get_faction_intelligence_reports(faction_id)
        networks = self.get_faction_networks(faction_id)
        
        active_agents = [a for a in agents if a.status == AgentStatus.ACTIVE]
        successful_operations = sum(1 for a in agents if a.successful_operations > 0)
        
        return {
            "total_agents": len(agents),
            "active_agents": len(active_agents),
            "total_reports": len(reports),
            "intelligence_networks": len(networks),
            "successful_operations": successful_operations,
            "average_agent_skill": sum(a.skill_level for a in agents) / len(agents) if agents else 0,
            "security_rating": sum(n.operational_capacity for n in networks) / len(networks) if networks else 0
        } 