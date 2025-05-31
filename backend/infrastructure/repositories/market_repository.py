import functools
from typing import List, Optional, Type, TypeVar, Generic
from sqlalchemy.orm import Session
from backend.systems.market.models import MarketItem, TradeOffer, Transaction, PriceHistory
from backend.infrastructure.database.session import SessionLocal
import logging
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError

T = TypeVar('T')

logger = logging.getLogger("market_repository")

@contextmanager
def transactional_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Transaction failed: {e}")
        raise
    finally:
        db.close()

class ValidationError(Exception):
    pass

def validate_market_item(data: dict):
    if not data.get('name') or not isinstance(data['name'], str):
        raise ValidationError("MarketItem must have a valid name.")
    if not data.get('type') or not isinstance(data['type'], str):
        raise ValidationError("MarketItem must have a valid type.")
    # Add more rules as needed

def validate_trade_offer(data: dict):
    if not data.get('seller_id'):
        raise ValidationError("TradeOffer must have a seller_id.")
    if not data.get('item_id'):
        raise ValidationError("TradeOffer must have an item_id.")
    if data.get('quantity', 0) <= 0:
        raise ValidationError("TradeOffer quantity must be positive.")
    if data.get('price_per_unit', 0) < 0:
        raise ValidationError("TradeOffer price_per_unit must be non-negative.")
    # Add more rules as needed

def validate_transaction(data: dict):
    if not data.get('offer_id'):
        raise ValidationError("Transaction must have an offer_id.")
    if not data.get('buyer_id'):
        raise ValidationError("Transaction must have a buyer_id.")
    if not data.get('seller_id'):
        raise ValidationError("Transaction must have a seller_id.")
    if data.get('quantity', 0) <= 0:
        raise ValidationError("Transaction quantity must be positive.")
    # Add more rules as needed

def validate_price_history(data: dict):
    if not data.get('item_id'):
        raise ValidationError("PriceHistory must have an item_id.")
    # Add more rules as needed

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, db: Session, id: int) -> Optional[T]:
        return db.query(self.model).get(id)

    def get_all(self, db: Session) -> List[T]:
        return db.query(self.model).all()

    def create(self, db: Session, obj_in: dict) -> T:
        obj = self.model(**obj_in)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update(self, db: Session, id: int, obj_in: dict) -> Optional[T]:
        obj = db.query(self.model).get(id)
        if not obj:
            return None
        for key, value in obj_in.items():
            setattr(obj, key, value)
        db.commit()
        db.refresh(obj)
        return obj

    def delete(self, db: Session, id: int) -> bool:
        obj = db.query(self.model).get(id)
        if not obj:
            return False
        db.delete(obj)
        db.commit()
        return True

# MarketItem Repository
class MarketItemRepository(BaseRepository[MarketItem]):
    def __init__(self):
        super().__init__(MarketItem)

    def create(self, db: Session, obj_in: dict) -> MarketItem:
        try:
            validate_market_item(obj_in)
        except ValidationError as e:
            logger.error(f"Validation failed for MarketItem: {e}")
            raise
        return super().create(db, obj_in)

    def update(self, db: Session, id: int, obj_in: dict) -> Optional[MarketItem]:
        try:
            validate_market_item(obj_in)
        except ValidationError as e:
            logger.error(f"Validation failed for MarketItem update: {e}")
            raise
        return super().update(db, id, obj_in)

# TradeOffer Repository
class TradeOfferRepository(BaseRepository[TradeOffer]):
    def __init__(self):
        super().__init__(TradeOffer)

    def create(self, db: Session, obj_in: dict) -> TradeOffer:
        try:
            validate_trade_offer(obj_in)
        except ValidationError as e:
            logger.error(f"Validation failed for TradeOffer: {e}")
            raise
        return super().create(db, obj_in)

    def update(self, db: Session, id: int, obj_in: dict) -> Optional[TradeOffer]:
        try:
            validate_trade_offer(obj_in)
        except ValidationError as e:
            logger.error(f"Validation failed for TradeOffer update: {e}")
            raise
        return super().update(db, id, obj_in)

# Transaction Repository
class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self):
        super().__init__(Transaction)

    def create(self, db: Session, obj_in: dict) -> Transaction:
        try:
            validate_transaction(obj_in)
        except ValidationError as e:
            logger.error(f"Validation failed for Transaction: {e}")
            raise
        return super().create(db, obj_in)

    def update(self, db: Session, id: int, obj_in: dict) -> Optional[Transaction]:
        try:
            validate_transaction(obj_in)
        except ValidationError as e:
            logger.error(f"Validation failed for Transaction update: {e}")
            raise
        return super().update(db, id, obj_in)

# PriceHistory Repository
class PriceHistoryRepository(BaseRepository[PriceHistory]):
    def __init__(self):
        super().__init__(PriceHistory)

    def create(self, db: Session, obj_in: dict) -> PriceHistory:
        try:
            validate_price_history(obj_in)
        except ValidationError as e:
            logger.error(f"Validation failed for PriceHistory: {e}")
            raise
        return super().create(db, obj_in)

    def update(self, db: Session, id: int, obj_in: dict) -> Optional[PriceHistory]:
        try:
            validate_price_history(obj_in)
        except ValidationError as e:
            logger.error(f"Validation failed for PriceHistory update: {e}")
            raise
        return super().update(db, id, obj_in)

# Example usage with caching (simple in-memory, not for production)
class CachedMarketItemRepository(MarketItemRepository):
    @functools.lru_cache(maxsize=128)
    def cached_get_by_id(self, id: int) -> Optional[MarketItem]:
        with SessionLocal() as db:
            return self.get_by_id(db, id)

    @functools.lru_cache(maxsize=1)
    def cached_get_all(self) -> List[MarketItem]:
        with SessionLocal() as db:
            return self.get_all(db) 