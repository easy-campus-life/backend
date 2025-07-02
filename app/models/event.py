from sqlalchemy import Column, Integer, String, Text, Date, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(200), nullable=False)
    desc = Column(Text, nullable=True)
    cat = Column(String(100), nullable=False)  # catégorie
    attendance = Column(String(50), nullable=True)  # nombre de participants attendus
    lieu = Column(String(200), nullable=False)
    datedebut = Column(Date, nullable=False)
    datefin = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 