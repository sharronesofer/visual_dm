from typing import Dict, Any

class ResourceService:
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