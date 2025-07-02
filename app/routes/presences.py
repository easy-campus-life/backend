from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Dict, Any
from datetime import datetime, date, timedelta

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
    
    # Chercher l'utilisateur par email
    user = db.query(User).filter(User.email == presence.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur avec l'email {presence.email} non trouvé"
        )
    
    # Vérifier qu'il n'y a pas déjà une présence pour cet utilisateur dans cette salle aujourd'hui
    today = date.today()
    existing_presence = db.query(Presence).filter(
        Presence.classroom_id == presence.classroom_id,
        Presence.user_id == user.id,
        func.date(Presence.timestamp) == today
    ).first()
    
    if existing_presence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une présence existe déjà pour cet utilisateur dans cette salle aujourd'hui"
        )
    
    # Créer la présence avec le user_id trouvé
    db_presence = Presence(
        presence=presence.presence,
        classroom_id=presence.classroom_id,
        user_id=user.id
    )
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

# ===== ENDPOINTS POUR L'ANALYSE D'AFFLUENCE =====

@router.get("/analytics/overview", response_model=Dict[str, Any])
def get_affluence_overview(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db)
):
    """Vue d'ensemble de l'affluence sur une période"""
    if not start_date:
        start_date = date.today() - timedelta(days=7)
    if not end_date:
        end_date = date.today()
    
    # Statistiques globales
    total_presences = db.query(Presence).filter(
        func.date(Presence.timestamp).between(start_date, end_date),
        Presence.presence == True
    ).count()
    
    total_absences = db.query(Presence).filter(
        func.date(Presence.timestamp).between(start_date, end_date),
        Presence.presence == False
    ).count()
    
    # Affluence par jour
    daily_affluence = db.query(
        func.date(Presence.timestamp).label('date'),
        func.count(Presence.id).label('count')
    ).filter(
        func.date(Presence.timestamp).between(start_date, end_date),
        Presence.presence == True
    ).group_by(func.date(Presence.timestamp)).order_by(func.date(Presence.timestamp)).all()
    
    # Affluence par salle
    classroom_affluence = db.query(
        Classroom.name.label('classroom_name'),
        func.count(Presence.id).label('presence_count')
    ).join(Presence, Classroom.id == Presence.classroom_id).filter(
        func.date(Presence.timestamp).between(start_date, end_date),
        Presence.presence == True
    ).group_by(Classroom.id, Classroom.name).order_by(func.count(Presence.id).desc()).all()
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "statistics": {
            "total_presences": total_presences,
            "total_absences": total_absences,
            "presence_rate": round((total_presences / (total_presences + total_absences)) * 100, 2) if (total_presences + total_absences) > 0 else 0
        },
        "daily_affluence": [
            {"date": str(day.date), "count": day.count} 
            for day in daily_affluence
        ],
        "classroom_affluence": [
            {"classroom_name": room.classroom_name, "presence_count": room.presence_count}
            for room in classroom_affluence
        ]
    }

@router.get("/analytics/classroom/{classroom_id}/trends", response_model=Dict[str, Any])
def get_classroom_affluence_trends(
    classroom_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Tendances d'affluence pour une salle spécifique"""
    # Vérifier que la salle existe
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salle de classe non trouvée"
        )
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    # Affluence par jour pour cette salle
    daily_data = db.query(
        func.date(Presence.timestamp).label('date'),
        func.count(Presence.id).label('presence_count'),
        func.avg(func.cast(Presence.presence, func.Integer)).label('presence_rate')
    ).filter(
        Presence.classroom_id == classroom_id,
        func.date(Presence.timestamp).between(start_date, end_date)
    ).group_by(func.date(Presence.timestamp)).order_by(func.date(Presence.timestamp)).all()
    
    # Heures de pointe
    peak_hours = db.query(
        extract('hour', Presence.timestamp).label('hour'),
        func.count(Presence.id).label('count')
    ).filter(
        Presence.classroom_id == classroom_id,
        func.date(Presence.timestamp).between(start_date, end_date),
        Presence.presence == True
    ).group_by(extract('hour', Presence.timestamp)).order_by(func.count(Presence.id).desc()).limit(5).all()
    
    return {
        "classroom": {
            "id": classroom_id,
            "name": classroom.name,
            "capacity": classroom.capacity
        },
        "period": {
            "start_date": start_date,
            "end_date": end_date,
            "days": days
        },
        "daily_trends": [
            {
                "date": str(day.date),
                "presence_count": day.presence_count,
                "presence_rate": round(float(day.presence_rate) * 100, 2) if day.presence_rate else 0
            }
            for day in daily_data
        ],
        "peak_hours": [
            {"hour": int(hour.hour), "count": hour.count}
            for hour in peak_hours
        ]
    }

@router.get("/analytics/real-time", response_model=Dict[str, Any])
def get_real_time_affluence(db: Session = Depends(get_db)):
    """Affluence en temps réel (aujourd'hui)"""
    today = date.today()
    
    # Occupation actuelle par salle
    current_occupancy = db.query(
        Classroom.id,
        Classroom.name,
        Classroom.capacity,
        func.count(Presence.id).label('current_presences')
    ).outerjoin(Presence, (Classroom.id == Presence.classroom_id) & 
                (func.date(Presence.timestamp) == today) & 
                (Presence.presence == True)
    ).group_by(Classroom.id, Classroom.name, Classroom.capacity).all()
    
    # Total des présences aujourd'hui
    total_today = db.query(Presence).filter(
        func.date(Presence.timestamp) == today,
        Presence.presence == True
    ).count()
    
    # Affluence par heure aujourd'hui
    hourly_today = db.query(
        extract('hour', Presence.timestamp).label('hour'),
        func.count(Presence.id).label('count')
    ).filter(
        func.date(Presence.timestamp) == today,
        Presence.presence == True
    ).group_by(extract('hour', Presence.timestamp)).order_by(extract('hour', Presence.timestamp)).all()
    
    return {
        "date": today,
        "total_presences_today": total_today,
        "current_occupancy": [
            {
                "classroom_id": room.id,
                "classroom_name": room.name,
                "capacity": room.capacity,
                "current_presences": room.current_presences,
                "occupancy_percentage": round((room.current_presences / room.capacity) * 100, 2) if room.capacity > 0 else 0,
                "available_seats": max(0, room.capacity - room.current_presences)
            }
            for room in current_occupancy
        ],
        "hourly_distribution": [
            {"hour": int(hour.hour), "count": hour.count}
            for hour in hourly_today
        ]
    }

@router.get("/analytics/peak-times", response_model=Dict[str, Any])
def get_peak_times(
    classroom_id: int = None,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Analyser les heures de pointe"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    query = db.query(
        extract('hour', Presence.timestamp).label('hour'),
        func.count(Presence.id).label('count')
    ).filter(
        func.date(Presence.timestamp).between(start_date, end_date),
        Presence.presence == True
    )
    
    if classroom_id:
        query = query.filter(Presence.classroom_id == classroom_id)
    
    hourly_data = query.group_by(extract('hour', Presence.timestamp)).order_by(extract('hour', Presence.timestamp)).all()
    
    # Calculer les heures de pointe
    max_count = max([hour.count for hour in hourly_data]) if hourly_data else 0
    peak_hours = [
        {"hour": int(hour.hour), "count": hour.count, "percentage": round((hour.count / max_count) * 100, 2)}
        for hour in hourly_data
    ]
    
    return {
        "period": {
            "start_date": start_date,
            "end_date": end_date,
            "days": days
        },
        "classroom_id": classroom_id,
        "peak_hours": peak_hours,
        "busiest_hour": max(peak_hours, key=lambda x: x['count']) if peak_hours else None
    } 