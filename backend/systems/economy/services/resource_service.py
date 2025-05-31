from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ResourceService:
    def __init__(self, db_session=None):
        """Initialize the resource service.
        
        Args:
            db_session: SQLAlchemy session for database operations
        """
        self.db_session = db_session
        logger.info("ResourceService initialized")
    
    def get_resource(self, resource_id):
        """Get a resource by ID."""
        # Mock implementation for now
        from backend.systems.economy.resource import Resource
        return Resource(
            id=str(resource_id),
            name=f"Resource {resource_id}",
            type="general",
            value=10.0,
            quantity=100,
            amount=100.0
        )
    
    def get_resources_by_region(self, region_id):
        """Get all resources in a region."""
        # Mock implementation for now
        from backend.systems.economy.resource import Resource
        return [
            Resource(
                id="1",
                name="Food",
                type="food",
                value=5.0,
                quantity=50,
                amount=50.0,
                region_id=str(region_id)
            ),
            Resource(
                id="2", 
                name="Water",
                type="water",
                value=3.0,
                quantity=100,
                amount=100.0,
                region_id=str(region_id)
            )
        ]
    
    def create_resource(self, resource_data):
        """Create a new resource."""
        # Mock implementation for now
        from backend.systems.economy.resource import Resource
        if isinstance(resource_data, dict):
            return Resource(**resource_data)
        return resource_data
    
    def update_resource(self, resource_id, updates):
        """Update an existing resource."""
        resource = self.get_resource(resource_id)
        if resource:
            for key, value in updates.items():
                if hasattr(resource, key):
                    setattr(resource, key, value)
        return resource
    
    def delete_resource(self, resource_id):
        """Delete a resource."""
        # Mock implementation for now
        return True
    
    def adjust_resource_amount(self, resource_id, amount_change):
        """Adjust the amount of a resource."""
        resource = self.get_resource(resource_id)
        if resource:
            resource.amount += amount_change
        return resource
    
    def get_available_resources(self, region_id=None, resource_type=None):
        """Get available resources, optionally filtered."""
        if region_id:
            resources = self.get_resources_by_region(region_id)
        else:
            # Mock implementation for all resources
            resources = []
        
        if resource_type:
            resources = [r for r in resources if r.type == resource_type]
        
        return resources
    
    def transfer_resource(self, source_region_id, dest_region_id, resource_id, amount):
        """Transfer resources between regions."""
        # Mock implementation for now
        return True, "Transfer successful"

    def population_impact_on_resources(self, region_id: int, 
                                   previous_population: int, 
                                   current_population: int) -> Dict[str, Any]:
        """Calculate the impact of population changes on resources.
        
        Args:
            region_id: ID of the region
            previous_population: Previous population count
            current_population: Current population count
            
        Returns:
            Dictionary with results of population impact
        """
        try:
            # No change in population, no impact
            if previous_population == current_population:
                return {
                    "region_id": region_id,
                    "population_change": 0,
                    "message": "No population change to process"
                }
            
            # Calculate population change percentage
            if previous_population > 0:
                change_percentage = (current_population - previous_population) / previous_population
            else:
                change_percentage = 1.0  # 100% increase if previous was 0
                
            # Get resources for the region
            resources = self.get_resources_by_region(region_id)
            
            results = {
                "region_id": region_id,
                "previous_population": previous_population,
                "current_population": current_population,
                "population_change": current_population - previous_population,
                "change_percentage": change_percentage,
                "resource_changes": [],
                "events": []
            }
            
            # Define resource impact factors for population changes
            # Higher impact on resources like food and water
            impact_factors = {
                "food": 0.5,      # Food consumption strongly tied to population
                "water": 0.6,     # Water consumption strongly tied to population
                "housing": 0.4,   # Housing demand tied to population
                "luxury": 0.3,    # Luxury goods moderately tied to population
                "default": 0.2    # Default moderate impact for other resources
            }
            
            # Process each resource
            for resource in resources:
                resource_type = getattr(resource, 'type', 'default')
                impact_factor = impact_factors.get(resource_type, impact_factors["default"])
                
                # Calculate resource change based on population change
                # Population increase -> resource decrease and vice versa
                resource_change = -1 * resource.amount * change_percentage * impact_factor
                
                # Special case: For production resources, population increase can mean
                # more production (positive correlation)
                if resource_type in ["labor", "crafted"]:
                    # Reverse the change direction for production resources
                    resource_change = -resource_change
                
                # Apply change to resource
                original_amount = resource.amount
                resource.amount = max(0, resource.amount + resource_change)
                
                # Save the change
                if self.db_session:
                    self.db_session.add(resource)
                
                # Record the change
                results["resource_changes"].append({
                    "resource_id": resource.id,
                    "resource_name": getattr(resource, 'name', f"Resource {resource.id}"),
                    "resource_type": resource_type,
                    "previous_amount": original_amount,
                    "new_amount": resource.amount,
                    "change": resource_change
                })
                
                # Generate events for significant changes
                if abs(resource_change) > resource.amount * 0.2:  # More than 20% change
                    event_type = "depletion" if resource_change < 0 else "abundance"
                    results["events"].append({
                        "type": f"resource_{event_type}",
                        "region_id": region_id,
                        "resource_id": resource.id,
                        "resource_name": getattr(resource, 'name', f"Resource {resource.id}"),
                        "resource_type": resource_type,
                        "change": resource_change,
                        "cause": "population_change",
                        "description": f"Population change caused resource {event_type}"
                    })
            
            # Commit changes to database
            if self.db_session:
                self.db_session.commit()
                
            return results
            
        except Exception as e:
            if self.db_session:
                self.db_session.rollback()
            logger.error(f"Error calculating population impact on resources: {str(e)}")
            return {"error": str(e)} 