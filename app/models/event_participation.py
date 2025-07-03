from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class EventParticipation(Base):
    __tablename__ = "event_participations"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_attending = Column(Boolean, nullable=False, default=True)  # True = participe, False = ne participe plus
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Contrainte unique pour éviter les doublons
    __table_args__ = (UniqueConstraint('event_id', 'user_id', name='unique_event_user'),)
    
    # Relations
    event = relationship("Event", back_populates="participations")
    user = relationship("User", back_populates="event_participations") 