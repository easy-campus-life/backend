from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    level = Column(String(50), nullable=False)  # étudiant, professeur, admin, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    mentor_relationships = relationship("Mentoring", foreign_keys="Mentoring.mentor_id", back_populates="mentor")
    sponsored_relationships = relationship("Mentoring", foreign_keys="Mentoring.sponsored_id", back_populates="sponsored")
    presences = relationship("Presence", back_populates="user") 