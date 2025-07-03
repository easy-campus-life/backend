from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # catégorie
    attendance = Column(String(50), nullable=True)  # nombre de participants attendus
    place = Column(String(200), nullable=False)
    image_url = Column(String(500), nullable=True)  # URL de l'image de l'événement
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    participations = relationship("EventParticipation", back_populates="event")