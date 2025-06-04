"""
Test NPC Barter Service

Tests for NPC bartering business logic.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4, UUID
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.systems.npc.services.npc_barter_service import (
    NPCBarterService,
    NPCBarterRules,
    ItemTier,
    BarterValidationResult,
    get_npc_barter_service
)

# Import models from infrastructure
from backend.infrastructure.systems.npc.models.models import NpcEntity
from backend.infrastructure.shared.exceptions import (
    NpcNotFoundError,
    NpcValidationError
)


class TestItemTier:
    """Test ItemTier enum"""
    
    def test_item_tier_values(self):
        """Test that ItemTier has correct values"""
        assert ItemTier.ALWAYS_AVAILABLE.value == "always_available"
        assert ItemTier.HIGH_PRICE_RELATIONSHIP.value == "high_price_relationship"
        assert ItemTier.NEVER_AVAILABLE.value == "never_available"


class TestBarterValidationResult:
    """Test BarterValidationResult class"""
    
    def test_validation_result_creation(self):
        """Test creating validation results"""
        result = BarterValidationResult(True, "Test reason", ItemTier.ALWAYS_AVAILABLE)
        assert result.allowed is True
        assert result.reason == "Test reason"
        assert result.tier == ItemTier.ALWAYS_AVAILABLE
        
    def test_validation_result_defaults(self):
        """Test validation result with defaults"""
        result = BarterValidationResult(False)
        assert result.allowed is False
        assert result.reason == ""
        assert result.tier is None


class TestNPCBarterRules:
    """Test NPCBarterRules class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.npc = Mock(spec=NpcEntity)
        self.npc.id = uuid4()
        self.npc.name = "Test NPC"
        self.npc.tags = ["guard"]
        self.npc.properties = {"profession": "guard"}
        self.npc.charisma = 12
        self.npc.hidden_pragmatism = 0
        
    def test_can_sell_equipped_item(self):
        """Test that equipped items cannot be sold"""
        item = {"is_equipped": True, "name": "Sword"}
        result = NPCBarterRules.can_sell_item(self.npc, item)
        
        assert result.allowed is False
        assert "equipped" in result.reason.lower()
        assert result.tier == ItemTier.NEVER_AVAILABLE
        
    def test_can_sell_held_weapon(self):
        """Test that held weapons cannot be sold"""
        item = {"is_held_weapon": True, "name": "Bow"}
        result = NPCBarterRules.can_sell_item(self.npc, item)
        
        assert result.allowed is False
        assert "held weapon" in result.reason.lower()
        assert result.tier == ItemTier.NEVER_AVAILABLE
        
    def test_can_sell_essential_for_role(self):
        """Test that role-essential items cannot be sold"""
        item = {"essential_for_role": True, "name": "Badge"}
        result = NPCBarterRules.can_sell_item(self.npc, item)
        
        assert result.allowed is False
        assert "essential for npc's role" in result.reason.lower()
        assert result.tier == ItemTier.NEVER_AVAILABLE
        
    def test_can_sell_quest_critical(self):
        """Test that quest-critical items cannot be sold"""
        item = {"quest_critical": True, "name": "Key"}
        result = NPCBarterRules.can_sell_item(self.npc, item)
        
        assert result.allowed is False
        assert "quest-critical" in result.reason.lower()
        assert result.tier == ItemTier.NEVER_AVAILABLE
        
    def test_can_sell_soulbound(self):
        """Test that soulbound items cannot be sold"""
        item = {"soulbound": True, "name": "Heirloom"}
        result = NPCBarterRules.can_sell_item(self.npc, item)
        
        assert result.allowed is False
        assert "soulbound" in result.reason.lower()
        assert result.tier == ItemTier.NEVER_AVAILABLE
        
    def test_can_sell_high_value_insufficient_trust(self):
        """Test high value items require trust"""
        item = {"tier": "high_value", "name": "Diamond", "value": 500}
        result = NPCBarterRules.can_sell_item(self.npc, item, relationship_trust=0.3)
        
        assert result.allowed is False
        assert "trust" in result.reason.lower()
        assert result.tier == ItemTier.HIGH_PRICE_RELATIONSHIP
        
    def test_can_sell_high_value_sufficient_trust(self):
        """Test high value items with sufficient trust"""
        item = {"tier": "high_value", "name": "Diamond", "value": 500}
        result = NPCBarterRules.can_sell_item(self.npc, item, relationship_trust=0.7)
        
        assert result.allowed is True
        assert result.tier == ItemTier.HIGH_PRICE_RELATIONSHIP
        
    def test_can_sell_personal_item_insufficient_trust(self):
        """Test personal items require moderate trust"""
        item = {"item_type": "family_heirloom", "name": "Ring", "value": 50}
        result = NPCBarterRules.can_sell_item(self.npc, item, relationship_trust=0.2)
        
        assert result.allowed is False
        assert "trust" in result.reason.lower()
        assert result.tier == ItemTier.HIGH_PRICE_RELATIONSHIP
        
    def test_can_sell_personal_item_sufficient_trust(self):
        """Test personal items with sufficient trust"""
        item = {"item_type": "family_heirloom", "name": "Ring", "value": 50}
        result = NPCBarterRules.can_sell_item(self.npc, item, relationship_trust=0.5)
        
        assert result.allowed is True
        assert result.tier == ItemTier.HIGH_PRICE_RELATIONSHIP
        
    def test_can_sell_always_available_item(self):
        """Test always available items"""
        item = {"name": "Bread", "value": 1}
        result = NPCBarterRules.can_sell_item(self.npc, item)
        
        assert result.allowed is True
        assert result.tier == ItemTier.ALWAYS_AVAILABLE
        
    def test_is_role_essential_guard_badge(self):
        """Test guard badge is essential for guards"""
        item = {"item_type": "badge", "name": "Guard Badge"}
        result = NPCBarterRules._is_role_essential_item(self.npc, item)
        assert result is True
        
    def test_is_role_essential_guard_uniform(self):
        """Test guard uniform is essential for guards"""
        item = {"item_type": "uniform", "name": "Guard Uniform"}
        result = NPCBarterRules._is_role_essential_item(self.npc, item)
        assert result is True
        
    def test_is_role_essential_shopkeeper_keys(self):
        """Test shop keys are essential for merchants"""
        self.npc.tags = ["shopkeeper"]
        self.npc.properties = {"profession": "merchant"}
        item = {"item_type": "shop_keys", "name": "Shop Keys"}
        result = NPCBarterRules._is_role_essential_item(self.npc, item)
        assert result is True
        
    def test_is_role_essential_craftsman_tools(self):
        """Test primary tools are essential for craftsmen"""
        self.npc.tags = ["blacksmith"]
        item = {"item_type": "primary_tools", "name": "Hammer"}
        result = NPCBarterRules._is_role_essential_item(self.npc, item)
        assert result is True
        
    def test_is_not_role_essential(self):
        """Test non-essential items"""
        item = {"item_type": "food", "name": "Apple"}
        result = NPCBarterRules._is_role_essential_item(self.npc, item)
        assert result is False
        
    def test_calculate_barter_price_always_available(self):
        """Test price calculation for always available items"""
        price = NPCBarterRules.calculate_barter_price(
            100.0, self.npc, 0.5, ItemTier.ALWAYS_AVAILABLE
        )
        
        # Base price 100, relationship discount 10% (0.5 * 0.2), charisma +4% (12-10)*0.02
        expected = 100.0 * 0.9 * 1.04  # 93.6
        assert abs(price - expected) < 0.01
        
    def test_calculate_barter_price_high_value(self):
        """Test price calculation for high value items"""
        price = NPCBarterRules.calculate_barter_price(
            100.0, self.npc, 0.5, ItemTier.HIGH_PRICE_RELATIONSHIP
        )
        
        # Base price 100, tier multiplier 1.5, relationship discount 10%, charisma +4%
        expected = 100.0 * 1.5 * 0.9 * 1.04  # 140.4
        assert abs(price - expected) < 0.01
        
    def test_calculate_barter_price_pragmatic_npc(self):
        """Test price calculation with pragmatic NPC"""
        self.npc.hidden_pragmatism = 7
        price = NPCBarterRules.calculate_barter_price(
            100.0, self.npc, 0.0, ItemTier.ALWAYS_AVAILABLE
        )
        
        # Base price 100, no relationship discount, charisma +4%, pragmatism +10%
        expected = 100.0 * 1.04 * 1.1  # 114.4
        assert abs(price - expected) < 0.01
        
    def test_calculate_barter_price_minimum(self):
        """Test minimum price enforcement"""
        price = NPCBarterRules.calculate_barter_price(
            0.5, self.npc, 1.0, ItemTier.ALWAYS_AVAILABLE
        )
        assert price >= 1.0
        
    def test_calculate_barter_price_with_market_conditions(self):
        """Test price calculation with market conditions"""
        market_conditions = {"supply_demand_ratio": 1.2}
        price = NPCBarterRules.calculate_barter_price(
            100.0, self.npc, 0.0, ItemTier.ALWAYS_AVAILABLE, market_conditions
        )
        
        # Base price 100, charisma +4%, market conditions +20%
        expected = 100.0 * 1.04 * 1.2  # 124.8
        assert abs(price - expected) < 0.01


class TestNPCBarterService:
    """Test NPCBarterService class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.mock_npc_repository = Mock()
        
        # Create test NPC
        self.test_npc = Mock(spec=NpcEntity)
        self.test_npc.id = uuid4()
        self.test_npc.name = "Test Merchant"
        self.test_npc.tags = ["merchant"]
        self.test_npc.properties = {"profession": "shopkeeper"}
        self.test_npc.charisma = 14
        self.test_npc.hidden_pragmatism = 2
        self.test_npc.goodwill = 20
        self.test_npc.inventory = [
            {
                "id": "item1",
                "name": "Bread",
                "value": 2,
                "item_type": "food"
            },
            {
                "id": "item2", 
                "name": "Magic Sword",
                "value": 500,
                "tier": "high_value",
                "item_type": "weapon"
            },
            {
                "id": "item3",
                "name": "Shop Keys",
                "value": 10,
                "item_type": "shop_keys"
            }
        ]
        
    @patch('backend.systems.npc.services.npc_barter_service.get_db')
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    def test_service_initialization(self, mock_repo_class, mock_get_db):
        """Test service initialization"""
        mock_get_db.return_value = iter([self.mock_db])
        mock_repo_class.return_value = self.mock_npc_repository
        
        service = NPCBarterService()
        
        assert service.db == self.mock_db
        assert service.npc_repository == self.mock_npc_repository
        assert service.barter_rules is not None
        
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    def test_service_with_external_session(self, mock_repo_class):
        """Test service with external database session"""
        mock_repo_class.return_value = self.mock_npc_repository
        
        service = NPCBarterService(self.mock_db)
        
        assert service.db == self.mock_db
        assert service._is_external_session is True
        
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    async def test_get_tradeable_items_success(self, mock_repo_class):
        """Test getting tradeable items successfully"""
        mock_repo_class.return_value = self.mock_npc_repository
        self.mock_npc_repository.get_npc.return_value = self.test_npc
        
        service = NPCBarterService(self.mock_db)
        
        with patch.object(service, '_get_relationship_trust', return_value=0.5):
            result = await service.get_tradeable_items(self.test_npc.id, "character1")
            
        assert result["npc_id"] == str(self.test_npc.id)
        assert result["npc_name"] == self.test_npc.name
        assert result["relationship_trust"] == 0.5
        assert result["total_items"] == 3
        assert "always_available" in result["items"]
        assert "high_trust_required" in result["items"]
        assert "not_available" in result["items"]
        
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    async def test_get_tradeable_items_npc_not_found(self, mock_repo_class):
        """Test getting tradeable items when NPC not found"""
        mock_repo_class.return_value = self.mock_npc_repository
        self.mock_npc_repository.get_npc.return_value = None
        
        service = NPCBarterService(self.mock_db)
        
        with pytest.raises(NpcNotFoundError):
            await service.get_tradeable_items(uuid4(), "character1")
            
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    async def test_get_item_barter_price_success(self, mock_repo_class):
        """Test getting item barter price successfully"""
        mock_repo_class.return_value = self.mock_npc_repository
        self.mock_npc_repository.get_npc.return_value = self.test_npc
        
        service = NPCBarterService(self.mock_db)
        
        with patch.object(service, '_get_relationship_trust', return_value=0.5):
            result = await service.get_item_barter_price(
                self.test_npc.id, "item1", "character1"
            )
            
        assert result["item_id"] == "item1"
        assert result["can_trade"] is True
        assert result["price"] is not None
        assert result["base_value"] == 2
        assert "price_factors" in result
        
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    async def test_get_item_barter_price_item_not_found(self, mock_repo_class):
        """Test getting price for non-existent item"""
        mock_repo_class.return_value = self.mock_npc_repository
        self.mock_npc_repository.get_npc.return_value = self.test_npc
        
        service = NPCBarterService(self.mock_db)
        
        with pytest.raises(NpcValidationError):
            await service.get_item_barter_price(
                self.test_npc.id, "nonexistent", "character1"
            )
            
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    async def test_initiate_barter_success(self, mock_repo_class):
        """Test initiating barter successfully"""
        mock_repo_class.return_value = self.mock_npc_repository
        self.mock_npc_repository.get_npc.return_value = self.test_npc
        
        service = NPCBarterService(self.mock_db)
        
        offer_items = [{"name": "Gold", "value": 100}]
        request_items = [{"id": "item1", "name": "Bread"}]
        
        with patch.object(service, '_get_relationship_trust', return_value=0.5):
            result = await service.initiate_barter(
                self.test_npc.id, "character1", offer_items, request_items
            )
            
        assert result["npc_id"] == str(self.test_npc.id)
        assert result["character_id"] == "character1"
        assert "trade_acceptable" in result
        assert "value_ratio" in result
        assert "item_validations" in result
        assert "message" in result
        
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    async def test_complete_barter_success(self, mock_repo_class):
        """Test completing barter successfully"""
        mock_repo_class.return_value = self.mock_npc_repository
        self.mock_npc_repository.get_npc.return_value = self.test_npc
        
        service = NPCBarterService(self.mock_db)
        
        transaction_data = {
            "offer_items": [{"name": "Gold", "value": 100}],
            "request_items": [{"id": "item1", "name": "Bread"}],
            "total_request_value": 50
        }
        
        result = await service.complete_barter(
            self.test_npc.id, "character1", transaction_data
        )
        
        assert result["success"] is True
        assert result["npc_id"] == str(self.test_npc.id)
        assert result["character_id"] == "character1"
        assert "transaction_id" in result
        assert "relationship_improvement" in result
        assert "transaction_log" in result
        
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    async def test_get_relationship_trust_no_character(self, mock_repo_class):
        """Test relationship trust with no character"""
        service = NPCBarterService(self.mock_db)
        
        trust = await service._get_relationship_trust(self.test_npc, None)
        assert trust == 0.0
        
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    async def test_get_relationship_trust_with_character(self, mock_repo_class):
        """Test relationship trust calculation"""
        service = NPCBarterService(self.mock_db)
        
        trust = await service._get_relationship_trust(self.test_npc, "character1")
        
        # Base trust 0.3 + goodwill modifier (20-18)/18 * 0.3 = 0.3 + 0.033 = 0.333
        expected = 0.3 + (20 - 18) / 18 * 0.3
        assert abs(trust - expected) < 0.01
        
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    def test_generate_barter_message_very_pleased(self, mock_repo_class):
        """Test barter message generation - very pleased"""
        service = NPCBarterService(self.mock_db)
        
        message = service._generate_barter_message(self.test_npc, True, 1.0, 0.8)
        assert "very pleased" in message.lower()
        
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    def test_generate_barter_message_fair_trade(self, mock_repo_class):
        """Test barter message generation - fair trade"""
        service = NPCBarterService(self.mock_db)
        
        message = service._generate_barter_message(self.test_npc, True, 0.9, 0.8)
        assert "fair trade" in message.lower()
        
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    def test_generate_barter_message_reluctant(self, mock_repo_class):
        """Test barter message generation - reluctant"""
        service = NPCBarterService(self.mock_db)
        
        message = service._generate_barter_message(self.test_npc, True, 0.81, 0.8)
        assert "reluctant" in message.lower()
        
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    def test_generate_barter_message_insulting(self, mock_repo_class):
        """Test barter message generation - insulting offer"""
        service = NPCBarterService(self.mock_db)
        
        message = service._generate_barter_message(self.test_npc, False, 0.3, 0.8)
        assert "insulting" in message.lower()
        
    @patch('backend.systems.npc.services.npc_barter_service.NPCRepository')
    def test_generate_barter_message_need_more(self, mock_repo_class):
        """Test barter message generation - need more"""
        service = NPCBarterService(self.mock_db)
        
        message = service._generate_barter_message(self.test_npc, False, 0.6, 0.8)
        assert "more" in message.lower()


class TestFactoryFunction:
    """Test factory function"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
    
    @patch('backend.systems.npc.services.npc_barter_service.NPCBarterService')
    @patch('backend.systems.npc.services.npc_barter_service.get_db')
    def test_get_npc_barter_service(self, mock_get_db, mock_service_class):
        """Test factory function"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_get_db.return_value = iter([self.mock_db])
        
        result = get_npc_barter_service()
        
        # The function should be called with the result of Depends(get_db) 
        # which will be the actual db session from the dependency
        mock_service_class.assert_called_once()
        assert result == mock_service
        
    @patch('backend.systems.npc.services.npc_barter_service.NPCBarterService')
    def test_get_npc_barter_service_with_session(self, mock_service_class):
        """Test factory function with session"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_db = Mock()
        
        result = get_npc_barter_service(mock_db)
        
        mock_service_class.assert_called_once_with(mock_db)
        assert result == mock_service 