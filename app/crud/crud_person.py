from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.db.models.person import Person
from app.schemas.person import PersonCreate, PersonUpdate

def get(db: Session, person_id: str) -> Person | None:
    return db.query(Person).filter(Person.id == person_id).first()

def get_multi(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Person).order_by(desc(Person.id)).offset(skip).limit(limit).all()

def create(db: Session, person_in: PersonCreate) -> Person:
    person = Person(**person_in.model_dump())
    db.add(person)
    db.commit()
    db.refresh(person)
    return person

def update(db: Session, db_obj: Person, person_in: PersonUpdate) -> Person:
    for field, value in person_in.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def remove(db: Session, person_id: str) -> Person | None:
    obj = get(db, person_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj
