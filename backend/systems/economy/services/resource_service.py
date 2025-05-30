"""
Resource service for economy system.
Consolidated from resource_manager.py and other scattered implementations.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session

from backend.systems.economy.models import Resource, ResourceData
from app.core.logging import logger

class ResourceService:
    """Service for managing resources in the economy system."""
    
    def __init__(self, db_session: Session = None):
        """Initialize the resource service.
        
        Args:
            db_session: SQLAlchemy session for database operations
        """
        self.db_session = db_session
        self._resource_cache = {}
    
    def get_resource(self, resource_id: Union[str, int]) -> Optional[Resource]:
        """Get a resource by ID.
        
        Args:
            resource_id: ID of the resource
            
        Returns:
            Resource object if found, None otherwise
        """
        try:
            if isinstance(resource_id, str) and resource_id.isdigit():
                resource_id = int(resource_id)
                
            # Try to get from cache first
            if resource_id in self._resource_cache:
                return self._resource_cache[resource_id]
                
            # Get from database
            if self.db_session:
                resource = self.db_session.query(Resource).filter(Resource.id == resource_id).first()
                if resource:
                    self._resource_cache[resource_id] = resource
                return resource
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting resource: {str(e)}")
            return None
    
    def get_resources_by_region(self, region_id: int) -> List[Resource]:
        """Get all resources in a region.
        
        Args:
            region_id: ID of the region
            
        Returns:
            List of resources in the region
        """
        try:
            if self.db_session:
                return self.db_session.query(Resource).filter(Resource.region_id == region_id).all()
            return []
            
        except Exception as e:
            logger.error(f"Error getting resources by region: {str(e)}")
            return []
    
    def create_resource(self, resource_data: Union[Dict[str, Any], ResourceData]) -> Optional[Resource]:
        """Create a new resource.
        
        Args:
            resource_data: Resource data or dictionary
            
        Returns:
            Created resource if successful, None otherwise
        """
        try:
            if not self.db_session:
                logger.error("Database session not available")
                return None
                
            if isinstance(resource_data, dict):
                resource_data_obj = ResourceData(**resource_data)
            else:
                resource_data_obj = resource_data
                
            resource = Resource.from_data_model(resource_data_obj)
            self.db_session.add(resource)
            self.db_session.commit()
            
            # Update cache
            self._resource_cache[resource.id] = resource
            
            return resource
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error creating resource: {str(e)}")
            return None
    
    def update_resource(self, resource_id: int, updates: Dict[str, Any]) -> Optional[Resource]:
        """Update an existing resource.
        
        Args:
            resource_id: ID of the resource to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated resource if successful, None otherwise
        """
        try:
            if not self.db_session:
                logger.error("Database session not available")
                return None
                
            resource = self.get_resource(resource_id)
            if not resource:
                logger.error(f"Resource with ID {resource_id} not found")
                return None
                
            # Update fields
            for key, value in updates.items():
                if hasattr(resource, key):
                    setattr(resource, key, value)
            
            resource.updated_at = datetime.utcnow()
            self.db_session.commit()
            
            # Update cache
            self._resource_cache[resource.id] = resource
            
            return resource
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error updating resource: {str(e)}")
            return None
    
    def delete_resource(self, resource_id: int) -> bool:
        """Delete a resource.
        
        Args:
            resource_id: ID of the resource to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.db_session:
                logger.error("Database session not available")
                return False
                
            resource = self.get_resource(resource_id)
            if not resource:
                logger.error(f"Resource with ID {resource_id} not found")
                return False
                
            self.db_session.delete(resource)
            self.db_session.commit()
            
            # Remove from cache
            if resource_id in self._resource_cache:
                del self._resource_cache[resource_id]
                
            return True
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error deleting resource: {str(e)}")
            return False
    
    def adjust_resource_amount(self, resource_id: int, amount_change: float) -> Optional[Resource]:
        """Adjust the amount of a resource.
        
        Args:
            resource_id: ID of the resource
            amount_change: Amount to adjust (positive or negative)
            
        Returns:
            Updated resource if successful, None otherwise
        """
        try:
            resource = self.get_resource(resource_id)
            if not resource:
                logger.error(f"Resource with ID {resource_id} not found")
                return None
                
            # Adjust amount
            resource.amount += amount_change
            
            # Ensure amount is not negative
            if resource.amount < 0:
                resource.amount = 0
                
            if self.db_session:
                resource.updated_at = datetime.utcnow()
                self.db_session.commit()
                
                # Update cache
                self._resource_cache[resource.id] = resource
                
            return resource
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error adjusting resource amount: {str(e)}")
            return None
    
    def get_available_resources(self, region_id: Optional[int] = None, 
                               resource_type: Optional[str] = None) -> List[Resource]:
        """Get available resources, optionally filtered by region and type.
        
        Args:
            region_id: Optional region ID to filter by
            resource_type: Optional resource type to filter by
            
        Returns:
            List of resources matching the filters
        """
        try:
            if not self.db_session:
                logger.error("Database session not available")
                return []
                
            query = self.db_session.query(Resource).filter(Resource.amount > 0)
            
            if region_id:
                query = query.filter(Resource.region_id == region_id)
                
            if resource_type:
                query = query.filter(Resource.type == resource_type)
                
            return query.all()
            
        except Exception as e:
            logger.error(f"Error getting available resources: {str(e)}")
            return []
    
    def transfer_resource(self, 
                         source_region_id: int, 
                         dest_region_id: int,
                         resource_id: int,
                         amount: float) -> Tuple[bool, str]:
        """Transfer resources between regions.
        
        Args:
            source_region_id: Source region ID
            dest_region_id: Destination region ID
            resource_id: ID of the resource to transfer
            amount: Amount to transfer
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.db_session:
                return False, "Database session not available"
                
            # Get source resource
            source_resource = (self.db_session.query(Resource)
                              .filter(Resource.region_id == source_region_id)
                              .filter(Resource.id == resource_id)
                              .first())
            
            if not source_resource:
                return False, f"Resource {resource_id} not found in region {source_region_id}"
                
            # Check if enough resource exists
            if source_resource.amount < amount:
                return False, f"Not enough resource available (have {source_resource.amount}, need {amount})"
                
            # Get or create destination resource
            dest_resource = (self.db_session.query(Resource)
                            .filter(Resource.region_id == dest_region_id)
                            .filter(Resource.id == resource_id)
                            .first())
                            
            if not dest_resource:
                # Create new resource in destination
                dest_resource = Resource(
                    name=source_resource.name,
                    description=source_resource.description,
                    type=source_resource.type,
                    rarity=source_resource.rarity,
                    price=source_resource.price,
                    region_id=dest_region_id,
                    amount=0,
                    properties=source_resource.properties
                )
                self.db_session.add(dest_resource)
                
            # Transfer amount
            source_resource.amount -= amount
            dest_resource.amount += amount
            
            # Update timestamps
            now = datetime.utcnow()
            source_resource.updated_at = now
            dest_resource.updated_at = now
            
            self.db_session.commit()
            
            # Update cache
            self._resource_cache[source_resource.id] = source_resource
            self._resource_cache[dest_resource.id] = dest_resource
            
            return True, f"Successfully transferred {amount} units of resource {resource_id}"
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            error_msg = f"Error transferring resource: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def clear_cache(self) -> None:
        """Clear the resource cache."""
        self._resource_cache = {}
    
    def process_economic_event(self, event_type: str, region_id: int, 
                            affected_resources: Optional[List[str]] = None,
                            severity: float = 1.0) -> Dict[str, Any]:
        """Process an economic event and apply its effects to resources.
        
        Args:
            event_type: Type of event ('famine', 'war', 'harvest', 'boom', 'bust', etc.)
            region_id: ID of the affected region
            affected_resources: Optional list of specific resource IDs to affect
            severity: Severity of the event (0.1-10.0, with 1.0 being normal)
            
        Returns:
            Dictionary with results of the event processing
        """
        try:
            if severity <= 0:
                logger.error(f"Invalid severity: {severity}. Must be positive.")
                return {"error": "Invalid severity"}
            
            # Get resources for the region
            if affected_resources:
                resources = [r for r in self.get_resources_by_region(region_id) 
                           if str(r.id) in affected_resources]
            else:
                resources = self.get_resources_by_region(region_id)
            
            if not resources:
                logger.warning(f"No resources found for region {region_id}")
                return {"message": "No resources affected", "changes": []}
            
            # Define event effects
            event_effects = {
                "famine": {
                    "food": {"amount_multiplier": -0.5 * severity, "rarity_multiplier": 2.0 * severity},
                    "default": {"amount_multiplier": -0.2 * severity}
                },
                "war": {
                    "food": {"amount_multiplier": -0.3 * severity},
                    "gold": {"amount_multiplier": -0.4 * severity},
                    "default": {"amount_multiplier": -0.25 * severity}
                },
                "harvest": {
                    "food": {"amount_multiplier": 0.5 * severity},
                    "default": {"amount_multiplier": 0.1 * severity}
                },
                "boom": {
                    "default": {"amount_multiplier": 0.3 * severity}
                },
                "bust": {
                    "default": {"amount_multiplier": -0.3 * severity}
                },
                "disaster": {
                    "default": {"amount_multiplier": -0.6 * severity}
                },
                "discovery": {
                    "default": {"amount_multiplier": 0.4 * severity, "rarity_multiplier": 0.8}
                }
            }
            
            # Get effects for this event
            effects = event_effects.get(event_type, {"default": {"amount_multiplier": 0}})
            
            # Apply effects to resources
            changes = []
            
            for resource in resources:
                # Determine resource type
                resource_type = getattr(resource, 'type', 'default').lower()
                
                # Get effect for this resource type or use default
                effect = effects.get(resource_type, effects.get("default", {}))
                
                # Apply amount change if specified
                if "amount_multiplier" in effect:
                    current_amount = getattr(resource, 'amount', 0)
                    change_amount = current_amount * effect["amount_multiplier"]
                    
                    # Ensure we don't go below zero
                    new_amount = max(0, current_amount + change_amount)
                    
                    # Update resource
                    updates = {'amount': new_amount}
                    if hasattr(resource, 'last_event') and resource.last_event:
                        updates['last_event'] = event_type
                    
                    self.update_resource(resource.id, updates)
                    
                    changes.append({
                        "resource_id": resource.id,
                        "name": getattr(resource, 'name', f"Resource {resource.id}"),
                        "type": resource_type,
                        "previous_amount": current_amount,
                        "new_amount": new_amount,
                        "change": change_amount
                    })
                    
                # Apply rarity change if specified
                if "rarity_multiplier" in effect and hasattr(resource, 'rarity'):
                    current_rarity = resource.rarity
                    new_rarity = current_rarity * effect["rarity_multiplier"]
                    
                    # Update resource
                    self.update_resource(resource.id, {'rarity': new_rarity})
                    
                    # Add to changes if not already there
                    if not any(c["resource_id"] == resource.id for c in changes):
                        changes.append({
                            "resource_id": resource.id,
                            "name": getattr(resource, 'name', f"Resource {resource.id}"),
                            "type": resource_type,
                            "previous_rarity": current_rarity,
                            "new_rarity": new_rarity
                        })
                    else:
                        # Update existing entry
                        for change in changes:
                            if change["resource_id"] == resource.id:
                                change["previous_rarity"] = current_rarity
                                change["new_rarity"] = new_rarity
                                break
            
            return {
                "event_type": event_type,
                "region_id": region_id,
                "severity": severity,
                "affected_resources": len(changes),
                "changes": changes
            }
            
        except Exception as e:
            logger.error(f"Error processing economic event: {str(e)}")
            return {"error": str(e)}
    
    def simulate_resource_consumption(self, region_id: int, 
                                    population: int, 
                                    consumption_factors: Dict[str, float] = None) -> Dict[str, Any]:
        """Simulate resource consumption by population and activities.
        
        Args:
            region_id: ID of the region
            population: Current population size
            consumption_factors: Optional dictionary of resource type to consumption multiplier
                                (defaults will be used if not provided)
        
        Returns:
            Dictionary with consumption results
        """
        try:
            # Default consumption factors per 1000 population
            default_consumption = {
                "food": 5.0,       # 5 units of food per 1000 people
                "water": 10.0,     # 10 units of water per 1000 people
                "wood": 3.0,       # 3 units of wood per 1000 people
                "metal": 1.0,      # 1 unit of metal per 1000 people
                "luxury": 0.5,     # 0.5 units of luxury goods per 1000 people
                "fuel": 2.0        # 2 units of fuel per 1000 people
            }
            
            # Use provided factors or defaults
            factors = consumption_factors or default_consumption
            
            # Get resources in the region
            resources = self.get_resources_by_region(region_id)
            
            # Calculate population factor (per 1000)
            pop_factor = population / 1000.0
            
            results = {
                "region_id": region_id,
                "population": population,
                "resources_consumed": {},
                "shortages": [],
                "events": []
            }
            
            # Process consumption for each resource type
            for resource_type, base_consumption in factors.items():
                # Find resources of this type in the region
                type_resources = [r for r in resources if r.resource_type == resource_type]
                
                if not type_resources:
                    # No resources of this type in region
                    results["shortages"].append({
                        "resource_type": resource_type,
                        "severity": "critical",
                        "amount_needed": base_consumption * pop_factor,
                        "amount_available": 0
                    })
                    
                    # Generate shortage event
                    results["events"].append({
                        "type": "resource_shortage",
                        "region_id": region_id,
                        "resource_type": resource_type,
                        "severity": "critical",
                        "description": f"Critical shortage of {resource_type} in region {region_id}"
                    })
                    continue
                
                # Calculate total consumption for this resource type
                total_consumption = base_consumption * pop_factor
                
                # Track consumption across all resources of this type
                consumed = 0
                consumption_details = []
                
                # Try to consume from each resource of this type
                for resource in type_resources:
                    # How much we need to consume from this specific resource
                    needed = total_consumption - consumed
                    
                    if needed <= 0:
                        break  # We've already met our consumption needs
                        
                    # How much we can actually consume
                    consumable = min(needed, resource.amount)
                    
                    if consumable > 0:
                        # Update the resource
                        original_amount = resource.amount
                        resource.amount -= consumable
                        consumed += consumable
                        
                        # Save the resource
                        self.db_session.add(resource)
                        
                        # Track details
                        consumption_details.append({
                            "resource_id": resource.id,
                            "resource_name": resource.name,
                            "consumed": consumable,
                            "remaining": resource.amount
                        })
                        
                        # Check if resource is running low
                        if resource.amount < resource.minimum_viable_amount:
                            results["events"].append({
                                "type": "resource_low",
                                "region_id": region_id,
                                "resource_id": resource.id,
                                "resource_name": resource.name,
                                "amount": resource.amount,
                                "minimum_viable": resource.minimum_viable_amount,
                                "description": f"Resource {resource.name} running low in region {region_id}"
                            })
                
                # Record results for this resource type
                results["resources_consumed"][resource_type] = {
                    "total_consumed": consumed,
                    "total_needed": total_consumption,
                    "details": consumption_details
                }
                
                # Check for overall shortage
                if consumed < total_consumption:
                    shortage_amount = total_consumption - consumed
                    severity = "low"
                    
                    # Determine severity based on percentage of unfulfilled consumption
                    shortage_percentage = shortage_amount / total_consumption
                    if shortage_percentage > 0.5:
                        severity = "critical"
                    elif shortage_percentage > 0.2:
                        severity = "severe"
                    
                    results["shortages"].append({
                        "resource_type": resource_type,
                        "severity": severity,
                        "amount_needed": total_consumption,
                        "amount_available": consumed,
                        "shortage_amount": shortage_amount
                    })
                    
                    # Generate shortage event for significant shortages
                    if severity != "low":
                        results["events"].append({
                            "type": "resource_shortage",
                            "region_id": region_id,
                            "resource_type": resource_type,
                            "severity": severity,
                            "percentage": shortage_percentage,
                            "description": f"{severity.capitalize()} shortage of {resource_type} in region {region_id}"
                        })
            
            # Commit changes
            self.db_session.commit()
            
            return results
        
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error simulating resource consumption: {str(e)}")
            return {"error": str(e)}
    
    def simulate_production_activities(self, region_id: int, 
                                    production_capacity: Dict[str, float] = None) -> Dict[str, Any]:
        """Simulate resource production from various activities.
        
        Args:
            region_id: ID of the region
            production_capacity: Optional dictionary of resource type to production capacity
                               (defaults will be used if not provided)
        
        Returns:
            Dictionary with production results
        """
        try:
            # Default production capacities
            default_production = {
                "food": 4.0,      # Base food production
                "water": 8.0,     # Base water production
                "wood": 3.0,      # Base wood production
                "metal": 1.0,     # Base metal production
                "luxury": 0.5,    # Base luxury goods production
                "fuel": 1.5       # Base fuel production
            }
            
            # Use provided capacities or defaults
            capacities = production_capacity or default_production
            
            # Get existing resources in the region
            resources = self.get_resources_by_region(region_id)
            
            results = {
                "region_id": region_id,
                "resources_produced": {},
                "new_resources": [],
                "events": []
            }
            
            # Process production for each resource type
            for resource_type, base_production in capacities.items():
                # Find resources of this type in the region
                type_resources = [r for r in resources if r.resource_type == resource_type]
                
                # Apply production to existing resources or create new ones
                if type_resources:
                    # Distribute production among existing resources
                    production_per_resource = base_production / len(type_resources)
                    
                    for resource in type_resources:
                        original_amount = resource.amount
                        resource.amount += production_per_resource
                        
                        # Save changes
                        self.db_session.add(resource)
                        
                        # Track results
                        if resource_type not in results["resources_produced"]:
                            results["resources_produced"][resource_type] = []
                            
                        results["resources_produced"][resource_type].append({
                            "resource_id": resource.id,
                            "resource_name": resource.name,
                            "produced": production_per_resource,
                            "new_amount": resource.amount
                        })
                        
                        # Generate event for significant production
                        if production_per_resource > resource.minimum_viable_amount:
                            results["events"].append({
                                "type": "resource_production",
                                "region_id": region_id,
                                "resource_id": resource.id,
                                "resource_name": resource.name,
                                "amount_produced": production_per_resource,
                                "description": f"Significant {resource.name} production in region {region_id}"
                            })
                else:
                    # Create a new resource of this type
                    new_resource = ResourceData(
                        name=f"{resource_type.capitalize()} of Region {region_id}",
                        description=f"Natural {resource_type} resource in Region {region_id}",
                        resource_type=resource_type,
                        region_id=str(region_id),
                        amount=base_production,
                        rarity=0.5,  # Medium rarity
                        minimum_viable_amount=base_production * 0.2  # 20% of initial production
                    )
                    
                    # Create in database
                    created = self.create_resource(new_resource)
                    
                    if created:
                        # Track new resource
                        results["new_resources"].append({
                            "resource_id": created.id,
                            "resource_name": created.name,
                            "resource_type": resource_type,
                            "amount": created.amount
                        })
                        
                        # Generate discovery event
                        results["events"].append({
                            "type": "resource_discovery",
                            "region_id": region_id,
                            "resource_id": created.id,
                            "resource_name": created.name,
                            "resource_type": resource_type,
                            "amount": created.amount,
                            "description": f"New {resource_type} resource discovered in region {region_id}"
                        })
            
            # Commit changes
            self.db_session.commit()
            
            return results
        
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error simulating production activities: {str(e)}")
            return {"error": str(e)} 