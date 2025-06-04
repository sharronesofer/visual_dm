"""
NPC Integration Service - Infrastructure Layer

Concrete implementation of NPC system integration for cross-system communication.
Provides NPC data, traits, wealth, movement, and creation capabilities
to other systems without creating direct dependencies.
"""

import logging
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

# Import from infrastructure database layer (not business layer to avoid circular deps)
try:
    from backend.infrastructure.database.npc.models import NPCEntity, NPCTraits
    from backend.infrastructure.database.npc.enums import NPCType, NPCStatus
except ImportError:
    # Fallback if NPC models not available
    NPCEntity = None
    NPCTraits = None
    NPCType = None
    NPCStatus = None

from backend.systems.economy.services.integration_interfaces import NPCSystemInterface

logger = logging.getLogger(__name__)


class ConcreteNPCSystemInterface(NPCSystemInterface):
    """Concrete implementation of NPC system interface"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_npc_traits(self, npc_id: UUID) -> Dict[str, float]:
        """Get NPC traits for behavioral analysis"""
        try:
            if not NPCEntity:
                logger.warning("NPC database models not available, using defaults")
                return {
                    'wanderlust': 0.5,
                    'entrepreneurial': 0.5,
                    'wealth_seeking': 0.5,
                    'risk_tolerance': 0.5,
                    'sociability': 0.5,
                    'loyalty': 0.5,
                    'ambition': 0.5,
                    'intelligence': 0.5
                }
            
            npc = self.db.query(NPCEntity).filter(
                NPCEntity.id == npc_id
            ).first()
            
            if not npc:
                return {}
            
            # Try to get traits from a separate traits table first
            if NPCTraits:
                traits_entity = self.db.query(NPCTraits).filter(
                    NPCTraits.npc_id == npc_id
                ).first()
                
                if traits_entity:
                    return {
                        'wanderlust': getattr(traits_entity, 'wanderlust', 0.5),
                        'entrepreneurial': getattr(traits_entity, 'entrepreneurial', 0.5),
                        'wealth_seeking': getattr(traits_entity, 'wealth_seeking', 0.5),
                        'risk_tolerance': getattr(traits_entity, 'risk_tolerance', 0.5),
                        'sociability': getattr(traits_entity, 'sociability', 0.5),
                        'loyalty': getattr(traits_entity, 'loyalty', 0.5),
                        'ambition': getattr(traits_entity, 'ambition', 0.5),
                        'intelligence': getattr(traits_entity, 'intelligence', 0.5)
                    }
            
            # Fallback: check if traits are stored in metadata
            metadata = getattr(npc, 'metadata', {}) or {}
            traits = metadata.get('traits', {})
            
            if traits:
                return {
                    'wanderlust': traits.get('wanderlust', 0.5),
                    'entrepreneurial': traits.get('entrepreneurial', 0.5),
                    'wealth_seeking': traits.get('wealth_seeking', 0.5),
                    'risk_tolerance': traits.get('risk_tolerance', 0.5),
                    'sociability': traits.get('sociability', 0.5),
                    'loyalty': traits.get('loyalty', 0.5),
                    'ambition': traits.get('ambition', 0.5),
                    'intelligence': traits.get('intelligence', 0.5)
                }
            
            # Last resort: generate reasonable defaults based on NPC type
            npc_type = getattr(npc, 'npc_type', 'civilian')
            return self._generate_default_traits(npc_type)
            
        except Exception as e:
            logger.error(f"Error getting NPC traits for {npc_id}: {e}")
            return {}
    
    def _generate_default_traits(self, npc_type: str) -> Dict[str, float]:
        """Generate default traits based on NPC type"""
        trait_profiles = {
            'merchant': {
                'wanderlust': 0.7,
                'entrepreneurial': 0.8,
                'wealth_seeking': 0.9,
                'risk_tolerance': 0.6,
                'sociability': 0.7,
                'loyalty': 0.5,
                'ambition': 0.8,
                'intelligence': 0.7
            },
            'trader': {
                'wanderlust': 0.8,
                'entrepreneurial': 0.7,
                'wealth_seeking': 0.8,
                'risk_tolerance': 0.7,
                'sociability': 0.6,
                'loyalty': 0.4,
                'ambition': 0.7,
                'intelligence': 0.6
            },
            'craftsman': {
                'wanderlust': 0.3,
                'entrepreneurial': 0.6,
                'wealth_seeking': 0.6,
                'risk_tolerance': 0.4,
                'sociability': 0.5,
                'loyalty': 0.7,
                'ambition': 0.5,
                'intelligence': 0.7
            },
            'farmer': {
                'wanderlust': 0.2,
                'entrepreneurial': 0.3,
                'wealth_seeking': 0.4,
                'risk_tolerance': 0.3,
                'sociability': 0.6,
                'loyalty': 0.8,
                'ambition': 0.3,
                'intelligence': 0.5
            },
            'noble': {
                'wanderlust': 0.4,
                'entrepreneurial': 0.5,
                'wealth_seeking': 0.7,
                'risk_tolerance': 0.3,
                'sociability': 0.8,
                'loyalty': 0.6,
                'ambition': 0.9,
                'intelligence': 0.8
            },
            'adventurer': {
                'wanderlust': 0.9,
                'entrepreneurial': 0.6,
                'wealth_seeking': 0.7,
                'risk_tolerance': 0.9,
                'sociability': 0.5,
                'loyalty': 0.4,
                'ambition': 0.8,
                'intelligence': 0.6
            },
            'default': {
                'wanderlust': 0.5,
                'entrepreneurial': 0.5,
                'wealth_seeking': 0.5,
                'risk_tolerance': 0.5,
                'sociability': 0.5,
                'loyalty': 0.5,
                'ambition': 0.5,
                'intelligence': 0.5
            }
        }
        
        return trait_profiles.get(npc_type, trait_profiles['default'])
    
    def get_npc_wealth(self, npc_id: UUID) -> float:
        """Get NPC current wealth"""
        try:
            if not NPCEntity:
                logger.warning("NPC database models not available, using default wealth")
                return 1000.0  # Default wealth
            
            npc = self.db.query(NPCEntity).filter(
                NPCEntity.id == npc_id
            ).first()
            
            if npc:
                # Check for direct wealth attribute
                if hasattr(npc, 'wealth'):
                    return float(getattr(npc, 'wealth', 1000.0))
                
                # Check metadata for wealth information
                metadata = getattr(npc, 'metadata', {}) or {}
                wealth = metadata.get('wealth', metadata.get('gold', 1000.0))
                return float(wealth)
            
            return 1000.0  # Default if NPC not found
            
        except Exception as e:
            logger.error(f"Error getting NPC wealth for {npc_id}: {e}")
            return 1000.0
    
    def get_npcs_in_region(self, region_id: str, trait_filters: Optional[Dict[str, float]] = None) -> List[UUID]:
        """Get NPCs in a region, optionally filtered by traits"""
        try:
            if not NPCEntity:
                logger.warning("NPC database models not available, returning empty list")
                return []
            
            # Get NPCs in the region
            npcs_query = self.db.query(NPCEntity).filter(
                NPCEntity.current_region_id == region_id
            )
            
            # Add status filter to exclude dead/inactive NPCs
            if hasattr(NPCEntity, 'status'):
                npcs_query = npcs_query.filter(
                    NPCEntity.status.in_(['active', 'available', 'traveling'])
                )
            
            npcs = npcs_query.all()
            
            if not trait_filters:
                return [npc.id for npc in npcs]
            
            # Filter by traits
            filtered_npcs = []
            for npc in npcs:
                npc_traits = self.get_npc_traits(npc.id)
                
                # Check if NPC meets all trait criteria
                meets_criteria = True
                for trait_name, min_value in trait_filters.items():
                    if trait_name in npc_traits:
                        if npc_traits[trait_name] < min_value:
                            meets_criteria = False
                            break
                
                if meets_criteria:
                    filtered_npcs.append(npc.id)
            
            return filtered_npcs
            
        except Exception as e:
            logger.error(f"Error getting NPCs in region {region_id}: {e}")
            return []
    
    def move_npc_to_region(self, npc_id: UUID, region_id: str, reason: str = "") -> bool:
        """Move an NPC to a different region"""
        try:
            if not NPCEntity:
                logger.warning("NPC database models not available, cannot move NPC")
                return False
            
            npc = self.db.query(NPCEntity).filter(
                NPCEntity.id == npc_id
            ).first()
            
            if npc:
                # Update current region
                if hasattr(npc, 'current_region_id'):
                    npc.current_region_id = region_id
                
                # Add movement record to metadata
                metadata = getattr(npc, 'metadata', {}) or {}
                movement_history = metadata.get('movement_history', [])
                
                movement_history.append({
                    'from_region': getattr(npc, 'previous_region_id', 'unknown'),
                    'to_region': region_id,
                    'reason': reason,
                    'timestamp': str(datetime.utcnow())
                })
                
                # Keep only last 10 movements
                if len(movement_history) > 10:
                    movement_history = movement_history[-10:]
                
                metadata['movement_history'] = movement_history
                
                if hasattr(npc, 'metadata'):
                    npc.metadata = metadata
                
                # Update previous region reference
                if hasattr(npc, 'previous_region_id'):
                    npc.previous_region_id = npc.current_region_id
                
                self.db.commit()
                logger.info(f"Moved NPC {npc_id} to region {region_id} ({reason})")
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error moving NPC {npc_id} to region {region_id}: {e}")
            return False
    
    def create_wandering_npc(self, region_id: str, npc_type: str = "merchant") -> Optional[UUID]:
        """Create a new wandering NPC in the specified region"""
        try:
            if not NPCEntity:
                logger.warning("NPC database models not available, cannot create NPC")
                return None
            
            # Generate NPC data based on type
            npc_data = self._generate_npc_data(npc_type, region_id)
            
            # Create NPC entity
            new_npc = NPCEntity(
                id=uuid4(),
                name=npc_data['name'],
                npc_type=npc_type,
                current_region_id=region_id,
                status='active' if hasattr(NPCEntity, 'status') else None,
                wealth=npc_data['wealth'] if hasattr(NPCEntity, 'wealth') else None,
                metadata=npc_data['metadata']
            )
            
            self.db.add(new_npc)
            
            # Create traits if NPCTraits table exists
            if NPCTraits:
                traits = NPCTraits(
                    npc_id=new_npc.id,
                    **npc_data['traits']
                )
                self.db.add(traits)
            
            self.db.commit()
            
            logger.info(f"Created wandering {npc_type} {new_npc.id} in region {region_id}")
            return new_npc.id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating wandering NPC: {e}")
            return None
    
    def _generate_npc_data(self, npc_type: str, region_id: str) -> Dict[str, Any]:
        """Generate data for a new NPC"""
        import random
        
        # Name generators by type
        merchant_names = ["Aldric the Trader", "Mira Goldhand", "Gareth Coinwise", "Elena Silkweaver"]
        trader_names = ["Jorik Roadwalker", "Vera Swiftfoot", "Magnus Caravan", "Lyra Merchant"]
        opportunity_seeker_names = ["Finn Goldrush", "Sara Fortunehunter", "Drake Prospector", "Nora Seeker"]
        
        name_pools = {
            'merchant': merchant_names,
            'trader': trader_names,
            'opportunity_seeker': opportunity_seeker_names
        }
        
        # Wealth ranges by type
        wealth_ranges = {
            'merchant': (1500, 3500),
            'trader': (800, 2000),
            'opportunity_seeker': (500, 1500),
            'craftsman': (300, 1200),
            'default': (500, 1500)
        }
        
        # Generate basic data
        name_pool = name_pools.get(npc_type, merchant_names)
        name = random.choice(name_pool)
        
        wealth_range = wealth_ranges.get(npc_type, wealth_ranges['default'])
        wealth = random.uniform(*wealth_range)
        
        # Generate traits based on type with some variation
        base_traits = self._generate_default_traits(npc_type)
        varied_traits = {}
        
        for trait_name, base_value in base_traits.items():
            # Add random variation of ±0.2
            variation = random.uniform(-0.2, 0.2)
            varied_traits[trait_name] = max(0.0, min(1.0, base_value + variation))
        
        metadata = {
            'created_as': 'wandering_npc',
            'creation_reason': f'{npc_type}_opportunity',
            'origin_region': region_id,
            'traits': varied_traits,  # Store in metadata as backup
            'wealth': wealth,  # Store in metadata as backup
            'equipment': self._generate_equipment(npc_type),
            'goals': self._generate_goals(npc_type)
        }
        
        return {
            'name': name,
            'wealth': wealth,
            'traits': varied_traits,
            'metadata': metadata
        }
    
    def _generate_equipment(self, npc_type: str) -> List[str]:
        """Generate equipment list for NPC type"""
        equipment_by_type = {
            'merchant': ['scales', 'ledger', 'coin_purse', 'merchant_clothes', 'cart'],
            'trader': ['travel_pack', 'map', 'trading_goods', 'walking_stick', 'horse'],
            'opportunity_seeker': ['prospecting_tools', 'travel_gear', 'basic_weapons', 'provisions'],
            'craftsman': ['crafting_tools', 'materials', 'workshop_key', 'guild_badge'],
            'default': ['basic_gear', 'traveling_clothes', 'small_purse']
        }
        
        return equipment_by_type.get(npc_type, equipment_by_type['default'])
    
    def _generate_goals(self, npc_type: str) -> List[str]:
        """Generate goals for NPC type"""
        goals_by_type = {
            'merchant': ['establish_trade_route', 'increase_profit_margins', 'expand_customer_base'],
            'trader': ['find_rare_goods', 'discover_new_markets', 'build_reputation'],
            'opportunity_seeker': ['strike_it_rich', 'find_valuable_resources', 'beat_competitors'],
            'craftsman': ['perfect_craft', 'find_rare_materials', 'establish_workshop'],
            'default': ['survive', 'find_opportunity', 'return_home']
        }
        
        return goals_by_type.get(npc_type, goals_by_type['default'])
    
    def update_npc_wealth(self, npc_id: UUID, wealth_change: float) -> bool:
        """Update NPC wealth by a delta amount"""
        try:
            if not NPCEntity:
                logger.warning("NPC database models not available, cannot update wealth")
                return False
            
            npc = self.db.query(NPCEntity).filter(
                NPCEntity.id == npc_id
            ).first()
            
            if npc:
                current_wealth = self.get_npc_wealth(npc_id)
                new_wealth = max(0, current_wealth + wealth_change)
                
                # Update wealth attribute if it exists
                if hasattr(npc, 'wealth'):
                    npc.wealth = new_wealth
                
                # Update metadata as backup
                metadata = getattr(npc, 'metadata', {}) or {}
                metadata['wealth'] = new_wealth
                
                # Track wealth changes
                wealth_history = metadata.get('wealth_history', [])
                wealth_history.append({
                    'change': wealth_change,
                    'new_total': new_wealth,
                    'timestamp': str(datetime.utcnow())
                })
                
                # Keep only last 20 wealth changes
                if len(wealth_history) > 20:
                    wealth_history = wealth_history[-20:]
                
                metadata['wealth_history'] = wealth_history
                
                if hasattr(npc, 'metadata'):
                    npc.metadata = metadata
                
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating NPC {npc_id} wealth: {e}")
            return False


class NPCIntegrationService:
    """Service for managing NPC integrations across systems"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.npc_interface = ConcreteNPCSystemInterface(db_session)
    
    def get_interface(self) -> NPCSystemInterface:
        """Get the NPC system interface"""
        return self.npc_interface
    
    def trigger_npc_economic_behavior(self, region_id: str, event_type: str) -> Dict[str, Any]:
        """Trigger NPCs to respond to economic events"""
        try:
            result = {
                'region_id': region_id,
                'event_type': event_type,
                'npcs_affected': [],
                'behaviors_triggered': []
            }
            
            # Get NPCs in the region
            npcs_in_region = self.npc_interface.get_npcs_in_region(region_id)
            
            for npc_id in npcs_in_region:
                npc_traits = self.npc_interface.get_npc_traits(npc_id)
                
                # Determine if NPC responds based on traits and event
                if self._should_npc_respond(npc_traits, event_type):
                    behavior = self._determine_npc_behavior(npc_traits, event_type)
                    
                    result['npcs_affected'].append({
                        'npc_id': str(npc_id),
                        'behavior': behavior
                    })
                    
                    if behavior not in result['behaviors_triggered']:
                        result['behaviors_triggered'].append(behavior)
            
            return result
            
        except Exception as e:
            logger.error(f"Error triggering NPC economic behavior: {e}")
            return {'error': str(e)}
    
    def _should_npc_respond(self, traits: Dict[str, float], event_type: str) -> bool:
        """Determine if NPC should respond to an economic event"""
        response_thresholds = {
            'price_increase': traits.get('wealth_seeking', 0.5) > 0.6,
            'resource_scarcity': traits.get('entrepreneurial', 0.5) > 0.5,
            'new_market': traits.get('wanderlust', 0.5) > 0.4,
            'competition': traits.get('risk_tolerance', 0.5) > 0.5,
            'opportunity': traits.get('ambition', 0.5) > 0.6
        }
        
        return response_thresholds.get(event_type, False)
    
    def _determine_npc_behavior(self, traits: Dict[str, float], event_type: str) -> str:
        """Determine what behavior NPC should exhibit"""
        if event_type == 'price_increase':
            if traits.get('entrepreneurial', 0.5) > 0.7:
                return 'increase_production'
            elif traits.get('wealth_seeking', 0.5) > 0.7:
                return 'hoard_resources'
            else:
                return 'adjust_prices'
        
        elif event_type == 'resource_scarcity':
            if traits.get('wanderlust', 0.5) > 0.6:
                return 'seek_new_sources'
            else:
                return 'ration_usage'
        
        elif event_type == 'new_market':
            if traits.get('risk_tolerance', 0.5) > 0.6:
                return 'enter_market'
            else:
                return 'observe_market'
        
        elif event_type == 'competition':
            if traits.get('ambition', 0.5) > 0.7:
                return 'compete_aggressively'
            else:
                return 'find_niche'
        
        return 'wait_and_see'


def create_npc_integration_service(db_session: Session) -> NPCIntegrationService:
    """Factory function to create NPC integration service"""
    return NPCIntegrationService(db_session) 