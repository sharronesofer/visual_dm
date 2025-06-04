"""
Central Bank Service - Economic control and gold circulation management.

This service implements federal reserve-like functions for managing the game's
economy including interest rates, taxation, loans, and economic events.
"""

import logging
import json
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.infrastructure.config_loaders.economy_config_loader import get_economy_config

logger = logging.getLogger(__name__)

class CentralBankService:
    """Service for managing economic controls and gold circulation."""
    
    def __init__(self, db_session: Session = None):
        """Initialize the central bank service.
        
        Args:
            db_session: SQLAlchemy session for database operations
        """
        self.db_session = db_session
        self.config = get_economy_config()
        self._current_economic_state = {
            "inflation_rate": 0.02,
            "base_interest_rate": 0.05,
            "active_events": [],
            "regional_tax_rates": {},
            "gold_reserves": 100000
        }
        logger.info("CentralBankService initialized")
    
    def calculate_interest_rate(self, region_id: Optional[str] = None,
                              loan_type: str = "personal_loan") -> float:
        """
        Calculate current interest rate for a region and loan type.
        
        Args:
            region_id: Region for rate calculation
            loan_type: Type of loan (personal_loan, business_loan, emergency_loan)
            
        Returns:
            Current interest rate as decimal (0.05 = 5%)
        """
        try:
            central_bank_config = self.config.get_central_bank_config()
            interest_config = central_bank_config.get('interest_rates', {})
            
            # Base rate
            base_rate = interest_config.get('base_interest_rate', 0.05)
            
            # Regional adjustment
            regional_adjustments = interest_config.get('regional_adjustments', {})
            # TODO: Determine region type from region system
            region_type = "neutral_regions"  # Default
            regional_modifier = regional_adjustments.get(region_type, 0.0)
            
            # Dynamic adjustment based on inflation
            dynamic_config = interest_config.get('dynamic_adjustment', {})
            inflation_response = dynamic_config.get('inflation_response', 0.02)
            current_inflation = self._current_economic_state.get('inflation_rate', 0.02)
            inflation_adjustment = current_inflation * inflation_response
            
            # Loan type modifier
            loan_config = central_bank_config.get('loan_system', {})
            loan_types = loan_config.get('loan_types', {})
            loan_info = loan_types.get(loan_type, {})
            loan_modifier = loan_info.get('interest_rate_modifier', 1.0)
            
            # Calculate final rate
            adjusted_rate = (base_rate + regional_modifier + inflation_adjustment) * loan_modifier
            
            # Apply limits
            max_rate = dynamic_config.get('max_rate', 0.15)
            min_rate = dynamic_config.get('min_rate', 0.01)
            final_rate = max(min_rate, min(max_rate, adjusted_rate))
            
            return final_rate
            
        except Exception as e:
            logger.error(f"Error calculating interest rate: {str(e)}")
            return 0.05  # Default 5%
    
    def calculate_tax_rate(self, region_id: Optional[str] = None,
                          tax_type: str = "default") -> float:
        """
        Calculate current tax rate for a region and tax type.
        
        Args:
            region_id: Region for tax calculation
            tax_type: Type of tax (default, transaction_tax, luxury_tax, etc.)
            
        Returns:
            Current tax rate as decimal (0.1 = 10%)
        """
        try:
            central_bank_config = self.config.get_central_bank_config()
            taxation_config = central_bank_config.get('taxation', {})
            
            if tax_type in taxation_config.get('tax_types', {}):
                # Specific tax type
                base_rate = taxation_config['tax_types'][tax_type]
            else:
                # Regional tax rate
                regional_rates = taxation_config.get('regional_tax_rates', {})
                # TODO: Determine region wealth level from region system
                region_type = "default"  # Default
                base_rate = regional_rates.get(region_type, 0.1)
            
            # Check for active economic events affecting taxes
            event_modifier = 0.0
            for event in self._current_economic_state.get('active_events', []):
                if event.get('type') == 'war_economy':
                    event_modifier += 0.1  # War tax
                elif event.get('type') == 'economic_disaster':
                    event_modifier += 0.05  # Emergency tax
            
            final_rate = base_rate + event_modifier
            return max(0.0, min(0.5, final_rate))  # Cap at 50%
            
        except Exception as e:
            logger.error(f"Error calculating tax rate: {str(e)}")
            return 0.1  # Default 10%
    
    def create_loan_offer(self, borrower_data: Dict[str, Any],
                         loan_amount: int, loan_type: str = "personal_loan",
                         region_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a loan offer for a borrower.
        
        Args:
            borrower_data: Borrower information (wealth, credit history, etc.)
            loan_amount: Requested loan amount
            loan_type: Type of loan
            region_id: Region for loan terms
            
        Returns:
            Loan offer details or rejection
        """
        try:
            central_bank_config = self.config.get_central_bank_config()
            loan_config = central_bank_config.get('loan_system', {})
            loan_terms = loan_config.get('loan_terms', {})
            loan_types = loan_config.get('loan_types', {})
            
            # Check loan type validity
            if loan_type not in loan_types:
                return {"approved": False, "reason": f"Invalid loan type: {loan_type}"}
            
            loan_type_config = loan_types[loan_type]
            max_amount = loan_type_config.get('max_amount', 1000)
            duration_days = loan_type_config.get('duration_days', 30)
            
            # Check amount limits
            if loan_amount > max_amount:
                return {
                    "approved": False,
                    "reason": f"Amount exceeds maximum for {loan_type}: {max_amount}"
                }
            
            # Calculate borrower's capacity
            borrower_wealth = borrower_data.get('total_wealth', 0)
            max_loan_ratio = loan_terms.get('max_loan_ratio', 2.0)
            max_borrowable = int(borrower_wealth * max_loan_ratio)
            
            if loan_amount > max_borrowable:
                return {
                    "approved": False,
                    "reason": f"Amount exceeds borrowing capacity: {max_borrowable}"
                }
            
            # Calculate terms
            interest_rate = self.calculate_interest_rate(region_id, loan_type)
            collateral_requirement = loan_terms.get('collateral_requirement', 0.5)
            required_collateral = int(loan_amount * collateral_requirement)
            
            # Calculate repayment
            total_interest = int(loan_amount * interest_rate * (duration_days / 365))
            total_repayment = loan_amount + total_interest
            
            return {
                "approved": True,
                "loan_id": f"loan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "principal": loan_amount,
                "interest_rate": interest_rate,
                "duration_days": duration_days,
                "total_interest": total_interest,
                "total_repayment": total_repayment,
                "required_collateral": required_collateral,
                "due_date": (datetime.utcnow() + timedelta(days=duration_days)).isoformat(),
                "terms": {
                    "late_payment_penalty": loan_terms.get('late_payment_penalty', 0.1),
                    "early_repayment_allowed": True,
                    "collateral_type": "gold_equivalent"
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating loan offer: {str(e)}")
            return {"approved": False, "reason": f"System error: {str(e)}"}
    
    def trigger_economic_event(self, event_type: str,
                             region_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Trigger an economic event affecting the regional economy.
        
        Args:
            event_type: Type of event (gold_rush, economic_disaster, etc.)
            region_id: Region to affect (None for global)
            
        Returns:
            Event details and effects
        """
        try:
            central_bank_config = self.config.get_central_bank_config()
            events_config = central_bank_config.get('economic_events', {})
            
            if event_type not in events_config:
                return {"success": False, "reason": f"Unknown event type: {event_type}"}
            
            event_config = events_config[event_type]
            duration_days = event_config.get('duration_days', 7)
            
            event = {
                "id": f"event_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                "type": event_type,
                "region_id": region_id,
                "start_date": datetime.utcnow().isoformat(),
                "end_date": (datetime.utcnow() + timedelta(days=duration_days)).isoformat(),
                "duration_days": duration_days,
                "effects": {},
                "active": True
            }
            
            # Apply event-specific effects
            if event_type == "gold_rush":
                event["effects"] = {
                    "gold_generation_multiplier": event_config.get('gold_generation_multiplier', 2.0),
                    "inflation_impact": event_config.get('inflation_impact', 0.15)
                }
                # Update economic state
                current_inflation = self._current_economic_state.get('inflation_rate', 0.02)
                self._current_economic_state['inflation_rate'] = current_inflation + 0.15
                
            elif event_type == "economic_disaster":
                event["effects"] = {
                    "gold_destruction_rate": event_config.get('gold_destruction_rate', 0.1),
                    "deflation_impact": event_config.get('deflation_impact', -0.1)
                }
                # Update economic state
                current_inflation = self._current_economic_state.get('inflation_rate', 0.02)
                self._current_economic_state['inflation_rate'] = max(0.0, current_inflation - 0.1)
                
            elif event_type == "festival_event":
                event["effects"] = {
                    "optional_donation_rate": event_config.get('optional_donation_rate', 0.05),
                    "community_benefit_multiplier": event_config.get('community_benefit_multiplier', 1.2)
                }
                
            elif event_type == "war_economy":
                event["effects"] = {
                    "emergency_tax_rate": event_config.get('emergency_tax_rate', 0.15),
                    "resource_price_multiplier": event_config.get('resource_price_multiplier', 1.5)
                }
            
            # Add to active events
            self._current_economic_state['active_events'].append(event)
            
            logger.info(f"Economic event triggered: {event_type} in region {region_id}")
            return {"success": True, "event": event}
            
        except Exception as e:
            logger.error(f"Error triggering economic event: {str(e)}")
            return {"success": False, "reason": f"System error: {str(e)}"}
    
    def manage_money_supply(self, target_inflation: float = 0.02) -> Dict[str, Any]:
        """
        Manage money supply to target inflation rate.
        
        Args:
            target_inflation: Target inflation rate
            
        Returns:
            Money supply management actions taken
        """
        try:
            central_bank_config = self.config.get_central_bank_config()
            money_supply_config = central_bank_config.get('money_supply_controls', {})
            
            current_inflation = self._current_economic_state.get('inflation_rate', 0.02)
            inflation_diff = current_inflation - target_inflation
            
            actions = []
            
            # Inflation targets
            inflation_targets = money_supply_config.get('inflation_targets', {})
            tolerance = inflation_targets.get('tolerance_range', 0.01)
            intervention_threshold = inflation_targets.get('intervention_threshold', 0.05)
            
            if abs(inflation_diff) > intervention_threshold:
                # Major intervention needed
                if inflation_diff > 0:  # Too much inflation
                    # Contractionary policy
                    actions.append({
                        "type": "interest_rate_increase",
                        "amount": min(0.02, inflation_diff * 0.5),
                        "reason": "Combat inflation"
                    })
                    actions.append({
                        "type": "gold_sink_activation",
                        "amount": int(self._current_economic_state.get('gold_reserves', 100000) * 0.1),
                        "reason": "Reduce money supply"
                    })
                else:  # Deflation
                    # Expansionary policy
                    actions.append({
                        "type": "interest_rate_decrease",
                        "amount": min(0.02, abs(inflation_diff) * 0.5),
                        "reason": "Stimulate economy"
                    })
                    actions.append({
                        "type": "gold_injection",
                        "amount": int(self._current_economic_state.get('gold_reserves', 100000) * 0.05),
                        "reason": "Increase money supply"
                    })
            
            elif abs(inflation_diff) > tolerance:
                # Minor adjustment
                if inflation_diff > 0:
                    actions.append({
                        "type": "minor_tightening",
                        "interest_adjustment": 0.005,
                        "reason": "Fine-tune inflation"
                    })
                else:
                    actions.append({
                        "type": "minor_easing",
                        "interest_adjustment": -0.005,
                        "reason": "Fine-tune inflation"
                    })
            
            # Apply actions
            for action in actions:
                if action["type"] == "interest_rate_increase":
                    current_rate = self._current_economic_state.get('base_interest_rate', 0.05)
                    self._current_economic_state['base_interest_rate'] = min(0.15, current_rate + action["amount"])
                elif action["type"] == "interest_rate_decrease":
                    current_rate = self._current_economic_state.get('base_interest_rate', 0.05)
                    self._current_economic_state['base_interest_rate'] = max(0.01, current_rate - action["amount"])
            
            return {
                "current_inflation": current_inflation,
                "target_inflation": target_inflation,
                "inflation_diff": inflation_diff,
                "actions_taken": actions,
                "new_base_rate": self._current_economic_state.get('base_interest_rate', 0.05)
            }
            
        except Exception as e:
            logger.error(f"Error managing money supply: {str(e)}")
            return {"error": str(e)}
    
    def get_economic_state(self) -> Dict[str, Any]:
        """Get current economic state information."""
        return self._current_economic_state.copy()
    
    def update_economic_state(self, updates: Dict[str, Any]) -> None:
        """Update economic state with new values."""
        self._current_economic_state.update(updates)
        logger.info(f"Economic state updated: {list(updates.keys())}") 