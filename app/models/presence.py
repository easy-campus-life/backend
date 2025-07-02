from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Presence(Base):
    __tablename__ = "presences"
    
    id = Column(Integer, primary_key=True, index=True)
    presence = Column(Boolean, nullable=False, default=True)  # True = présent, False = absent
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    classroom = relationship("Classroom", back_populates="presences")
    user = relationship("User", back_populates="presences") 