from pydantic import BaseModel
from typing import Optional, List
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
    title: str
    description: Optional[str] = None
    category: str
    attendance: Optional[str] = None
    place: str
    date_start: date
    date_end: date

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cat: Optional[str] = None
    attendance: Optional[str] = None
    place: Optional[str] = None
    date_start: Optional[date] = None
    date_end: Optional[date] = None

class Event(EventBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas pour Mentoring
class MentoringBase(BaseModel):
    mentor_id: int
    sponsored_id: int
    subject: str
    description: Optional[str] = None

class MentoringCreate(MentoringBase):
    pass

class MentoringUpdate(BaseModel):
    mentor_id: Optional[int] = None
    sponsored_id: Optional[int] = None
    subject: Optional[str] = None
    description: Optional[str] = None

class Mentoring(MentoringBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schema pour la réponse avec relations
class MentoringWithUsers(Mentoring):
    mentor: User
    sponsored: User

# Schemas pour Classroom
class ClassroomBase(BaseModel):
    name: str
    capacity: int

class ClassroomCreate(ClassroomBase):
    pass

class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None

class Classroom(ClassroomBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Schemas pour Presence
class PresenceBase(BaseModel):
    presence: bool = True
    classroom_id: int
    user_id: int

class PresenceCreate(BaseModel):
    presence: bool = True
    classroom_id: int
    email: str  # Utiliser l'email au lieu du user_id

class PresenceUpdate(BaseModel):
    presence: Optional[bool] = None
    classroom_id: Optional[int] = None
    user_id: Optional[int] = None

class Presence(PresenceBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Schemas pour l'authentification
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(User):
    """Schema de réponse pour l'utilisateur (sans mot de passe)"""
    class Config:
        from_attributes = True

# Schemas pour les réponses avec relations
class PresenceWithDetails(Presence):
    classroom: Classroom
    user: UserResponse

class ClassroomWithPresences(Classroom):
    presences: List[Presence] = [] 