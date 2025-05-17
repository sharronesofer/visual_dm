import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.app.models.base import Base
from backend.app.models.market import MarketItem, TradeOffer, Transaction, PriceHistory

target_metadata = Base.metadata
print('Alembic sees tables:', list(Base.metadata.tables.keys())) 