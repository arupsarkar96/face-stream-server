from sqlalchemy.orm import Session
from app.db.models.face import Face
from app.schemas.face import FaceCreate, FaceUpdate


def get(db: Session, face_id: str) -> Face | None:
    return db.query(Face).filter(Face.id == face_id).first()


def get_by_person(db: Session, person_id: str):
    return db.query(Face).filter(Face.person_id == person_id).all()


def get_multi(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Face).offset(skip).limit(limit).all()

def get_all(db: Session):
    return db.query(Face).all()


def create(db: Session, face_in: FaceCreate) -> Face:
    face = Face(**face_in.dict())
    db.add(face)
    db.commit()
    db.refresh(face)
    return face


def update(db: Session, db_obj: Face, face_in: FaceUpdate) -> Face:
    for field, value in face_in.dict(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, face_id: str) -> Face | None:
    obj = get(db, face_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
