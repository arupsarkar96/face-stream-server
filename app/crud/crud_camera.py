from sqlalchemy.orm import Session
from app.db.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate


def get(db: Session, camera_id: str) -> Camera | None:
    return db.query(Camera).filter(Camera.id == camera_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Camera).offset(skip).limit(limit).all()


def create(db: Session, camera_in: CameraCreate) -> Camera:
    camera = Camera(**camera_in.dict())
    db.add(camera)
    db.commit()
    db.refresh(camera)
    return camera


def update(db: Session, db_obj: Camera, camera_in: CameraUpdate) -> Camera:
    for field, value in camera_in.dict(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, camera_id: str) -> Camera | None:
    obj = get(db, camera_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
