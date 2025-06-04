"""
Intelligence Database Adapter

Handles all database operations for intelligence, espionage, and information warfare.
This adapter extracts database-specific code from the business logic layer.
"""

import random
from typing import List, Dict, Optional, Tuple, Union, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.infrastructure.databases.diplomacy.intelligence_db_models import (
    IntelligenceAgent as DBAgent, IntelligenceNetwork as DBNetwork,
    IntelligenceOperation as DBOperation, IntelligenceReport as DBReport,
    CounterIntelligenceOperation as DBCounterOp, InformationWarfareOperation as DBInfoWar,
    IntelligenceAssessment as DBAssessment, SecurityBreach as DBBreach
)
from backend.infrastructure.databases.diplomacy.diplomacy_models import DiplomaticRelationship as DBRelationship

# Import business models
from backend.systems.diplomacy.models.intelligence_models import (
    IntelligenceAgent, IntelligenceNetwork, IntelligenceOperation, IntelligenceReport,
    CounterIntelligenceOperation, InformationWarfareOperation, IntelligenceAssessment,
    SecurityBreach, IntelligenceType, EspionageOperationType, InformationWarfareType,
    OperationStatus, IntelligenceQuality, AgentStatus, NetworkSecurityLevel
)


class IntelligenceDatabaseAdapter:
    """Database adapter for intelligence operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    # Agent Operations
    def create_agent(self, agent: IntelligenceAgent) -> IntelligenceAgent:
        """Create a new agent in the database"""
        db_agent = DBAgent(**agent.dict())
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        return self._db_agent_to_model(db_agent)
    
    def get_agent(self, agent_id: UUID) -> Optional[IntelligenceAgent]:
        """Get an agent by ID"""
        db_agent = self.db.query(DBAgent).filter(DBAgent.id == agent_id).first()
        return self._db_agent_to_model(db_agent) if db_agent else None
    
    def update_agent(self, agent_id: UUID, updates: Dict[str, Any]) -> Optional[IntelligenceAgent]:
        """Update an agent with new data"""
        db_agent = self.db.query(DBAgent).filter(DBAgent.id == agent_id).first()
        if not db_agent:
            return None
        
        for key, value in updates.items():
            if hasattr(db_agent, key):
                setattr(db_agent, key, value)
        
        db_agent.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_agent)
        return self._db_agent_to_model(db_agent)
    
    def get_available_agents(self, faction_id: UUID, specialization: Optional[IntelligenceType] = None) -> List[IntelligenceAgent]:
        """Get available agents for a faction"""
        query = self.db.query(DBAgent).filter(
            DBAgent.faction_id == faction_id,
            DBAgent.status == AgentStatus.ACTIVE,
            DBAgent.current_assignment.is_(None)
        )
        
        if specialization:
            query = query.filter(DBAgent.specialization == specialization)
        
        db_agents = query.all()
        return [self._db_agent_to_model(agent) for agent in db_agents]
    
    def get_faction_agents(self, faction_id: UUID) -> List[IntelligenceAgent]:
        """Get all agents for a faction"""
        db_agents = self.db.query(DBAgent).filter(DBAgent.faction_id == faction_id).all()
        return [self._db_agent_to_model(agent) for agent in db_agents]
    
    # Operation Operations
    def create_operation(self, operation: IntelligenceOperation) -> IntelligenceOperation:
        """Create a new operation in the database"""
        db_operation = DBOperation(**operation.dict())
        self.db.add(db_operation)
        self.db.commit()
        self.db.refresh(db_operation)
        return self._db_operation_to_model(db_operation)
    
    def get_operation(self, operation_id: UUID) -> Optional[IntelligenceOperation]:
        """Get an operation by ID"""
        db_operation = self.db.query(DBOperation).filter(DBOperation.id == operation_id).first()
        return self._db_operation_to_model(db_operation) if db_operation else None
    
    def update_operation(self, operation_id: UUID, updates: Dict[str, Any]) -> Optional[IntelligenceOperation]:
        """Update an operation with new data"""
        db_operation = self.db.query(DBOperation).filter(DBOperation.id == operation_id).first()
        if not db_operation:
            return None
        
        for key, value in updates.items():
            if hasattr(db_operation, key):
                setattr(db_operation, key, value)
        
        db_operation.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_operation)
        return self._db_operation_to_model(db_operation)
    
    def get_operations_targeting_faction(self, target_faction_id: UUID) -> List[IntelligenceOperation]:
        """Get operations targeting a specific faction"""
        db_operations = self.db.query(DBOperation).filter(
            DBOperation.target_faction == target_faction_id,
            DBOperation.status == OperationStatus.ACTIVE
        ).all()
        return [self._db_operation_to_model(op) for op in db_operations]
    
    # Report Operations
    def create_report(self, report: IntelligenceReport) -> IntelligenceReport:
        """Create a new intelligence report"""
        db_report = DBReport(**report.dict())
        self.db.add(db_report)
        self.db.commit()
        self.db.refresh(db_report)
        return self._db_report_to_model(db_report)
    
    def get_faction_reports(self, faction_id: UUID) -> List[IntelligenceReport]:
        """Get all intelligence reports for a faction"""
        db_reports = self.db.query(DBReport).filter(DBReport.recipient_faction == faction_id).all()
        return [self._db_report_to_model(report) for report in db_reports]
    
    def get_reports_by_ids(self, report_ids: List[UUID]) -> List[IntelligenceReport]:
        """Get multiple reports by their IDs"""
        db_reports = self.db.query(DBReport).filter(DBReport.id.in_(report_ids)).all()
        return [self._db_report_to_model(report) for report in db_reports]
    
    # Counter-Intelligence Operations
    def create_counter_operation(self, counter_op: CounterIntelligenceOperation) -> CounterIntelligenceOperation:
        """Create a new counter-intelligence operation"""
        db_counter_op = DBCounterOp(**counter_op.dict())
        self.db.add(db_counter_op)
        self.db.commit()
        self.db.refresh(db_counter_op)
        return self._db_counter_op_to_model(db_counter_op)
    
    # Information Warfare Operations
    def create_info_warfare_operation(self, info_war_op: InformationWarfareOperation) -> InformationWarfareOperation:
        """Create a new information warfare operation"""
        db_info_war = DBInfoWar(**info_war_op.dict())
        self.db.add(db_info_war)
        self.db.commit()
        self.db.refresh(db_info_war)
        return self._db_info_war_to_model(db_info_war)
    
    def get_info_warfare_operation(self, campaign_id: UUID) -> Optional[InformationWarfareOperation]:
        """Get an information warfare operation by ID"""
        db_info_war = self.db.query(DBInfoWar).filter(DBInfoWar.id == campaign_id).first()
        return self._db_info_war_to_model(db_info_war) if db_info_war else None
    
    def update_info_warfare_operation(self, campaign_id: UUID, updates: Dict[str, Any]) -> Optional[InformationWarfareOperation]:
        """Update an information warfare operation"""
        db_info_war = self.db.query(DBInfoWar).filter(DBInfoWar.id == campaign_id).first()
        if not db_info_war:
            return None
        
        for key, value in updates.items():
            if hasattr(db_info_war, key):
                setattr(db_info_war, key, value)
        
        db_info_war.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_info_war)
        return self._db_info_war_to_model(db_info_war)
    
    # Network Operations
    def create_network(self, network: IntelligenceNetwork) -> IntelligenceNetwork:
        """Create a new intelligence network"""
        db_network = DBNetwork(**network.dict())
        self.db.add(db_network)
        self.db.commit()
        self.db.refresh(db_network)
        return self._db_network_to_model(db_network)
    
    def get_faction_networks(self, faction_id: UUID) -> List[IntelligenceNetwork]:
        """Get all networks for a faction"""
        db_networks = self.db.query(DBNetwork).filter(DBNetwork.faction_id == faction_id).all()
        return [self._db_network_to_model(network) for network in db_networks]
    
    # Assessment Operations
    def create_assessment(self, assessment: IntelligenceAssessment) -> IntelligenceAssessment:
        """Create a new intelligence assessment"""
        db_assessment = DBAssessment(**assessment.dict())
        self.db.add(db_assessment)
        self.db.commit()
        self.db.refresh(db_assessment)
        return self._db_assessment_to_model(db_assessment)
    
    # Security Breach Operations
    def create_security_breach(self, operation: IntelligenceOperation, defending_faction: UUID):
        """Create a security breach record"""
        breach = SecurityBreach(
            operation_id=operation.id,
            defending_faction=defending_faction,
            breach_type="hostile_operation_detected",
            severity=50,
            description=f"Hostile intelligence operation detected: {operation.operation_name}"
        )
        
        db_breach = DBBreach(**breach.dict())
        self.db.add(db_breach)
        self.db.commit()
    
    # Model conversion methods
    def _db_agent_to_model(self, db_agent: DBAgent) -> IntelligenceAgent:
        """Convert database agent to Pydantic model"""
        return IntelligenceAgent(**{
            column.name: getattr(db_agent, column.name)
            for column in db_agent.__table__.columns
        })
    
    def _db_operation_to_model(self, db_operation: DBOperation) -> IntelligenceOperation:
        """Convert database operation to Pydantic model"""
        return IntelligenceOperation(**{
            column.name: getattr(db_operation, column.name)
            for column in db_operation.__table__.columns
        })
    
    def _db_report_to_model(self, db_report: DBReport) -> IntelligenceReport:
        """Convert database report to Pydantic model"""
        return IntelligenceReport(**{
            column.name: getattr(db_report, column.name)
            for column in db_report.__table__.columns
        })
    
    def _db_counter_op_to_model(self, db_counter_op: DBCounterOp) -> CounterIntelligenceOperation:
        """Convert database counter-op to Pydantic model"""
        return CounterIntelligenceOperation(**{
            column.name: getattr(db_counter_op, column.name)
            for column in db_counter_op.__table__.columns
        })
    
    def _db_info_war_to_model(self, db_info_war: DBInfoWar) -> InformationWarfareOperation:
        """Convert database info war to Pydantic model"""
        return InformationWarfareOperation(**{
            column.name: getattr(db_info_war, column.name)
            for column in db_info_war.__table__.columns
        })
    
    def _db_network_to_model(self, db_network: DBNetwork) -> IntelligenceNetwork:
        """Convert database network to Pydantic model"""
        return IntelligenceNetwork(**{
            column.name: getattr(db_network, column.name)
            for column in db_network.__table__.columns
        })
    
    def _db_assessment_to_model(self, db_assessment: DBAssessment) -> IntelligenceAssessment:
        """Convert database assessment to Pydantic model"""
        return IntelligenceAssessment(**{
            column.name: getattr(db_assessment, column.name)
            for column in db_assessment.__table__.columns
        }) 