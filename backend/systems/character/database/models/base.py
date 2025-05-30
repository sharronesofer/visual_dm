from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid

# Define the declarative base
Base = declarative_base()

class TimestampMixin:
    \"\"\"Mixin for created_at and updated_at timestamps.\"\"\"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class UUIDMixin:
    \"\"\"Mixin for a primary key UUID column.\"\"\"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

# A common base model for all new system models to inherit from
class CoreBaseModel(Base, UUIDMixin, TimestampMixin):
    \"\"\"Base model for all tables, includes UUID id and timestamps.\"\"\"
    __abstract__ = True # To ensure this table itself is not created

    # Potential future common fields or methods can be added here 
