from sqlalchemy.orm import Session
from app.db.models.tracking import Tracking
from app.schemas.tracking import TrackingCreate, TrackingUpdate


def get(db: Session, tracking_id: str) -> Tracking | None:
    return db.query(Tracking).filter(Tracking.id == tracking_id).first()


def get_multi(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Tracking).order_by(Tracking.timestamp.desc()).offset(skip).limit(limit).all()


def get_by_person(db: Session, person_id: str):
    return db.query(Tracking).filter(Tracking.person_id == person_id).order_by(Tracking.timestamp.desc()).all()


def create(db: Session, tracking_in: TrackingCreate) -> Tracking:
    tracking = Tracking(**tracking_in.model_dump())
    db.add(tracking)
    db.commit()
    db.refresh(tracking)
    return tracking


def update(db: Session, db_obj: Tracking, tracking_in: TrackingUpdate) -> Tracking:
    for field, value in tracking_in.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, tracking_id: str) -> Tracking | None:
    obj = get(db, tracking_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
