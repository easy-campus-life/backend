from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

# Schemas pour User
class UserBase(BaseModel):
    name: str
    email: str
    level: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    level: Optional[str] = None

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas pour Event
class EventBase(BaseModel):
    titre: str
    desc: Optional[str] = None
    cat: str
    attendance: Optional[str] = None
    lieu: str
    datedebut: date
    datefin: date

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    titre: Optional[str] = None
    desc: Optional[str] = None
    cat: Optional[str] = None
    attendance: Optional[str] = None
    lieu: Optional[str] = None
    datedebut: Optional[date] = None
    datefin: Optional[date] = None

class Event(EventBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas pour Mentor
class MentorBase(BaseModel):
    mentor_id: int
    sponsored_id: int
    subject: str
    description: Optional[str] = None

class MentorCreate(MentorBase):
    pass

class MentorUpdate(BaseModel):
    mentor_id: Optional[int] = None
    sponsored_id: Optional[int] = None
    subject: Optional[str] = None
    description: Optional[str] = None

class Mentor(MentorBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema pour la réponse avec relations
class MentorWithUsers(Mentor):
    mentor: User
    sponsored: User 