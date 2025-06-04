"""
Resource Service - Enhanced with rich production mechanics

This service manages resources with complex production requirements,
processing chains, storage mechanics, and trade effects.
"""

import logging
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from sqlalchemy.orm import Session

from backend.systems.economy.services.resource import (
    Resource, ResourceData, ResourceManager, ResourceCategory,
    ProductionRequirements, ProcessingOption
)
from backend.infrastructure.database.economy.resource_models import ResourceEntity
from backend.infrastructure.config_loaders.economy_config_loader import get_economy_config

logger = logging.getLogger(__name__)


class ResourceService:
    """Service for managing resources with rich production mechanics"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.resource_manager = ResourceManager()
        self._load_resource_configurations()
    
    def _load_resource_configurations(self) -> None:
        """Load resource configurations from JSON files"""
        try:
            # Load resource types configuration
            config_path = Path("data/systems/economy/resource_types.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    resource_config = json.load(f)
                    self.resource_manager.load_resource_config(resource_config)
                    logger.info(f"Loaded {len(resource_config.get('resources', {}))} resource configurations")
            else:
                logger.warning(f"Resource configuration not found at {config_path}")
                
        except Exception as e:
            logger.error(f"Error loading resource configurations: {e}")
    
    def create_resource_from_config(self, resource_type: str, quantity: int = 1, 
                                  region_id: str = "") -> ResourceData:
        """Create a resource instance from configuration"""
        try:
            resource = self.resource_manager.create_resource_from_config(
                resource_type, quantity, region_id
            )
            
            # Persist to database
            self._save_resource_to_db(resource)
            
            logger.info(f"Created {quantity} {resource_type} in region {region_id}")
            return resource
            
        except Exception as e:
            logger.error(f"Error creating resource from config: {e}")
            raise
    
    def _save_resource_to_db(self, resource: ResourceData) -> None:
        """Save resource data to database"""
        try:
            # Convert rich resource data to database entity
            entity = ResourceEntity(
                id=resource.id,
                name=resource.name,
                resource_type=resource.category.value,
                quantity=resource.quantity,
                base_price=resource.base_value,
                current_price=resource.current_price,
                region_id=resource.region_id,
                metadata={
                    'weight': resource.weight,
                    'volume': resource.volume,
                    'description': resource.description,
                    'rarity_level': resource.rarity_level,
                    'production_requirements': resource.production_requirements.__dict__,
                    'processing_options': {
                        name: option.__dict__ 
                        for name, option in resource.processing_options.items()
                    },
                    'storage_decay': resource.storage_decay.rates,
                    'trade_modifiers': resource.trade_modifiers.modifiers,
                    'magical_properties': resource.magical_properties.__dict__ if resource.magical_properties else None,
                    'nutritional_value': resource.nutritional_value,
                    'population_sustenance': resource.population_sustenance,
                    'cultural_value': resource.cultural_value,
                    'status_symbol': resource.status_symbol,
                    **resource.metadata
                }
            )
            
            self.db.add(entity)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving resource to database: {e}")
            raise
    
    def get_resource(self, resource_id: str) -> Optional[ResourceData]:
        """Get a resource by ID"""
        try:
            # First check in-memory manager
            resource = self.resource_manager.get_resource(resource_id)
            if resource:
                return resource
            
            # Check database
            entity = self.db.query(ResourceEntity).filter(
                ResourceEntity.id == resource_id
            ).first()
            
            if entity:
                return self._entity_to_resource_data(entity)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting resource {resource_id}: {e}")
            return None
    
    def _entity_to_resource_data(self, entity: ResourceEntity) -> ResourceData:
        """Convert database entity to ResourceData"""
        metadata = entity.metadata or {}
        
        # Create basic resource
        resource = ResourceData(
            id=entity.id,
            name=entity.name,
            category=ResourceCategory(entity.resource_type),
            base_value=entity.base_price,
            current_price=entity.current_price,
            quantity=entity.quantity,
            region_id=entity.region_id,
            weight=metadata.get('weight', 1.0),
            volume=metadata.get('volume', 1.0),
            description=metadata.get('description', ''),
            rarity_level=metadata.get('rarity_level', 'common'),
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
        
        # Restore complex data from metadata
        if 'production_requirements' in metadata:
            prod_data = metadata['production_requirements']
            resource.production_requirements = ProductionRequirements(**prod_data)
        
        if 'processing_options' in metadata:
            for name, option_data in metadata['processing_options'].items():
                resource.processing_options[name] = ProcessingOption(**option_data)
        
        if 'storage_decay' in metadata:
            resource.storage_decay.rates = metadata['storage_decay']
        
        if 'trade_modifiers' in metadata:
            resource.trade_modifiers.modifiers = metadata['trade_modifiers']
        
        # Set special properties
        resource.nutritional_value = metadata.get('nutritional_value')
        resource.population_sustenance = metadata.get('population_sustenance')
        resource.cultural_value = metadata.get('cultural_value')
        resource.status_symbol = metadata.get('status_symbol', False)
        
        return resource
    
    def list_resources_by_category(self, category: ResourceCategory) -> List[ResourceData]:
        """List all resources in a category"""
        try:
            # Get from database
            entities = self.db.query(ResourceEntity).filter(
                ResourceEntity.resource_type == category.value
            ).all()
            
            return [self._entity_to_resource_data(entity) for entity in entities]
            
        except Exception as e:
            logger.error(f"Error listing resources by category {category}: {e}")
            return []
    
    def get_producible_resources_in_biome(self, biome_type: str) -> List[str]:
        """Get list of resource types that can be produced in a biome"""
        try:
            producible = []
            
            for resource_id, config in self.resource_manager.resource_configs.items():
                prod_req = config.get('production_requirements', {})
                required_biomes = prod_req.get('biome_types', [])
                
                if not required_biomes or biome_type in required_biomes:
                    producible.append(resource_id)
            
            return producible
            
        except Exception as e:
            logger.error(f"Error getting producible resources for biome {biome_type}: {e}")
            return []
    
    def calculate_production_feasibility(self, resource_type: str, region_id: str,
                                       available_tools: List[str] = None,
                                       season: str = "spring") -> Dict[str, Any]:
        """Calculate if and how efficiently a resource can be produced"""
        try:
            if resource_type not in self.resource_manager.resource_configs:
                return {"feasible": False, "reason": "Resource type not found"}
            
            config = self.resource_manager.resource_configs[resource_type]
            prod_req = config.get('production_requirements', {})
            
            result = {
                "feasible": True,
                "efficiency": 1.0,
                "requirements_met": {},
                "missing_requirements": [],
                "production_time": prod_req.get('time_to_harvest', 1)
            }
            
            # Check seasonal availability
            if prod_req.get('seasonal', False):
                required_seasons = prod_req.get('seasons', [])
                if season not in required_seasons:
                    result["feasible"] = False
                    result["reason"] = f"Not available in {season}, requires: {required_seasons}"
                    return result
                result["requirements_met"]["seasonal"] = True
            
            # Check tool requirements
            required_tools = prod_req.get('tools_required', [])
            available_tools = available_tools or []
            
            missing_tools = [tool for tool in required_tools if tool not in available_tools]
            if missing_tools:
                result["efficiency"] *= 0.5  # Can still produce but inefficiently
                result["missing_requirements"].extend(missing_tools)
            else:
                result["requirements_met"]["tools"] = True
            
            # Check infrastructure requirements
            infrastructure = prod_req.get('requires_infrastructure')
            if infrastructure:
                # Would need to check region's infrastructure here
                result["requirements_met"]["infrastructure"] = f"Requires {infrastructure}"
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating production feasibility: {e}")
            return {"feasible": False, "reason": f"Error: {e}"}
    
    def calculate_processing_options(self, resource: ResourceData) -> Dict[str, Dict[str, Any]]:
        """Calculate available processing options for a resource"""
        try:
            options = {}
            
            for proc_name, proc_option in resource.processing_options.items():
                processed_value = resource.calculate_processed_value(proc_name)
                profit_margin = processed_value - resource.current_price
                
                options[proc_name] = {
                    "processed_value": processed_value,
                    "profit_margin": profit_margin,
                    "profit_percentage": (profit_margin / resource.current_price) * 100,
                    "processing_time": proc_option.time,
                    "tools_required": proc_option.tools,
                    "skill_required": proc_option.skill_required,
                    "infrastructure_required": proc_option.infrastructure_required
                }
            
            return options
            
        except Exception as e:
            logger.error(f"Error calculating processing options: {e}")
            return {}
    
    def simulate_storage_decay(self, resource: ResourceData, storage_type: str, 
                             days: int) -> Dict[str, Any]:
        """Simulate storage decay over time"""
        try:
            initial_quantity = resource.quantity
            remaining_quantity = resource.calculate_decay_after_time(storage_type, days)
            
            return {
                "initial_quantity": initial_quantity,
                "remaining_quantity": remaining_quantity,
                "quantity_lost": initial_quantity - remaining_quantity,
                "decay_percentage": ((initial_quantity - remaining_quantity) / initial_quantity) * 100,
                "storage_type": storage_type,
                "days_stored": days
            }
            
        except Exception as e:
            logger.error(f"Error simulating storage decay: {e}")
            return {}
    
    def get_regional_price_analysis(self, resource: ResourceData, 
                                  region_types: List[str]) -> Dict[str, Dict[str, Any]]:
        """Analyze price variations across different region types"""
        try:
            analysis = {}
            base_price = resource.current_price
            
            for region_type in region_types:
                regional_price = resource.calculate_regional_price(region_type)
                price_difference = regional_price - base_price
                
                analysis[region_type] = {
                    "regional_price": regional_price,
                    "base_price": base_price,
                    "price_difference": price_difference,
                    "price_modifier": regional_price / base_price,
                    "profit_opportunity": price_difference > 0
                }
            
            # Find best and worst markets
            if analysis:
                best_market = max(analysis.items(), key=lambda x: x[1]["regional_price"])
                worst_market = min(analysis.items(), key=lambda x: x[1]["regional_price"])
                
                analysis["summary"] = {
                    "best_market": best_market[0],
                    "best_price": best_market[1]["regional_price"],
                    "worst_market": worst_market[0],
                    "worst_price": worst_market[1]["regional_price"],
                    "arbitrage_opportunity": best_market[1]["regional_price"] - worst_market[1]["regional_price"]
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing regional prices: {e}")
            return {}

    # Legacy compatibility methods
    def create_resource(self, name: str, resource_type: str, quantity: int, 
                       value: float, region_id: str = "") -> Resource:
        """Create a simple resource (backward compatibility)"""
        resource = Resource(
            id=str(len(self.resource_manager.resources) + 1),
            name=name,
            type=resource_type,
            value=value,
            quantity=quantity,
            region_id=region_id
        )
        
        # Convert to rich ResourceData and store
        rich_resource = resource.to_resource_data()
        self.resource_manager.add_resource(rich_resource)
        
        return resource
    
    def list_resources(self) -> List[Resource]:
        """List all resources (backward compatibility)"""
        rich_resources = self.resource_manager.list_resources()
        
        # Convert to simple Resource format
        simple_resources = []
        for rich_resource in rich_resources:
            simple_resource = Resource(
                id=rich_resource.id,
                name=rich_resource.name,
                type=rich_resource.category.value,
                value=rich_resource.current_price,
                quantity=rich_resource.quantity,
                region_id=rich_resource.region_id
            )
            simple_resources.append(simple_resource)
        
        return simple_resources

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
                if self.db:
                    self.db.add(resource)
                
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
            if self.db:
                self.db.commit()
                
            return results
            
        except Exception as e:
            if self.db:
                self.db.rollback()
            logger.error(f"Error calculating population impact on resources: {str(e)}")
            return {"error": str(e)} 