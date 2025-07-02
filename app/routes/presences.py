from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, date

from app.database import get_db
from app.models.presence import Presence
from app.models.classroom import Classroom
from app.models.user import User
from app.schemas import PresenceCreate, PresenceUpdate, Presence as PresenceSchema, PresenceWithDetails
from app.utils.auth import get_current_user

router = APIRouter(prefix="/presences", tags=["presences"])

@router.post("/", response_model=PresenceSchema, status_code=status.HTTP_201_CREATED)
def create_presence(presence: PresenceCreate, db: Session = Depends(get_db)):
    """Enregistrer une présence"""
    # Vérifier que la salle de classe existe
    classroom = db.query(Classroom).filter(Classroom.id == presence.classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salle de classe non trouvée"
        )
    
    # Vérifier que l'utilisateur existe
    user = db.query(User).filter(User.id == presence.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Vérifier qu'il n'y a pas déjà une présence pour cet utilisateur dans cette salle aujourd'hui
    today = date.today()
    existing_presence = db.query(Presence).filter(
        Presence.classroom_id == presence.classroom_id,
        Presence.user_id == presence.user_id,
        func.date(Presence.timestamp) == today
    ).first()
    
    if existing_presence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une présence existe déjà pour cet utilisateur dans cette salle aujourd'hui"
        )
    
    db_presence = Presence(**presence.dict())
    db.add(db_presence)
    db.commit()
    db.refresh(db_presence)
    return db_presence

@router.get("/", response_model=List[PresenceWithDetails])
def get_presences(
    skip: int = 0, 
    limit: int = 100, 
    classroom_id: int = None,
    user_id: int = None,
    date_filter: date = None,
    db: Session = Depends(get_db)
):
    """Récupérer les présences avec filtres"""
    query = db.query(Presence)
    
    if classroom_id:
        query = query.filter(Presence.classroom_id == classroom_id)
    
    if user_id:
        query = query.filter(Presence.user_id == user_id)
    
    if date_filter:
        query = query.filter(func.date(Presence.timestamp) == date_filter)
    
    presences = query.offset(skip).limit(limit).all()
    return presences

@router.get("/{presence_id}", response_model=PresenceWithDetails)
def get_presence(presence_id: int, db: Session = Depends(get_db)):
    """Récupérer une présence par son ID"""
    presence = db.query(Presence).filter(Presence.id == presence_id).first()
    if presence is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Présence non trouvée"
        )
    return presence

@router.get("/classroom/{classroom_id}/occupancy", response_model=dict)
def get_classroom_occupancy(classroom_id: int, date_filter: date = None, db: Session = Depends(get_db)):
    """Obtenir l'occupation d'une salle de classe"""
    # Vérifier que la salle existe
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salle de classe non trouvée"
        )
    
    # Construire la requête
    query = db.query(Presence).filter(Presence.classroom_id == classroom_id)
    
    if date_filter:
        query = query.filter(func.date(Presence.timestamp) == date_filter)
    else:
        # Par défaut, aujourd'hui
        today = date.today()
        query = query.filter(func.date(Presence.timestamp) == today)
    
    # Compter les présences
    total_presences = query.filter(Presence.presence == True).count()
    total_absences = query.filter(Presence.presence == False).count()
    
    return {
        "classroom_id": classroom_id,
        "classroom_name": classroom.name,
        "capacity": classroom.capacity,
        "current_occupancy": total_presences,
        "occupancy_percentage": round((total_presences / classroom.capacity) * 100, 2) if classroom.capacity > 0 else 0,
        "available_seats": max(0, classroom.capacity - total_presences),
        "total_presences": total_presences,
        "total_absences": total_absences,
        "date": date_filter or date.today()
    }

@router.get("/user/{user_id}/history", response_model=List[PresenceWithDetails])
def get_user_presence_history(user_id: int, db: Session = Depends(get_db)):
    """Obtenir l'historique des présences d'un utilisateur"""
    # Vérifier que l'utilisateur existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    presences = db.query(Presence).filter(Presence.user_id == user_id).order_by(Presence.timestamp.desc()).all()
    return presences

@router.put("/{presence_id}", response_model=PresenceSchema)
def update_presence(presence_id: int, presence_update: PresenceUpdate, db: Session = Depends(get_db)):
    """Mettre à jour une présence"""
    db_presence = db.query(Presence).filter(Presence.id == presence_id).first()
    if db_presence is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Présence non trouvée"
        )
    
    update_data = presence_update.dict(exclude_unset=True)
    
    # Vérifier les nouvelles relations si elles sont fournies
    if "classroom_id" in update_data:
        classroom = db.query(Classroom).filter(Classroom.id == update_data["classroom_id"]).first()
        if not classroom:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salle de classe non trouvée"
            )
    
    if "user_id" in update_data:
        user = db.query(User).filter(User.id == update_data["user_id"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
    
    for field, value in update_data.items():
        setattr(db_presence, field, value)
    
    db.commit()
    db.refresh(db_presence)
    return db_presence

@router.delete("/{presence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_presence(presence_id: int, db: Session = Depends(get_db)):
    """Supprimer une présence"""
    db_presence = db.query(Presence).filter(Presence.id == presence_id).first()
    if db_presence is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Présence non trouvée"
        )
    
    db.delete(db_presence)
    db.commit()
    return None 