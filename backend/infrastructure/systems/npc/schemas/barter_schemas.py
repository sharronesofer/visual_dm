"""
NPC Bartering System Schemas

Request and response models for the Universal NPC Bartering System.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class BarterItemRequest(BaseModel):
    """Request model for items in barter transactions"""
    
    id: Optional[str] = Field(None, description="Item ID")
    name: Optional[str] = Field(None, description="Item name")
    quantity: int = Field(default=1, ge=1, description="Quantity of the item")
    value: float = Field(default=0, ge=0, description="Item value for offered items")
    
    model_config = ConfigDict(from_attributes=True)


class BarterInitiateRequest(BaseModel):
    """Request model for initiating a barter transaction"""
    
    character_id: str = Field(..., description="Character making the barter offer")
    offer_items: List[BarterItemRequest] = Field(..., description="Items the character is offering")
    request_items: List[BarterItemRequest] = Field(..., description="Items the character wants")
    
    model_config = ConfigDict(from_attributes=True)


class BarterCompleteRequest(BaseModel):
    """Request model for completing a barter transaction"""
    
    character_id: str = Field(..., description="Character completing the trade")
    transaction_data: Dict[str, Any] = Field(..., description="Validated transaction data")
    
    model_config = ConfigDict(from_attributes=True)


class BarterItemResponse(BaseModel):
    """Response model for tradeable items"""
    
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    value: float
    item_type: Optional[str] = None
    tier: str
    can_trade: bool
    reason: Optional[str] = None
    price: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)


class BarterInventoryResponse(BaseModel):
    """Response model for NPC's tradeable inventory"""
    
    npc_id: str
    npc_name: str
    relationship_trust: float
    total_items: int
    items: Dict[str, List[BarterItemResponse]] = Field(
        description="Items organized by availability tier"
    )
    
    model_config = ConfigDict(from_attributes=True)


class BarterPriceResponse(BaseModel):
    """Response model for item barter pricing"""
    
    item_id: str
    item_name: Optional[str] = None
    can_trade: bool
    price: Optional[float] = None
    base_value: Optional[float] = None
    tier: Optional[str] = None
    relationship_trust: Optional[float] = None
    reason: Optional[str] = None
    price_factors: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True)


class BarterValidationResponse(BaseModel):
    """Response model for item validation in barter"""
    
    item_id: str
    valid: bool
    reason: Optional[str] = None
    price: Optional[float] = None
    tier: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class BarterInitiateResponse(BaseModel):
    """Response model for barter initiation"""
    
    npc_id: str
    character_id: str
    trade_acceptable: bool
    value_ratio: float
    required_ratio: float
    total_offer_value: float
    total_request_value: float
    relationship_trust: float
    item_validations: List[BarterValidationResponse]
    message: str
    
    model_config = ConfigDict(from_attributes=True)


class BarterTransactionLog(BaseModel):
    """Transaction log for completed barter"""
    
    timestamp: str
    character_id: str
    items_given: List[Dict[str, Any]]
    items_received: List[Dict[str, Any]]
    value_exchanged: float
    
    model_config = ConfigDict(from_attributes=True)


class BarterCompleteResponse(BaseModel):
    """Response model for completed barter transaction"""
    
    success: bool
    transaction_id: str
    npc_id: str
    character_id: str
    relationship_improvement: float
    message: str
    transaction_log: BarterTransactionLog
    
    model_config = ConfigDict(from_attributes=True)


class BarterErrorResponse(BaseModel):
    """Response model for barter errors"""
    
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(from_attributes=True) 