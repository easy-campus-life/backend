from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, date

from app.database import get_db
from app.models.event_participation import EventParticipation
from app.models.event import Event
from app.models.user import User
from app.schemas import (
    EventParticipationCreate, 
    EventParticipationUpdate, 
    EventParticipation as EventParticipationSchema,
    EventParticipationWithDetails,
    EventWithParticipations
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/event-participations", tags=["event-participations"])

@router.post("/", response_model=EventParticipationSchema, status_code=status.HTTP_201_CREATED)
def participate_to_event(participation: EventParticipationCreate, db: Session = Depends(get_db)):
    """Participer à un événement"""
    # Vérifier que l'événement existe
    event = db.query(Event).filter(Event.id == participation.event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement non trouvé"
        )
    
    # Chercher l'utilisateur par email
    user = db.query(User).filter(User.email == participation.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur avec l'email {participation.email} non trouvé"
        )
    
    # Vérifier qu'il n'y a pas déjà une participation pour cet utilisateur à cet événement
    existing_participation = db.query(EventParticipation).filter(
        EventParticipation.event_id == participation.event_id,
        EventParticipation.user_id == user.id
    ).first()
    
    if existing_participation:
        # Si la participation existe déjà, on la met à jour
        existing_participation.is_attending = True
        existing_participation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_participation)
        return existing_participation
    
    # Créer une nouvelle participation
    db_participation = EventParticipation(
        event_id=participation.event_id,
        user_id=user.id,
        is_attending=True
    )
    db.add(db_participation)
    db.commit()
    db.refresh(db_participation)
    return db_participation

@router.get("/", response_model=List[EventParticipationWithDetails])
def get_participations(
    skip: int = 0, 
    limit: int = 100, 
    event_id: int = None,
    user_id: int = None,
    is_attending: bool = None,
    db: Session = Depends(get_db)
):
    """Récupérer les participations avec filtres"""
    query = db.query(EventParticipation)
    
    if event_id:
        query = query.filter(EventParticipation.event_id == event_id)
    
    if user_id:
        query = query.filter(EventParticipation.user_id == user_id)
    
    if is_attending is not None:
        query = query.filter(EventParticipation.is_attending == is_attending)
    
    participations = query.offset(skip).limit(limit).all()
    return participations

@router.get("/event/{event_id}/participants", response_model=List[EventParticipationWithDetails])
def get_event_participants(event_id: int, db: Session = Depends(get_db)):
    """Récupérer tous les participants d'un événement"""
    # Vérifier que l'événement existe
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement non trouvé"
        )
    
    participations = db.query(EventParticipation).filter(
        EventParticipation.event_id == event_id,
        EventParticipation.is_attending == True
    ).all()
    return participations

@router.get("/event/{event_id}/participant-count", response_model=dict)
def get_event_participant_count(event_id: int, db: Session = Depends(get_db)):
    """Obtenir le nombre de participants d'un événement"""
    # Vérifier que l'événement existe
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Événement non trouvé"
        )
    
    # Compter les participants
    participant_count = db.query(EventParticipation).filter(
        EventParticipation.event_id == event_id,
        EventParticipation.is_attending == True
    ).count()
    
    return {
        "event_id": event_id,
        "event_title": event.title,
        "participant_count": participant_count,
        "expected_attendance": event.attendance,
        "attendance_percentage": round((participant_count / int(event.attendance)) * 100, 2) if event.attendance and event.attendance.isdigit() and int(event.attendance) > 0 else 0
    }

@router.get("/user/{user_id}/events", response_model=List[EventWithParticipations])
def get_user_events(user_id: int, db: Session = Depends(get_db)):
    """Obtenir tous les événements auxquels un utilisateur participe"""
    # Vérifier que l'utilisateur existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Récupérer les événements avec le nombre de participants
    events = db.query(Event).join(EventParticipation, Event.id == EventParticipation.event_id).filter(
        EventParticipation.user_id == user_id,
        EventParticipation.is_attending == True
    ).all()
    
    # Ajouter le nombre de participants pour chaque événement
    result = []
    for event in events:
        participant_count = db.query(EventParticipation).filter(
            EventParticipation.event_id == event.id,
            EventParticipation.is_attending == True
        ).count()
        
        event_dict = {
            **event.__dict__,
            "participant_count": participant_count
        }
        result.append(event_dict)
    
    return result

@router.put("/{participation_id}", response_model=EventParticipationSchema)
def update_participation(participation_id: int, participation_update: EventParticipationUpdate, db: Session = Depends(get_db)):
    """Mettre à jour une participation (annuler sa participation)"""
    db_participation = db.query(EventParticipation).filter(EventParticipation.id == participation_id).first()
    if db_participation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participation non trouvée"
        )
    
    update_data = participation_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_participation, field, value)
    
    db.commit()
    db.refresh(db_participation)
    return db_participation

@router.delete("/{participation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_participation(participation_id: int, db: Session = Depends(get_db)):
    """Supprimer une participation"""
    db_participation = db.query(EventParticipation).filter(EventParticipation.id == participation_id).first()
    if db_participation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participation non trouvée"
        )
    
    db.delete(db_participation)
    db.commit()
    return None

@router.post("/{event_id}/cancel", response_model=EventParticipationSchema)
def cancel_participation(event_id: int, email: str, db: Session = Depends(get_db)):
    """Annuler sa participation à un événement"""
    # Chercher l'utilisateur par email
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur avec l'email {email} non trouvé"
        )
    
    # Chercher la participation
    participation = db.query(EventParticipation).filter(
        EventParticipation.event_id == event_id,
        EventParticipation.user_id == user.id
    ).first()
    
    if not participation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participation non trouvée"
        )
    
    # Marquer comme ne participant plus
    participation.is_attending = False
    participation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(participation)
    return participation 