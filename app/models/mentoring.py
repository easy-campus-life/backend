from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Mentoring(Base):
    __tablename__ = "mentoring"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sponsored_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relations
    mentor = relationship("User", foreign_keys=[mentor_id], back_populates="mentor_relationships")
    sponsored = relationship("User", foreign_keys=[sponsored_id], back_populates="sponsored_relationships") 