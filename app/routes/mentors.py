from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.mentor import Mentor
from app.models.user import User
from app.schemas import MentorCreate, MentorUpdate, Mentor as MentorSchema, MentorWithUsers

router = APIRouter(prefix="/mentors", tags=["mentors"])

@router.post("/", response_model=MentorSchema, status_code=status.HTTP_201_CREATED)
def create_mentor(mentor: MentorCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle relation de mentorat"""
    # Vérifier que le mentor existe
    mentor_user = db.query(User).filter(User.id == mentor.mentor_id).first()
    if not mentor_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mentor non trouvé"
        )
    
    # Vérifier que l'étudiant sponsorisé existe
    sponsored_user = db.query(User).filter(User.id == mentor.sponsored_id).first()
    if not sponsored_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Étudiant sponsorisé non trouvé"
        )
    
    # Vérifier que le mentor et l'étudiant sont différents
    if mentor.mentor_id == mentor.sponsored_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mentor ne peut pas être son propre mentor"
        )
    
    # Vérifier qu'il n'y a pas déjà une relation de mentorat entre ces deux utilisateurs
    existing_mentor = db.query(Mentor).filter(
        Mentor.mentor_id == mentor.mentor_id,
        Mentor.sponsored_id == mentor.sponsored_id
    ).first()
    if existing_mentor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une relation de mentorat existe déjà entre ces utilisateurs"
        )
    
    db_mentor = Mentor(**mentor.dict())
    db.add(db_mentor)
    db.commit()
    db.refresh(db_mentor)
    return db_mentor

@router.get("/", response_model=List[MentorWithUsers])
def get_mentors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer toutes les relations de mentorat"""
    mentors = db.query(Mentor).offset(skip).limit(limit).all()
    return mentors

@router.get("/{mentor_id}", response_model=MentorWithUsers)
def get_mentor(mentor_id: int, db: Session = Depends(get_db)):
    """Récupérer une relation de mentorat par son ID"""
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if mentor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation de mentorat non trouvée"
        )
    return mentor

@router.get("/user/{user_id}/mentoring", response_model=List[MentorWithUsers])
def get_user_mentoring(user_id: int, db: Session = Depends(get_db)):
    """Récupérer tous les étudiants qu'un utilisateur mentore"""
    # Vérifier que l'utilisateur existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    mentors = db.query(Mentor).filter(Mentor.mentor_id == user_id).all()
    return mentors

@router.get("/user/{user_id}/sponsored", response_model=List[MentorWithUsers])
def get_user_sponsored(user_id: int, db: Session = Depends(get_db)):
    """Récupérer tous les mentors d'un utilisateur"""
    # Vérifier que l'utilisateur existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    mentors = db.query(Mentor).filter(Mentor.sponsored_id == user_id).all()
    return mentors

@router.put("/{mentor_id}", response_model=MentorSchema)
def update_mentor(mentor_id: int, mentor_update: MentorUpdate, db: Session = Depends(get_db)):
    """Mettre à jour une relation de mentorat"""
    db_mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if db_mentor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation de mentorat non trouvée"
        )
    
    update_data = mentor_update.dict(exclude_unset=True)
    
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
    new_mentor_id = update_data.get("mentor_id", db_mentor.mentor_id)
    new_sponsored_id = update_data.get("sponsored_id", db_mentor.sponsored_id)
    if new_mentor_id == new_sponsored_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mentor ne peut pas être son propre mentor"
        )
    
    for field, value in update_data.items():
        setattr(db_mentor, field, value)
    
    db.commit()
    db.refresh(db_mentor)
    return db_mentor

@router.delete("/{mentor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mentor(mentor_id: int, db: Session = Depends(get_db)):
    """Supprimer une relation de mentorat"""
    db_mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if db_mentor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Relation de mentorat non trouvée"
        )
    
    db.delete(db_mentor)
    db.commit()
    return None 