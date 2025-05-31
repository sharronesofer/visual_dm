"""
Repository Module for Diplomacy System

This module handles data persistence for diplomatic entities (treaties, negotiations, events).
It provides a consistent interface for storing, retrieving, updating, and deleting data.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

from backend.systems.diplomacy.models import (
    DiplomaticEvent, 
    DiplomaticEventType, 
    DiplomaticIncident,
    DiplomaticIncidentSeverity,
    DiplomaticIncidentType,
    DiplomaticStatus, 
    Negotiation, 
    NegotiationStatus, 
    Sanction,
    SanctionStatus,
    SanctionType,
    Treaty, 
    TreatyType,
    TreatyViolation,
    TreatyViolationType,
    Ultimatum,
    UltimatumStatus
)


class DiplomacyRepository:
    """Repository for managing diplomatic entities."""

    def __init__(self, data_dir: str = "data/diplomacy"):
        """
        Initialize the repository with a data directory.
        
        Args:
            data_dir: Directory where diplomatic data will be stored
        """
        self.data_dir = data_dir
        self.treaties_dir = os.path.join(data_dir, "treaties")
        self.negotiations_dir = os.path.join(data_dir, "negotiations")
        self.events_dir = os.path.join(data_dir, "events")
        self.relations_dir = os.path.join(data_dir, "relations")
        self.violations_dir = os.path.join(data_dir, "violations")
        self.sanctions_dir = os.path.join(data_dir, "sanctions")
        
        # Ensure data directories exist
        os.makedirs(self.treaties_dir, exist_ok=True)
        os.makedirs(self.negotiations_dir, exist_ok=True)
        os.makedirs(self.events_dir, exist_ok=True)
        os.makedirs(self.relations_dir, exist_ok=True)
        os.makedirs(self.violations_dir, exist_ok=True)
        os.makedirs(self.sanctions_dir, exist_ok=True)

    # Treaty methods
    
    def create_treaty(self, treaty: Treaty) -> Treaty:
        """Create a new treaty."""
        treaty_path = os.path.join(self.treaties_dir, f"{treaty.id}.json")
        with open(treaty_path, "w") as f:
            f.write(treaty.json())
        return treaty
    
    def get_treaty(self, treaty_id: UUID) -> Optional[Treaty]:
        """Get a treaty by ID."""
        treaty_path = os.path.join(self.treaties_dir, f"{treaty_id}.json")
        if not os.path.exists(treaty_path):
            return None
        
        with open(treaty_path, "r") as f:
            return Treaty.parse_raw(f.read())
    
    def update_treaty(self, treaty_id: UUID, updates: Dict) -> Optional[Treaty]:
        """Update a treaty with new values."""
        treaty = self.get_treaty(treaty_id)
        if not treaty:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(treaty, key):
                setattr(treaty, key, value)
        
        # Always update the updated_at timestamp
        treaty.updated_at = datetime.utcnow()
        
        # Save updated treaty
        treaty_path = os.path.join(self.treaties_dir, f"{treaty_id}.json")
        with open(treaty_path, "w") as f:
            f.write(treaty.json())
        
        return treaty
    
    def delete_treaty(self, treaty_id: UUID) -> bool:
        """Delete a treaty by ID."""
        treaty_path = os.path.join(self.treaties_dir, f"{treaty_id}.json")
        if not os.path.exists(treaty_path):
            return False
        
        os.remove(treaty_path)
        return True
    
    def list_treaties(
        self, 
        faction_id: Optional[UUID] = None,
        active_only: bool = False,
        treaty_type: Optional[TreatyType] = None
    ) -> List[Treaty]:
        """List treaties, optionally filtered by faction, active status, and type."""
        treaties = []
        
        for filename in os.listdir(self.treaties_dir):
            if not filename.endswith(".json"):
                continue
            
            treaty_path = os.path.join(self.treaties_dir, filename)
            with open(treaty_path, "r") as f:
                treaty = Treaty.parse_raw(f.read())
            
            # Filter by faction
            if faction_id and faction_id not in treaty.parties:
                continue
            
            # Filter by active status
            if active_only and not treaty.is_active:
                continue
            
            # Filter by treaty type
            if treaty_type and treaty.type != treaty_type:
                continue
            
            treaties.append(treaty)
        
        return treaties

    # Negotiation methods
    
    def create_negotiation(self, negotiation: Negotiation) -> Negotiation:
        """Create a new negotiation."""
        negotiation_path = os.path.join(self.negotiations_dir, f"{negotiation.id}.json")
        with open(negotiation_path, "w") as f:
            f.write(negotiation.json())
        return negotiation
    
    def get_negotiation(self, negotiation_id: UUID) -> Optional[Negotiation]:
        """Get a negotiation by ID."""
        negotiation_path = os.path.join(self.negotiations_dir, f"{negotiation_id}.json")
        if not os.path.exists(negotiation_path):
            return None
        
        with open(negotiation_path, "r") as f:
            return Negotiation.parse_raw(f.read())
    
    def update_negotiation(self, negotiation_id: UUID, updates: Dict) -> Optional[Negotiation]:
        """Update a negotiation with new values."""
        negotiation = self.get_negotiation(negotiation_id)
        if not negotiation:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(negotiation, key):
                setattr(negotiation, key, value)
        
        # Save updated negotiation
        negotiation_path = os.path.join(self.negotiations_dir, f"{negotiation_id}.json")
        with open(negotiation_path, "w") as f:
            f.write(negotiation.json())
        
        return negotiation
    
    def delete_negotiation(self, negotiation_id: UUID) -> bool:
        """Delete a negotiation by ID."""
        negotiation_path = os.path.join(self.negotiations_dir, f"{negotiation_id}.json")
        if not os.path.exists(negotiation_path):
            return False
        
        os.remove(negotiation_path)
        return True
    
    def list_negotiations(
        self, 
        faction_id: Optional[UUID] = None,
        status: Optional[NegotiationStatus] = None
    ) -> List[Negotiation]:
        """List negotiations, optionally filtered by faction and status."""
        negotiations = []
        
        for filename in os.listdir(self.negotiations_dir):
            if not filename.endswith(".json"):
                continue
            
            negotiation_path = os.path.join(self.negotiations_dir, filename)
            with open(negotiation_path, "r") as f:
                negotiation = Negotiation.parse_raw(f.read())
            
            # Filter by faction
            if faction_id and faction_id not in negotiation.parties:
                continue
            
            # Filter by status
            if status and negotiation.status != status:
                continue
            
            negotiations.append(negotiation)
        
        return negotiations

    # Diplomatic Event methods
    
    def create_event(self, event: DiplomaticEvent) -> DiplomaticEvent:
        """Create a new diplomatic event."""
        event_path = os.path.join(self.events_dir, f"{event.id}.json")
        with open(event_path, "w") as f:
            f.write(event.json())
        return event
    
    def get_event(self, event_id: UUID) -> Optional[DiplomaticEvent]:
        """Get a diplomatic event by ID."""
        event_path = os.path.join(self.events_dir, f"{event_id}.json")
        if not os.path.exists(event_path):
            return None
        
        with open(event_path, "r") as f:
            return DiplomaticEvent.parse_raw(f.read())
    
    def list_events(
        self, 
        faction_id: Optional[UUID] = None,
        event_type: Optional[DiplomaticEventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        public_only: bool = False
    ) -> List[DiplomaticEvent]:
        """List diplomatic events, optionally filtered by various criteria."""
        events = []
        
        for filename in os.listdir(self.events_dir):
            if not filename.endswith(".json"):
                continue
            
            event_path = os.path.join(self.events_dir, filename)
            with open(event_path, "r") as f:
                event = DiplomaticEvent.parse_raw(f.read())
            
            # Filter by faction
            if faction_id and faction_id not in event.factions:
                continue
            
            # Filter by event type
            if event_type and event.event_type != event_type:
                continue
            
            # Filter by time range
            if start_time and event.timestamp < start_time:
                continue
            if end_time and event.timestamp > end_time:
                continue
            
            # Filter by publicity
            if public_only and not event.public:
                continue
            
            events.append(event)
        
        # Sort by timestamp, newest first
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        return events

    # Faction Relationship methods
    
    def get_faction_relationship(self, faction_a_id: UUID, faction_b_id: UUID) -> Dict:
        """Get the diplomatic relationship between two factions."""
        # Ensure consistent order of faction IDs to generate a unique key
        if str(faction_a_id) > str(faction_b_id):
            faction_a_id, faction_b_id = faction_b_id, faction_a_id
        
        relation_path = os.path.join(self.relations_dir, f"{faction_a_id}_{faction_b_id}.json")
        if not os.path.exists(relation_path):
            # Return default relationship if none exists
            return {
                "faction_a_id": faction_a_id,
                "faction_b_id": faction_b_id,
                "status": DiplomaticStatus.NEUTRAL,
                "tension": 0,
                "treaties": [],
                "last_status_change": datetime.utcnow(),
                "negotiations": []
            }
        
        with open(relation_path, "r") as f:
            return json.load(f)
    
    def update_faction_relationship(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID, 
        updates: Dict
    ) -> Dict:
        """Update the diplomatic relationship between two factions."""
        # Ensure consistent order of faction IDs
        if str(faction_a_id) > str(faction_b_id):
            faction_a_id, faction_b_id = faction_b_id, faction_a_id
        
        relation_path = os.path.join(self.relations_dir, f"{faction_a_id}_{faction_b_id}.json")
        relation = self.get_faction_relationship(faction_a_id, faction_b_id)
        
        # Update relationship fields
        for key, value in updates.items():
            relation[key] = value
        
        # Update the last status change if status is updated
        if "status" in updates:
            relation["last_status_change"] = datetime.utcnow().isoformat()
        
        # Save updated relationship
        with open(relation_path, "w") as f:
            json.dump(relation, f)
        
        return relation
    
    def get_all_faction_relationships(self, faction_id: UUID) -> List[Dict]:
        """Get all diplomatic relationships for a faction."""
        relationships = []
        
        for filename in os.listdir(self.relations_dir):
            if not filename.endswith(".json"):
                continue
            
            # Extract faction IDs from filename
            parts = filename.split(".")[0].split("_")
            if len(parts) != 2:
                continue
            
            faction_a_id, faction_b_id = UUID(parts[0]), UUID(parts[1])
            
            # Check if our target faction is part of this relationship
            if faction_id != faction_a_id and faction_id != faction_b_id:
                continue
            
            # Load the relationship
            relation_path = os.path.join(self.relations_dir, filename)
            with open(relation_path, "r") as f:
                relationship = json.load(f)
            
            # Ensure the target faction is always faction_a in the response
            if faction_id == faction_b_id:
                # Swap faction IDs to make the target faction first
                relationship["faction_a_id"], relationship["faction_b_id"] = \
                    relationship["faction_b_id"], relationship["faction_a_id"]
            
            relationships.append(relationship)
        
        return relationships

    # Treaty Violation methods
    
    def create_violation(self, violation: TreatyViolation) -> TreatyViolation:
        """Create a new treaty violation record."""
        violation_path = os.path.join(self.violations_dir, f"{violation.id}.json")
        with open(violation_path, "w") as f:
            f.write(violation.json())
        return violation
    
    def get_violation(self, violation_id: UUID) -> Optional[TreatyViolation]:
        """Get a treaty violation by ID."""
        violation_path = os.path.join(self.violations_dir, f"{violation_id}.json")
        if not os.path.exists(violation_path):
            return None
        
        with open(violation_path, "r") as f:
            return TreatyViolation.parse_raw(f.read())
    
    def update_violation(self, violation_id: UUID, updates: Dict) -> Optional[TreatyViolation]:
        """Update a treaty violation with new values."""
        violation = self.get_violation(violation_id)
        if not violation:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(violation, key):
                setattr(violation, key, value)
        
        # Save updated violation
        violation_path = os.path.join(self.violations_dir, f"{violation_id}.json")
        with open(violation_path, "w") as f:
            f.write(violation.json())
        
        return violation
    
    def list_violations(
        self, 
        treaty_id: Optional[UUID] = None,
        faction_id: Optional[UUID] = None,
        violation_type: Optional[TreatyViolationType] = None,
        resolved: Optional[bool] = None
    ) -> List[TreatyViolation]:
        """List treaty violations, optionally filtered."""
        violations = []
        
        for filename in os.listdir(self.violations_dir):
            if not filename.endswith(".json"):
                continue
            
            violation_path = os.path.join(self.violations_dir, filename)
            with open(violation_path, "r") as f:
                violation = TreatyViolation.parse_raw(f.read())
            
            # Filter by treaty
            if treaty_id and violation.treaty_id != treaty_id:
                continue
            
            # Filter by faction (either violator or reporter)
            if faction_id and faction_id != violation.violator_id and faction_id != violation.reported_by:
                continue
            
            # Filter by violation type
            if violation_type and violation.violation_type != violation_type:
                continue
            
            # Filter by resolved status
            if resolved is not None and violation.resolved != resolved:
                continue
            
            violations.append(violation)
        
        return violations

    # Ultimatum Methods
    
    def create_ultimatum(self, ultimatum: dict) -> Ultimatum:
        """
        Create a new ultimatum.
        
        Args:
            ultimatum: The ultimatum data
            
        Returns:
            The created ultimatum object
        """
        ultimatums = self._load_ultimatums()
        
        new_ultimatum = Ultimatum(
            id=ultimatum.get("id", uuid4()),
            issuer_id=ultimatum["issuer_id"],
            recipient_id=ultimatum["recipient_id"],
            demands=ultimatum["demands"],
            consequences=ultimatum["consequences"],
            status=UltimatumStatus.PENDING,
            issue_date=ultimatum.get("issue_date", datetime.now()),
            deadline=ultimatum["deadline"],
            response_date=None,
            justification=ultimatum["justification"],
            public=ultimatum.get("public", True),
            witnessed_by=ultimatum.get("witnessed_by", []),
            related_incident_id=ultimatum.get("related_incident_id"),
            related_treaty_id=ultimatum.get("related_treaty_id"),
            related_event_id=ultimatum.get("related_event_id"),
            tension_change_on_issue=ultimatum.get("tension_change_on_issue", 20),
            tension_change_on_accept=ultimatum.get("tension_change_on_accept", -10),
            tension_change_on_reject=ultimatum.get("tension_change_on_reject", 40),
        )
        
        ultimatums[str(new_ultimatum.id)] = new_ultimatum.dict()
        self._save_ultimatums(ultimatums)
        
        # Create a corresponding diplomatic event
        event_data = {
            "event_type": DiplomaticEventType.ULTIMATUM_ISSUED,
            "factions": [new_ultimatum.issuer_id, new_ultimatum.recipient_id] + new_ultimatum.witnessed_by,
            "description": f"Ultimatum issued: {new_ultimatum.justification}",
            "severity": 70,  # Ultimatums are serious
            "public": new_ultimatum.public,
            "related_treaty_id": new_ultimatum.related_treaty_id,
            "metadata": {
                "ultimatum_id": str(new_ultimatum.id),
                "issuer_id": str(new_ultimatum.issuer_id),
                "recipient_id": str(new_ultimatum.recipient_id),
                "deadline": new_ultimatum.deadline.isoformat()
            },
            "tension_change": {
                str(new_ultimatum.recipient_id): new_ultimatum.tension_change_on_issue
            }
        }
        
        self.create_diplomatic_event(event_data)
        
        return new_ultimatum
    
    def get_ultimatum(self, ultimatum_id: UUID) -> Optional[Ultimatum]:
        """
        Get an ultimatum by ID.
        
        Args:
            ultimatum_id: The ID of the ultimatum to get
            
        Returns:
            The ultimatum object if found, None otherwise
        """
        ultimatums = self._load_ultimatums()
        
        ultimatum_data = ultimatums.get(str(ultimatum_id))
        if not ultimatum_data:
            return None
            
        return Ultimatum(**ultimatum_data)
    
    def update_ultimatum(self, ultimatum_id: UUID, updates: dict) -> Optional[Ultimatum]:
        """
        Update an ultimatum.
        
        Args:
            ultimatum_id: The ID of the ultimatum to update
            updates: The fields to update
            
        Returns:
            The updated ultimatum object if found, None otherwise
        """
        ultimatums = self._load_ultimatums()
        
        if str(ultimatum_id) not in ultimatums:
            return None
            
        ultimatum_data = ultimatums[str(ultimatum_id)]
        current_status = ultimatum_data.get("status")
        
        # Update fields
        for key, value in updates.items():
            if key in ultimatum_data:
                ultimatum_data[key] = value
        
        # If status is changing, record the response time
        new_status = updates.get("status")
        if new_status and new_status != current_status and new_status != UltimatumStatus.PENDING:
            ultimatum_data["response_date"] = datetime.now().isoformat()
        
        ultimatums[str(ultimatum_id)] = ultimatum_data
        self._save_ultimatums(ultimatums)
        
        # Create event if status changed to accepted or rejected
        ultimatum = Ultimatum(**ultimatum_data)
        if new_status in [UltimatumStatus.ACCEPTED, UltimatumStatus.REJECTED]:
            event_type = DiplomaticEventType.ULTIMATUM_ACCEPTED if new_status == UltimatumStatus.ACCEPTED else DiplomaticEventType.ULTIMATUM_REJECTED
            tension_change = ultimatum.tension_change_on_accept if new_status == UltimatumStatus.ACCEPTED else ultimatum.tension_change_on_reject
            
            event_data = {
                "event_type": event_type,
                "factions": [ultimatum.issuer_id, ultimatum.recipient_id] + ultimatum.witnessed_by,
                "description": f"Ultimatum {new_status.lower()}: {ultimatum.justification}",
                "severity": 60,
                "public": ultimatum.public,
                "related_treaty_id": ultimatum.related_treaty_id,
                "metadata": {
                    "ultimatum_id": str(ultimatum.id),
                    "issuer_id": str(ultimatum.issuer_id),
                    "recipient_id": str(ultimatum.recipient_id),
                }
            }
            
            if new_status == UltimatumStatus.ACCEPTED:
                event_data["tension_change"] = {
                    str(ultimatum.issuer_id): tension_change,
                    str(ultimatum.recipient_id): tension_change
                }
            else:  # Rejected
                event_data["tension_change"] = {
                    str(ultimatum.issuer_id): tension_change
                }
            
            self.create_diplomatic_event(event_data)
        
        return ultimatum
    
    def list_ultimatums(
        self, 
        faction_id: Optional[UUID] = None,
        as_issuer: bool = True,
        as_recipient: bool = True,
        status: Optional[UltimatumStatus] = None,
        active_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Ultimatum]:
        """
        List ultimatums with optional filtering.
        
        Args:
            faction_id: Filter by faction involved (either as issuer or recipient)
            as_issuer: Include ultimatums where faction is the issuer
            as_recipient: Include ultimatums where faction is the recipient
            status: Filter by ultimatum status
            active_only: Only include active ultimatums (not expired, not responded)
            limit: Maximum number of ultimatums to return
            offset: Number of ultimatums to skip
            
        Returns:
            List of ultimatum objects matching the criteria
        """
        ultimatums = self._load_ultimatums()
        
        result = []
        now = datetime.now()
        
        for ultimatum_data in ultimatums.values():
            # Convert date strings to datetime objects for comparison
            if isinstance(ultimatum_data.get("issue_date"), str):
                ultimatum_data["issue_date"] = datetime.fromisoformat(ultimatum_data["issue_date"])
            if isinstance(ultimatum_data.get("deadline"), str):
                ultimatum_data["deadline"] = datetime.fromisoformat(ultimatum_data["deadline"])
            if isinstance(ultimatum_data.get("response_date"), str) and ultimatum_data["response_date"]:
                ultimatum_data["response_date"] = datetime.fromisoformat(ultimatum_data["response_date"])
                
            ultimatum = Ultimatum(**ultimatum_data)
            
            # Apply filters
            if faction_id:
                is_issuer = ultimatum.issuer_id == faction_id
                is_recipient = ultimatum.recipient_id == faction_id
                
                if (not as_issuer and is_issuer) or (not as_recipient and is_recipient):
                    continue
                    
                if not (is_issuer or is_recipient or faction_id in ultimatum.witnessed_by):
                    continue
            
            if status and ultimatum.status != status:
                continue
                
            if active_only:
                # Active means status is PENDING and deadline has not passed
                if ultimatum.status != UltimatumStatus.PENDING or ultimatum.deadline < now:
                    continue
                
            result.append(ultimatum)
        
        # Sort by issue_date (most recent first)
        result.sort(key=lambda x: x.issue_date, reverse=True)
        
        # Apply pagination
        return result[offset:offset+limit]
    
    def _load_ultimatums(self) -> Dict[str, dict]:
        """Load ultimatums from file."""
        filepath = os.path.join(self.data_dir, "ultimatums.json")
        
        if not os.path.exists(filepath):
            return {}
            
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_ultimatums(self, ultimatums: Dict[str, dict]) -> None:
        """Save ultimatums to file."""
        filepath = os.path.join(self.data_dir, "ultimatums.json")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w") as f:
            json.dump(ultimatums, f, indent=2)

    # Sanctions methods
    
    def create_sanction(self, sanction: Sanction) -> Sanction:
        """
        Create a new diplomatic sanction.
        
        Args:
            sanction: The sanction data
            
        Returns:
            The created sanction object
        """
        sanction_path = os.path.join(self.sanctions_dir, f"{sanction.id}.json")
        with open(sanction_path, "w") as f:
            f.write(sanction.json())
        return sanction
    
    def get_sanction(self, sanction_id: UUID) -> Optional[Sanction]:
        """
        Get a sanction by ID.
        
        Args:
            sanction_id: The ID of the sanction to get
            
        Returns:
            The sanction object if found, None otherwise
        """
        sanction_path = os.path.join(self.sanctions_dir, f"{sanction_id}.json")
        if not os.path.exists(sanction_path):
            return None
        
        with open(sanction_path, "r") as f:
            return Sanction.parse_raw(f.read())
    
    def update_sanction(self, sanction_id: UUID, updates: Dict) -> Optional[Sanction]:
        """
        Update a sanction with new values.
        
        Args:
            sanction_id: The ID of the sanction to update
            updates: The fields to update
            
        Returns:
            The updated sanction object if found, None otherwise
        """
        sanction = self.get_sanction(sanction_id)
        if not sanction:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(sanction, key):
                setattr(sanction, key, value)
        
        # Save updated sanction
        sanction_path = os.path.join(self.sanctions_dir, f"{sanction_id}.json")
        with open(sanction_path, "w") as f:
            f.write(sanction.json())
        
        return sanction
    
    def delete_sanction(self, sanction_id: UUID) -> bool:
        """
        Delete a sanction by ID.
        
        Args:
            sanction_id: The ID of the sanction to delete
            
        Returns:
            True if successful, False otherwise
        """
        sanction_path = os.path.join(self.sanctions_dir, f"{sanction_id}.json")
        if not os.path.exists(sanction_path):
            return False
        
        os.remove(sanction_path)
        return True
    
    def list_sanctions(
        self,
        imposer_id: Optional[UUID] = None,
        target_id: Optional[UUID] = None,
        sanction_type: Optional[SanctionType] = None,
        status: Optional[SanctionStatus] = None,
        active_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Sanction]:
        """
        List sanctions with optional filtering.
        
        Args:
            imposer_id: Filter by faction imposing the sanction
            target_id: Filter by faction targeted by the sanction
            sanction_type: Filter by type of sanction
            status: Filter by sanction status
            active_only: Only include active sanctions
            limit: Maximum number of sanctions to return
            offset: Number of sanctions to skip
            
        Returns:
            List of sanction objects matching the criteria
        """
        sanctions = []
        
        for filename in os.listdir(self.sanctions_dir):
            if not filename.endswith(".json"):
                continue
            
            sanction_path = os.path.join(self.sanctions_dir, filename)
            with open(sanction_path, "r") as f:
                sanction = Sanction.parse_raw(f.read())
            
            # Apply filters
            if imposer_id and sanction.imposer_id != imposer_id:
                continue
            
            if target_id and sanction.target_id != target_id:
                continue
            
            if sanction_type and sanction.sanction_type != sanction_type:
                continue
            
            if status and sanction.status != status:
                continue
            
            if active_only and sanction.status != SanctionStatus.ACTIVE:
                continue
            
            sanctions.append(sanction)
        
        # Sort by imposed_date (newest first)
        sanctions.sort(key=lambda s: s.imposed_date, reverse=True)
        
        # Apply pagination
        return sanctions[offset:offset+limit]
    
    def record_sanction_violation(
        self,
        sanction_id: UUID,
        violation: Dict
    ) -> Optional[Sanction]:
        """
        Record a violation of a sanction.
        
        Args:
            sanction_id: The ID of the sanction that was violated
            violation: Details of the violation
            
        Returns:
            The updated sanction object if found, None otherwise
        """
        sanction = self.get_sanction(sanction_id)
        if not sanction:
            return None
        
        # Make sure the violation has a date
        if "violation_date" not in violation:
            violation["violation_date"] = datetime.utcnow().isoformat()
        
        # Add the violation to the sanction's violations list
        violations = sanction.violations.copy()
        violations.append(violation)
        
        return self.update_sanction(
            sanction_id=sanction_id,
            updates={
                "violations": violations,
                "status": SanctionStatus.VIOLATED
            }
        ) 