from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.mentoring import Mentoring
from app.models.user import User
from app.schemas import MentoringCreate, MentoringUpdate, Mentoring as MentoringSchema, MentoringWithUsers

router = APIRouter(prefix="/mentoring", tags=["mentoring"])

@router.post("/", response_model=MentoringSchema, status_code=status.HTTP_201_CREATED)
def create_mentoring(mentoring: MentoringCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle relation de mentorat"""
    # Vérifier que le mentor existe
    mentor_user = db.query(User).filter(User.id == mentoring.mentor_id).first()
    if not mentor_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor non trouvé"
        )
    
    # Vérifier que l'étudiant sponsorisé existe
    sponsored_user = db.query(User).filter(User.id == mentoring.sponsored_id).first()
    if not sponsored_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant sponsorisé non trouvé"
        )
    
    # Vérifier que le mentor et l'étudiant sont différents
    if mentoring.mentor_id == mentoring.sponsored_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mentor ne peut pas être son propre mentor"
        )
    
    # Vérifier qu'il n'y a pas déjà une relation de mentorat entre ces deux utilisateurs
    existing_mentoring = db.query(Mentoring).filter(
        Mentoring.mentor_id == mentoring.mentor_id,
        Mentoring.sponsored_id == mentoring.sponsored_id
    ).first()
    if existing_mentoring:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une relation de mentorat existe déjà entre ces utilisateurs"
        )
    
    db_mentoring = Mentoring(**mentoring.dict())
    db.add(db_mentoring)
    db.commit()
    db.refresh(db_mentoring)
    return db_mentoring

@router.get("/", response_model=List[MentoringWithUsers])
def get_mentoring(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer toutes les relations de mentorat"""
    mentoring = db.query(Mentoring).offset(skip).limit(limit).all()
    return mentoring

@router.get("/{mentoring_id}", response_model=MentoringWithUsers)
def get_mentoring_by_id(mentoring_id: int, db: Session = Depends(get_db)):
    """Récupérer une relation de mentorat par son ID"""
    mentoring = db.query(Mentoring).filter(Mentoring.id == mentoring_id).first()
    if mentoring is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation de mentorat non trouvée"
        )
    return mentoring

@router.get("/user/{user_id}/mentoring", response_model=List[MentoringWithUsers])
def get_user_mentoring(user_id: int, db: Session = Depends(get_db)):
    """Récupérer tous les étudiants qu'un utilisateur mentore"""
    # Vérifier que l'utilisateur existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    mentoring = db.query(Mentoring).filter(Mentoring.mentor_id == user_id).all()
    return mentoring

@router.get("/user/{user_id}/sponsored", response_model=List[MentoringWithUsers])
def get_user_sponsored(user_id: int, db: Session = Depends(get_db)):
    """Récupérer tous les mentors d'un utilisateur"""
    # Vérifier que l'utilisateur existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    mentoring = db.query(Mentoring).filter(Mentoring.sponsored_id == user_id).all()
    return mentoring

@router.put("/{mentoring_id}", response_model=MentoringSchema)
def update_mentoring(mentoring_id: int, mentoring_update: MentoringUpdate, db: Session = Depends(get_db)):
    """Mettre à jour une relation de mentorat"""
    db_mentoring = db.query(Mentoring).filter(Mentoring.id == mentoring_id).first()
    if db_mentoring is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation de mentorat non trouvée"
        )
    
    update_data = mentoring_update.dict(exclude_unset=True)
    
    # Vérifier les nouvelles relations si elles sont fournies
    if "mentor_id" in update_data:
        mentor_user = db.query(User).filter(User.id == update_data["mentor_id"]).first()
        if not mentor_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mentor non trouvé"
            )
    
    if "sponsored_id" in update_data:
        sponsored_user = db.query(User).filter(User.id == update_data["sponsored_id"]).first()
        if not sponsored_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Étudiant sponsorisé non trouvé"
            )
    
    # Vérifier que le mentor et l'étudiant sont différents
    new_mentor_id = update_data.get("mentor_id", db_mentoring.mentor_id)
    new_sponsored_id = update_data.get("sponsored_id", db_mentoring.sponsored_id)
    if new_mentor_id == new_sponsored_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mentor ne peut pas être son propre mentor"
        )
    
    for field, value in update_data.items():
        setattr(db_mentoring, field, value)
    
    db.commit()
    db.refresh(db_mentoring)
    return db_mentoring

@router.delete("/{mentoring_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mentoring(mentoring_id: int, db: Session = Depends(get_db)):
    """Supprimer une relation de mentorat"""
    db_mentoring = db.query(Mentoring).filter(Mentoring.id == mentoring_id).first()
    if db_mentoring is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation de mentorat non trouvée"
        )
    
    db.delete(db_mentoring)
    db.commit()
    return None 