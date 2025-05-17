from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from app.core.database import db
from app.core.models.base import BaseModel

class POIState(BaseModel):
    __tablename__ = 'poi_states'

    poi_id = Column(Integer, ForeignKey('points_of_interest.id', ondelete='CASCADE'), nullable=False, index=True)
    state_data = Column(JSON, nullable=False)
    valid_from = Column(DateTime, nullable=False, default=datetime.utcnow)
    valid_to = Column(DateTime, nullable=True, index=True)
    version = Column(Integer, nullable=False, default=1)
    created_by = Column(String(100))

    poi = relationship('PointOfInterest', back_populates='states')
    transitions_from = relationship('POITransition', foreign_keys='POITransition.from_state_id', back_populates='from_state')
    transitions_to = relationship('POITransition', foreign_keys='POITransition.to_state_id', back_populates='to_state')
    histories = relationship('POIHistory', back_populates='state')

    __table_args__ = (
        db.Index('ix_poi_state_poiid_valid', 'poi_id', 'valid_from', 'valid_to'),
        db.Index('ix_poi_state_current', 'poi_id', postgresql_where=(valid_to == None)),
    )

class POITransition(BaseModel):
    __tablename__ = 'poi_transitions'

    poi_id = Column(Integer, ForeignKey('points_of_interest.id', ondelete='CASCADE'), nullable=False, index=True)
    from_state_id = Column(Integer, ForeignKey('poi_states.id'))
    to_state_id = Column(Integer, ForeignKey('poi_states.id'))
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON)
    triggered_by = Column(String(100))
    triggered_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    poi = relationship('PointOfInterest', back_populates='transitions')
    from_state = relationship('POIState', foreign_keys=[from_state_id], back_populates='transitions_from')
    to_state = relationship('POIState', foreign_keys=[to_state_id], back_populates='transitions_to')

    __table_args__ = (
        db.Index('ix_poi_transition_poiid', 'poi_id'),
        db.Index('ix_poi_transition_event_type', 'event_type'),
        db.Index('ix_poi_transition_triggered_at', 'triggered_at'),
    )

class POIHistory(BaseModel):
    __tablename__ = 'poi_histories'

    poi_id = Column(Integer, ForeignKey('points_of_interest.id', ondelete='CASCADE'), nullable=False, index=True)
    state_id = Column(Integer, ForeignKey('poi_states.id'))
    change_type = Column(String(50), nullable=False)  # e.g., 'insert', 'update', 'delete'
    changed_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    changed_by = Column(String(100))

    poi = relationship('PointOfInterest', back_populates='histories')
    state = relationship('POIState', back_populates='histories')

    __table_args__ = (
        db.Index('ix_poi_history_poiid', 'poi_id'),
        db.Index('ix_poi_history_changed_at', 'changed_at'),
    ) 