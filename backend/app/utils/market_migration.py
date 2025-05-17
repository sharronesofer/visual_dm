"""
market_migration.py

Script to migrate in-memory market data to the database using the repository pattern.

Usage:
    1. Populate the in-memory data structures below with your current market data.
    2. Run this script in the backend/app context:
        python utils/market_migration.py
    3. Review logs for migration status and errors.

This script is idempotent and will skip records that already exist in the database.
"""
import logging
from backend.app.repositories.market_repository import (
    MarketItemRepository, TradeOfferRepository, TransactionRepository, PriceHistoryRepository, transactional_session
)
from backend.app.models.market import MarketItem, TradeOffer, Transaction, PriceHistory
from sqlalchemy.exc import IntegrityError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("market_migration")

# Example in-memory data (replace with your actual data)
in_memory_market_items = [
    {"id": 1, "name": "Iron Ore", "type": "resource", "description": "Raw iron ore."},
    {"id": 2, "name": "Wheat", "type": "food", "description": "Basic food staple."},
]
in_memory_trade_offers = [
    {"id": 1, "seller_id": "user1", "item_id": 1, "quantity": 100, "price_per_unit": 5.0, "expires_at": "2024-12-31T23:59:59"},
]
in_memory_transactions = [
    {"id": 1, "offer_id": 1, "buyer_id": "user2", "seller_id": "user1", "quantity": 10, "price_per_unit": 5.0, "market_id": "central", "timestamp": "2024-06-01T12:00:00"},
]
in_memory_price_history = [
    {"id": 1, "item_id": 1, "average_price": 5.0, "min_price": 4.5, "max_price": 5.5, "volume": 100, "trend": 0.1, "last_update": "2024-06-01T12:00:00"},
]

def migrate():
    item_repo = MarketItemRepository()
    offer_repo = TradeOfferRepository()
    txn_repo = TransactionRepository()
    price_repo = PriceHistoryRepository()

    with transactional_session() as db:
        # Market Items
        for item in in_memory_market_items:
            if not item_repo.get_by_id(db, item["id"]):
                try:
                    item_repo.create(db, item)
                    logger.info(f"Inserted MarketItem: {item['name']}")
                except IntegrityError:
                    logger.warning(f"MarketItem already exists: {item['id']}")
                except Exception as e:
                    logger.error(f"Failed to insert MarketItem {item['id']}: {e}")
            else:
                logger.info(f"MarketItem already exists: {item['id']}")

        # Trade Offers
        for offer in in_memory_trade_offers:
            if not offer_repo.get_by_id(db, offer["id"]):
                try:
                    offer_repo.create(db, offer)
                    logger.info(f"Inserted TradeOffer: {offer['id']}")
                except IntegrityError:
                    logger.warning(f"TradeOffer already exists: {offer['id']}")
                except Exception as e:
                    logger.error(f"Failed to insert TradeOffer {offer['id']}: {e}")
            else:
                logger.info(f"TradeOffer already exists: {offer['id']}")

        # Transactions
        for txn in in_memory_transactions:
            if not txn_repo.get_by_id(db, txn["id"]):
                try:
                    txn_repo.create(db, txn)
                    logger.info(f"Inserted Transaction: {txn['id']}")
                except IntegrityError:
                    logger.warning(f"Transaction already exists: {txn['id']}")
                except Exception as e:
                    logger.error(f"Failed to insert Transaction {txn['id']}: {e}")
            else:
                logger.info(f"Transaction already exists: {txn['id']}")

        # Price History
        for ph in in_memory_price_history:
            if not price_repo.get_by_id(db, ph["id"]):
                try:
                    price_repo.create(db, ph)
                    logger.info(f"Inserted PriceHistory: {ph['id']}")
                except IntegrityError:
                    logger.warning(f"PriceHistory already exists: {ph['id']}")
                except Exception as e:
                    logger.error(f"Failed to insert PriceHistory {ph['id']}: {e}")
            else:
                logger.info(f"PriceHistory already exists: {ph['id']}")

if __name__ == "__main__":
    migrate() 