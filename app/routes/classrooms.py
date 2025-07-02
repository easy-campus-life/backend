from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.classroom import Classroom
from app.schemas import ClassroomCreate, ClassroomUpdate, Classroom as ClassroomSchema, ClassroomWithPresences

router = APIRouter(prefix="/classrooms", tags=["classrooms"])

@router.post("/", response_model=ClassroomSchema, status_code=status.HTTP_201_CREATED)
def create_classroom(classroom: ClassroomCreate, db: Session = Depends(get_db)):
    """Créer une nouvelle salle de classe"""
    # Vérifier que la capacité est positive
    if classroom.capacity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La capacité doit être supérieure à 0"
        )
    
    db_classroom = Classroom(**classroom.dict())
    db.add(db_classroom)
    db.commit()
    db.refresh(db_classroom)
    return db_classroom

@router.get("/", response_model=List[ClassroomSchema])
def get_classrooms(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer toutes les salles de classe"""
    classrooms = db.query(Classroom).offset(skip).limit(limit).all()
    return classrooms

@router.get("/{classroom_id}", response_model=ClassroomSchema)
def get_classroom(classroom_id: int, db: Session = Depends(get_db)):
    """Récupérer une salle de classe par son ID"""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if classroom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salle de classe non trouvée"
        )
    return classroom

@router.get("/{classroom_id}/with-presences", response_model=ClassroomWithPresences)
def get_classroom_with_presences(classroom_id: int, db: Session = Depends(get_db)):
    """Récupérer une salle de classe avec ses présences"""
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if classroom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salle de classe non trouvée"
        )
    return classroom

@router.put("/{classroom_id}", response_model=ClassroomSchema)
def update_classroom(classroom_id: int, classroom_update: ClassroomUpdate, db: Session = Depends(get_db)):
    """Mettre à jour une salle de classe"""
    db_classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if db_classroom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salle de classe non trouvée"
        )
    
    update_data = classroom_update.dict(exclude_unset=True)
    
    # Vérifier que la capacité est positive si elle est fournie
    if "capacity" in update_data and update_data["capacity"] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La capacité doit être supérieure à 0"
        )
    
    for field, value in update_data.items():
        setattr(db_classroom, field, value)
    
    db.commit()
    db.refresh(db_classroom)
    return db_classroom

@router.delete("/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_classroom(classroom_id: int, db: Session = Depends(get_db)):
    """Supprimer une salle de classe"""
    db_classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if db_classroom is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salle de classe non trouvée"
        )
    
    db.delete(db_classroom)
    db.commit()
    return None 