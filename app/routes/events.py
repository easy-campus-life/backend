from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db
from app.models.event import Event
from app.schemas import EventCreate, EventUpdate, Event as EventSchema

router = APIRouter(prefix="/events", tags=["events"])

@router.post("/", response_model=EventSchema, status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    """Créer un nouvel événement"""
    # Vérifier que la date de fin est après la date de début
    if event.date_end < event.date_start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La date de fin doit être après la date de début"
        )
    
    db_event = Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/", response_model=List[EventSchema])
def get_events(
    skip: int = 0, 
    limit: int = 100, 
    category: str = None,
    db: Session = Depends(get_db)
):
    """Récupérer tous les événements avec filtres optionnels"""
    query = db.query(Event)
    
    if category:
        query = query.filter(Event.category == category)
    
    events = query.offset(skip).limit(limit).all()
    return events

@router.get("/{event_id}", response_model=EventSchema)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Récupérer un événement par son ID"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement non trouvé"
        )
    return event

@router.get("/upcoming/", response_model=List[EventSchema])
def get_upcoming_events(db: Session = Depends(get_db)):
    """Récupérer les événements à venir"""
    today = date.today()
    events = db.query(Event).filter(Event.date_start >= today).order_by(Event.date_start).all()
    return events

@router.put("/{event_id}", response_model=EventSchema)
def update_event(event_id: int, event_update: EventUpdate, db: Session = Depends(get_db)):
    """Mettre à jour un événement"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if db_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement non trouvé"
        )
    
    # Vérifier les dates si elles sont fournies
    update_data = event_update.dict(exclude_unset=True)
    if "date_start" in update_data and "date_end" in update_data:
        if update_data["date_end"] < update_data["date_start"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La date de fin doit être après la date de début"
            )
    elif "date_start" in update_data:
        if db_event.date_end < update_data["date_start"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La date de fin doit être après la date de début"
            )
    elif "date_end" in update_data:
        if update_data["date_end"] < db_event.date_start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La date de fin doit être après la date de début"
            )
    
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Supprimer un événement"""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if db_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement non trouvé"
        )
    
    db.delete(db_event)
    db.commit()
    return None 