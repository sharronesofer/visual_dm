"""
Tournament Economy Service - Manages dual currency tournament system.

This service handles tournament entry fees, prize distributions, and economic
controls for the hybrid gold/token tournament system.
"""

import logging
import json
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.infrastructure.config_loaders.economy_config_loader import get_economy_config

logger = logging.getLogger(__name__)

class TournamentEconomyService:
    """Service for managing tournament economy with dual currency support."""
    
    def __init__(self, db_session: Session = None):
        """Initialize the tournament economy service.
        
        Args:
            db_session: SQLAlchemy session for database operations
        """
        self.db_session = db_session
        self.config = get_economy_config()
        logger.info("TournamentEconomyService initialized")
    
    def calculate_entry_fee(self, tournament_type: str, player_level: int, 
                           region_id: Optional[str] = None, 
                           currency: str = "gold") -> Tuple[int, Dict[str, Any]]:
        """
        Calculate tournament entry fee based on type, level, and region.
        
        Args:
            tournament_type: Type of tournament (gold_only, token_only, mixed)
            player_level: Player's level
            region_id: Region where tournament is held
            currency: Currency type (gold or tokens)
            
        Returns:
            Tuple of (entry_fee, calculation_details)
        """
        try:
            tournament_config = self.config.get_tournament_config()
            entry_fees = tournament_config.get('entry_fees', {})
            
            # Get base fee for currency type
            if currency == "gold":
                base_fee = entry_fees.get('gold_entry_base', 100)
                level_multiplier = entry_fees.get('level_multiplier', 1.5)
            else:  # tokens
                base_fee = entry_fees.get('token_entry_base', 10)
                level_multiplier = entry_fees.get('token_level_multiplier', 1.2)
            
            # Calculate level-based fee
            level_fee = base_fee * (level_multiplier ** (player_level - 1))
            
            # Apply regional modifier
            regional_modifier = 1.0
            if region_id:
                regional_modifiers = tournament_config.get('regional_modifiers', {})
                # TODO: Determine region wealth level from region system
                region_type = "neutral_regions"  # Default
                modifier_data = regional_modifiers.get(region_type, {})
                regional_modifier = modifier_data.get('entry_fee_multiplier', 1.0)
            
            final_fee = int(level_fee * regional_modifier)
            
            calculation_details = {
                "base_fee": base_fee,
                "level_multiplier": level_multiplier,
                "level_fee": level_fee,
                "regional_modifier": regional_modifier,
                "final_fee": final_fee,
                "currency": currency,
                "tournament_type": tournament_type
            }
            
            return final_fee, calculation_details
            
        except Exception as e:
            logger.error(f"Error calculating entry fee: {str(e)}")
            return 100 if currency == "gold" else 10, {"error": str(e)}
    
    def create_tournament_prize_pool(self, participants: List[Dict[str, Any]], 
                                   tournament_type: str) -> Dict[str, Any]:
        """
        Create prize pool from participant entry fees.
        
        Args:
            participants: List of participant data with entry fees
            tournament_type: Type of tournament
            
        Returns:
            Prize pool information
        """
        try:
            tournament_config = self.config.get_tournament_config()
            economic_controls = tournament_config.get('economic_controls', {})
            house_edge = economic_controls.get('house_edge', 0.15)
            
            # Separate gold and token pools
            gold_pool = 0
            token_pool = 0
            gold_participants = []
            token_participants = []
            
            for participant in participants:
                entry_currency = participant.get('entry_currency', 'gold')
                entry_fee = participant.get('entry_fee', 0)
                
                if entry_currency == 'gold':
                    gold_pool += entry_fee
                    gold_participants.append(participant)
                else:  # tokens
                    token_pool += entry_fee
                    token_participants.append(participant)
            
            # Apply house edge (economic control)
            gold_prize_pool = int(gold_pool * (1 - house_edge))
            token_prize_pool = int(token_pool * (1 - house_edge))
            
            # Calculate prize distribution
            prize_distribution = tournament_config.get('prize_distribution', {})
            percentages = prize_distribution.get('percentages', [0.5, 0.3, 0.1, 0.05, 0.05])
            
            gold_prizes = [int(gold_prize_pool * pct) for pct in percentages]
            token_prizes = [int(token_prize_pool * pct) for pct in percentages]
            
            return {
                "total_participants": len(participants),
                "gold_participants": len(gold_participants),
                "token_participants": len(token_participants),
                "gold_pool": {
                    "total_collected": gold_pool,
                    "house_edge_amount": gold_pool - gold_prize_pool,
                    "prize_pool": gold_prize_pool,
                    "prizes": gold_prizes
                },
                "token_pool": {
                    "total_collected": token_pool,
                    "house_edge_amount": token_pool - token_prize_pool,
                    "prize_pool": token_prize_pool,
                    "prizes": token_prizes
                },
                "prize_distribution": percentages,
                "house_edge": house_edge
            }
            
        except Exception as e:
            logger.error(f"Error creating prize pool: {str(e)}")
            return {"error": str(e)}
    
    def distribute_tournament_prizes(self, winners: List[Dict[str, Any]], 
                                   prize_pool: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Distribute prizes to tournament winners based on entry type.
        
        Args:
            winners: List of winners in order (1st, 2nd, etc.)
            prize_pool: Prize pool information from create_tournament_prize_pool
            
        Returns:
            List of prize distribution results
        """
        try:
            results = []
            gold_prizes = prize_pool.get('gold_pool', {}).get('prizes', [])
            token_prizes = prize_pool.get('token_pool', {}).get('prizes', [])
            
            for i, winner in enumerate(winners):
                if i >= len(gold_prizes):  # No more prizes
                    break
                
                entry_currency = winner.get('entry_currency', 'gold')
                player_id = winner.get('player_id')
                position = i + 1
                
                prize_result = {
                    "player_id": player_id,
                    "position": position,
                    "entry_currency": entry_currency,
                    "prizes": {}
                }
                
                # Gold prizes (available to all)
                if gold_prizes[i] > 0:
                    prize_result["prizes"]["gold"] = gold_prizes[i]
                
                # Token prizes (only for token-entry participants)
                if entry_currency == "tokens" and token_prizes[i] > 0:
                    prize_result["prizes"]["tokens"] = token_prizes[i]
                
                results.append(prize_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error distributing prizes: {str(e)}")
            return [{"error": str(e)}]
    
    def calculate_economic_impact(self, tournament_result: Dict[str, Any], 
                                region_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate the economic impact of a tournament on the regional economy.
        
        Args:
            tournament_result: Complete tournament result data
            region_id: Region where tournament was held
            
        Returns:
            Economic impact analysis
        """
        try:
            prize_pool = tournament_result.get('prize_pool', {})
            
            # Gold circulation impact
            gold_collected = prize_pool.get('gold_pool', {}).get('total_collected', 0)
            gold_distributed = prize_pool.get('gold_pool', {}).get('prize_pool', 0)
            gold_removed = gold_collected - gold_distributed  # House edge
            
            # Token circulation impact
            token_collected = prize_pool.get('token_pool', {}).get('total_collected', 0)
            token_distributed = prize_pool.get('token_pool', {}).get('prize_pool', 0)
            token_removed = token_collected - token_distributed  # House edge
            
            # Economic effects
            net_gold_sink = gold_removed  # Gold removed from economy
            gold_redistribution = gold_distributed  # Gold moved between players
            
            impact = {
                "region_id": region_id,
                "tournament_date": datetime.utcnow().isoformat(),
                "gold_impact": {
                    "collected": gold_collected,
                    "distributed": gold_distributed,
                    "net_sink": net_gold_sink,
                    "redistribution": gold_redistribution
                },
                "token_impact": {
                    "collected": token_collected,
                    "distributed": token_distributed,
                    "net_sink": token_removed
                },
                "economic_effects": {
                    "inflation_pressure": -net_gold_sink * 0.001,  # Deflationary effect
                    "wealth_concentration": self._calculate_wealth_concentration(tournament_result),
                    "economic_activity": gold_collected + token_collected
                }
            }
            
            return impact
            
        except Exception as e:
            logger.error(f"Error calculating economic impact: {str(e)}")
            return {"error": str(e)}
    
    def validate_tournament_entry(self, player_data: Dict[str, Any], 
                                tournament_type: str, 
                                entry_currency: str) -> Tuple[bool, str]:
        """
        Validate if a player can enter a tournament.
        
        Args:
            player_data: Player information including currency balances
            tournament_type: Type of tournament
            entry_currency: Currency player wants to use for entry
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            tournament_config = self.config.get_tournament_config()
            tournament_types = tournament_config.get('tournament_types', {})
            
            # Check if tournament type exists
            if tournament_type not in tournament_types:
                return False, f"Invalid tournament type: {tournament_type}"
            
            tournament_info = tournament_types[tournament_type]
            
            # Check if entry currency is allowed
            allowed_currencies = tournament_info.get('entry_currencies', 
                                                   [tournament_info.get('entry_currency')])
            
            if entry_currency not in allowed_currencies:
                return False, f"Currency {entry_currency} not allowed for {tournament_type} tournaments"
            
            # Calculate required entry fee
            player_level = player_data.get('level', 1)
            region_id = player_data.get('region_id')
            
            entry_fee, _ = self.calculate_entry_fee(
                tournament_type, player_level, region_id, entry_currency
            )
            
            # Check if player has sufficient funds
            player_balance = player_data.get(f'{entry_currency}_balance', 0)
            if player_balance < entry_fee:
                return False, f"Insufficient {entry_currency}: need {entry_fee}, have {player_balance}"
            
            return True, "Entry validated"
            
        except Exception as e:
            logger.error(f"Error validating tournament entry: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    def _calculate_wealth_concentration(self, tournament_result: Dict[str, Any]) -> float:
        """Calculate wealth concentration metric from tournament results."""
        try:
            # Simple Gini-like coefficient for prize distribution
            prize_distributions = tournament_result.get('prize_distributions', [])
            if not prize_distributions:
                return 0.0
            
            total_prizes = sum(sum(p.get('prizes', {}).values()) for p in prize_distributions)
            if total_prizes == 0:
                return 0.0
            
            # Calculate concentration (higher = more concentrated)
            top_prize = max(sum(p.get('prizes', {}).values()) for p in prize_distributions)
            concentration = top_prize / total_prizes
            
            return min(concentration, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating wealth concentration: {str(e)}")
            return 0.0 