"""
Repository Module for Diplomacy System

This module handles data persistence for diplomatic entities (treaties, negotiations, events).
It provides a consistent interface for storing, retrieving, updating, and deleting data.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from uuid import UUID, uuid4

from backend.systems.diplomacy.models.core_models import (
    DiplomaticStatus, TreatyType, TreatyStatus, NegotiationStatus,
    DiplomaticEventType, TreatyViolationType, DiplomaticIncidentType,
    DiplomaticIncidentSeverity, UltimatumStatus, SanctionType, SanctionStatus,
    Treaty, Negotiation, NegotiationOffer, DiplomaticEvent, TreatyViolation,
    DiplomaticIncident, Ultimatum, Sanction
)


class DiplomacyRepository:
    """Repository for managing diplomatic entities."""

    def __init__(self, data_dir: str = "data/systems/diplomacy"):
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

    # Diplomatic event methods
    
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
        """List diplomatic events, optionally filtered."""
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
            
            # Filter by public status
            if public_only and not event.public:
                continue
            
            events.append(event)
        
        # Sort by timestamp (most recent first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events

    # Diplomatic relationship methods
    
    def get_faction_relationship(self, faction_a_id: UUID, faction_b_id: UUID) -> Dict:
        """Get relationship between two factions."""
        # Ensure consistent ordering (smaller UUID first)
        if str(faction_a_id) > str(faction_b_id):
            faction_a_id, faction_b_id = faction_b_id, faction_a_id
        
        relationship_file = f"{faction_a_id}_{faction_b_id}.json"
        relationship_path = os.path.join(self.relations_dir, relationship_file)
        
        if not os.path.exists(relationship_path):
            # Return default relationship
            return {
                "faction_a_id": faction_a_id,
                "faction_b_id": faction_b_id,
                "status": DiplomaticStatus.NEUTRAL,
                "trust_level": 50,
                "tension_level": 0,
                "last_interaction": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        
        with open(relationship_path, "r") as f:
            return json.load(f)
    
    def update_faction_relationship(
        self, 
        faction_a_id: UUID, 
        faction_b_id: UUID, 
        updates: Dict
    ) -> Dict:
        """Update relationship between two factions."""
        # Ensure consistent ordering
        if str(faction_a_id) > str(faction_b_id):
            faction_a_id, faction_b_id = faction_b_id, faction_a_id
        
        relationship = self.get_faction_relationship(faction_a_id, faction_b_id)
        
        # Update fields
        for key, value in updates.items():
            relationship[key] = value
        
        relationship["updated_at"] = datetime.utcnow().isoformat()
        relationship["last_interaction"] = datetime.utcnow().isoformat()
        
        # Save updated relationship
        relationship_file = f"{faction_a_id}_{faction_b_id}.json"
        relationship_path = os.path.join(self.relations_dir, relationship_file)
        
        with open(relationship_path, "w") as f:
            json.dump(relationship, f, default=str, indent=2)
        
        return relationship
    
    def get_all_faction_relationships(self, faction_id: UUID) -> List[Dict]:
        """Get all relationships for a faction."""
        relationships = []
        
        for filename in os.listdir(self.relations_dir):
            if not filename.endswith(".json"):
                continue
            
            # Extract faction IDs from filename
            parts = filename.replace(".json", "").split("_")
            if len(parts) != 2:
                continue
            
            try:
                file_faction_a = UUID(parts[0])
                file_faction_b = UUID(parts[1])
            except ValueError:
                continue
            
            # Check if this relationship involves our faction
            if faction_id in [file_faction_a, file_faction_b]:
                relationship_path = os.path.join(self.relations_dir, filename)
                with open(relationship_path, "r") as f:
                    relationship = json.load(f)
                
                # Add the other faction ID
                other_faction_id = file_faction_b if file_faction_a == faction_id else file_faction_a
                relationship["other_faction_id"] = str(other_faction_id)
                
                relationships.append(relationship)
        
        return relationships

    # Treaty violation methods
    
    def create_violation(self, violation: TreatyViolation) -> TreatyViolation:
        """Create a new treaty violation."""
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
            
            # Filter by faction (as violator or reporter)
            if faction_id and violation.violator_id != faction_id and violation.reported_by != faction_id:
                continue
            
            # Filter by violation type
            if violation_type and violation.violation_type != violation_type:
                continue
            
            # Filter by resolution status
            if resolved is not None and violation.resolved != resolved:
                continue
            
            violations.append(violation)
        
        return violations

    # Ultimatum methods
    
    def create_ultimatum(self, ultimatum: dict) -> Ultimatum:
        """Create a new ultimatum."""
        # Load existing ultimatums
        ultimatums = self._load_ultimatums()
        
        # Generate new ID if not provided
        if "id" not in ultimatum:
            ultimatum["id"] = str(uuid4())
        
        # Set default values
        ultimatum.setdefault("status", UltimatumStatus.PENDING.value)
        ultimatum.setdefault("issue_date", datetime.utcnow().isoformat())
        ultimatum.setdefault("public", True)
        ultimatum.setdefault("witnessed_by", [])
        ultimatum.setdefault("tension_change_on_issue", 20)
        ultimatum.setdefault("tension_change_on_accept", -10)
        ultimatum.setdefault("tension_change_on_reject", 40)
        
        # Convert UUIDs to strings for JSON serialization
        for key in ["issuer_id", "recipient_id", "related_incident_id", "related_treaty_id", "related_event_id"]:
            if key in ultimatum and ultimatum[key] is not None:
                ultimatum[key] = str(ultimatum[key])
        
        # Convert witnessed_by list
        if "witnessed_by" in ultimatum:
            ultimatum["witnessed_by"] = [str(wid) for wid in ultimatum["witnessed_by"]]
        
        # Convert deadline to string if it's a datetime
        if "deadline" in ultimatum and hasattr(ultimatum["deadline"], "isoformat"):
            ultimatum["deadline"] = ultimatum["deadline"].isoformat()
        
        # Add ultimatum to collection
        ultimatums[ultimatum["id"]] = ultimatum
        
        # Save ultimatums
        self._save_ultimatums(ultimatums)
        
        # Return as Ultimatum object
        return Ultimatum.parse_obj(ultimatum)
    
    def get_ultimatum(self, ultimatum_id: UUID) -> Optional[Ultimatum]:
        """Get an ultimatum by ID."""
        ultimatums = self._load_ultimatums()
        ultimatum_data = ultimatums.get(str(ultimatum_id))
        
        if not ultimatum_data:
            return None
        
        try:
            return Ultimatum.parse_obj(ultimatum_data)
        except Exception as e:
            print(f"Error parsing ultimatum {ultimatum_id}: {e}")
            return None
    
    def update_ultimatum(self, ultimatum_id: UUID, updates: dict) -> Optional[Ultimatum]:
        """Update an ultimatum with new values."""
        ultimatums = self._load_ultimatums()
        ultimatum_data = ultimatums.get(str(ultimatum_id))
        
        if not ultimatum_data:
            return None
        
        # Update fields
        for key, value in updates.items():
            if value is not None:
                # Convert UUIDs to strings
                if key in ["issuer_id", "recipient_id", "related_incident_id", "related_treaty_id", "related_event_id"] and value is not None:
                    value = str(value)
                elif key == "witnessed_by" and isinstance(value, list):
                    value = [str(wid) for wid in value]
                elif key in ["deadline", "response_date"] and hasattr(value, "isoformat"):
                    value = value.isoformat()
                elif key == "status" and hasattr(value, "value"):
                    value = value.value
                
                ultimatum_data[key] = value
        
        ultimatums[str(ultimatum_id)] = ultimatum_data
        self._save_ultimatums(ultimatums)
        
        try:
            return Ultimatum.parse_obj(ultimatum_data)
        except Exception as e:
            print(f"Error parsing updated ultimatum {ultimatum_id}: {e}")
            return None
    
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
        """List ultimatums, optionally filtered."""
        ultimatums = self._load_ultimatums()
        result = []
        
        for ultimatum_data in ultimatums.values():
            try:
                ultimatum = Ultimatum.parse_obj(ultimatum_data)
                
                # Filter by faction involvement
                if faction_id:
                    is_involved = False
                    if as_issuer and ultimatum.issuer_id == faction_id:
                        is_involved = True
                    if as_recipient and ultimatum.recipient_id == faction_id:
                        is_involved = True
                    
                    if not is_involved:
                        continue
                
                # Filter by status
                if status and ultimatum.status != status:
                    continue
                
                # Filter by active status
                if active_only:
                    active_statuses = [UltimatumStatus.PENDING, UltimatumStatus.UNDER_REVIEW]
                    if ultimatum.status not in active_statuses:
                        continue
                
                result.append(ultimatum)
                
            except Exception as e:
                print(f"Error parsing ultimatum data: {e}")
                continue
        
        # Sort by issue date (most recent first)
        result.sort(key=lambda u: u.issue_date, reverse=True)
        
        # Apply pagination
        return result[offset:offset + limit]
    
    def _load_ultimatums(self) -> Dict[str, dict]:
        """Load ultimatums from JSON file."""
        ultimatums_file = os.path.join(self.data_dir, "ultimatums.json")
        
        if not os.path.exists(ultimatums_file):
            return {}
        
        try:
            with open(ultimatums_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_ultimatums(self, ultimatums: Dict[str, dict]) -> None:
        """Save ultimatums to JSON file."""
        ultimatums_file = os.path.join(self.data_dir, "ultimatums.json")
        
        try:
            with open(ultimatums_file, "w") as f:
                json.dump(ultimatums, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving ultimatums: {e}")

    # Sanction methods
    
    def create_sanction(self, sanction: Sanction) -> Sanction:
        """Create a new sanction."""
        sanction_path = os.path.join(self.sanctions_dir, f"{sanction.id}.json")
        
        # Convert to dict and handle UUID serialization
        sanction_dict = sanction.dict()
        for key in ["imposer_id", "target_id"]:
            if sanction_dict[key]:
                sanction_dict[key] = str(sanction_dict[key])
        
        # Convert faction lists
        for key in ["supporting_factions", "opposing_factions"]:
            if sanction_dict[key]:
                sanction_dict[key] = [str(fid) for fid in sanction_dict[key]]
        
        with open(sanction_path, "w") as f:
            json.dump(sanction_dict, f, indent=2, default=str)
        
        return sanction
    
    def get_sanction(self, sanction_id: UUID) -> Optional[Sanction]:
        """Get a sanction by ID."""
        sanction_path = os.path.join(self.sanctions_dir, f"{sanction_id}.json")
        if not os.path.exists(sanction_path):
            return None
        
        try:
            with open(sanction_path, "r") as f:
                sanction_data = json.load(f)
            return Sanction.parse_obj(sanction_data)
        except Exception as e:
            print(f"Error loading sanction {sanction_id}: {e}")
            return None
    
    def update_sanction(self, sanction_id: UUID, updates: Dict) -> Optional[Sanction]:
        """Update a sanction with new values."""
        sanction = self.get_sanction(sanction_id)
        if not sanction:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(sanction, key) and value is not None:
                setattr(sanction, key, value)
        
        # Save updated sanction
        return self.create_sanction(sanction)
    
    def delete_sanction(self, sanction_id: UUID) -> bool:
        """Delete a sanction by ID."""
        sanction_path = os.path.join(self.sanctions_dir, f"{sanction_id}.json")
        if not os.path.exists(sanction_path):
            return False
        
        try:
            os.remove(sanction_path)
            return True
        except Exception:
            return False
    
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
        """List sanctions, optionally filtered."""
        sanctions = []
        
        try:
            for filename in os.listdir(self.sanctions_dir):
                if not filename.endswith(".json"):
                    continue
                
                sanction_path = os.path.join(self.sanctions_dir, filename)
                with open(sanction_path, "r") as f:
                    sanction_data = json.load(f)
                
                try:
                    sanction = Sanction.parse_obj(sanction_data)
                except Exception as e:
                    print(f"Error parsing sanction from {filename}: {e}")
                    continue
                
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
        
        except FileNotFoundError:
            pass  # Sanctions directory doesn't exist yet
        
        # Sort by imposed date (most recent first)
        sanctions.sort(key=lambda s: s.imposed_date, reverse=True)
        
        # Apply pagination
        return sanctions[offset:offset + limit]
    
    def record_sanction_violation(
        self,
        sanction_id: UUID,
        violation: Dict
    ) -> Optional[Sanction]:
        """Record a violation of a sanction."""
        sanction = self.get_sanction(sanction_id)
        if not sanction:
            return None
        
        # Add violation to the list
        if not sanction.violations:
            sanction.violations = []
        
        # Ensure violation has required fields
        violation.setdefault("timestamp", datetime.utcnow().isoformat())
        violation.setdefault("id", str(uuid4()))
        
        # Convert UUIDs to strings
        if "reported_by" in violation:
            violation["reported_by"] = str(violation["reported_by"])
        
        sanction.violations.append(violation)
        
        # Save updated sanction
        return self.create_sanction(sanction)

    # Diplomatic Incident methods
    
    def create_diplomatic_incident(self, incident_data: Dict) -> DiplomaticIncident:
        """Create a new diplomatic incident."""
        # Convert dict to DiplomaticIncident model
        incident = DiplomaticIncident(**incident_data)
        incident_path = os.path.join(self.data_dir, "incidents", f"{incident.id}.json")
        os.makedirs(os.path.dirname(incident_path), exist_ok=True)
        
        with open(incident_path, "w") as f:
            f.write(incident.json())
        return incident
    
    def get_diplomatic_incident(self, incident_id: UUID) -> Optional[DiplomaticIncident]:
        """Get a diplomatic incident by ID."""
        incident_path = os.path.join(self.data_dir, "incidents", f"{incident_id}.json")
        if not os.path.exists(incident_path):
            return None
        
        with open(incident_path, "r") as f:
            return DiplomaticIncident.parse_raw(f.read())
    
    def update_diplomatic_incident(self, incident_id: UUID, updates: Dict) -> Optional[DiplomaticIncident]:
        """Update a diplomatic incident with new values."""
        incident = self.get_diplomatic_incident(incident_id)
        if not incident:
            return None
        
        # Update fields
        for key, value in updates.items():
            if hasattr(incident, key):
                setattr(incident, key, value)
        
        # Save updated incident
        incident_path = os.path.join(self.data_dir, "incidents", f"{incident_id}.json")
        with open(incident_path, "w") as f:
            f.write(incident.json())
        
        return incident
    
    def list_diplomatic_incidents(
        self,
        faction_id: Optional[UUID] = None,
        as_perpetrator: bool = True,
        as_victim: bool = True,
        resolved: Optional[bool] = None,
        incident_type: Optional[DiplomaticIncidentType] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[DiplomaticIncident]:
        """List diplomatic incidents with optional filtering."""
        incidents = []
        incidents_dir = os.path.join(self.data_dir, "incidents")
        
        if not os.path.exists(incidents_dir):
            return incidents
        
        for filename in os.listdir(incidents_dir):
            if not filename.endswith(".json"):
                continue
            
            incident_path = os.path.join(incidents_dir, filename)
            with open(incident_path, "r") as f:
                incident = DiplomaticIncident.parse_raw(f.read())
            
            # Filter by faction involvement
            if faction_id:
                involved = False
                if as_perpetrator and incident.perpetrator_id == faction_id:
                    involved = True
                if as_victim and incident.victim_id == faction_id:
                    involved = True
                if not involved:
                    continue
            
            # Filter by resolution status
            if resolved is not None and incident.resolved != resolved:
                continue
            
            # Filter by incident type
            if incident_type and incident.incident_type != incident_type:
                continue
            
            incidents.append(incident)
        
        # Sort by timestamp (most recent first) and apply pagination
        incidents.sort(key=lambda x: x.timestamp, reverse=True)
        return incidents[offset:offset + limit]

    # Diplomatic Event methods
    
    def create_diplomatic_event(self, event_data: Dict) -> DiplomaticEvent:
        """Create a new diplomatic event."""
        # Convert dict to DiplomaticEvent model
        event = DiplomaticEvent(**event_data)
        event_path = os.path.join(self.events_dir, f"{event.id}.json")
        
        with open(event_path, "w") as f:
            f.write(event.json())
        return event

    # Event methods 