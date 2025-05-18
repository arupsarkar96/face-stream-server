
from sqlalchemy import Column, String, UUID, DateTime, func
from sqlalchemy.orm import relationship
import ulid
from app.db.base import Base

class Person(Base):
    __tablename__ = "persons"

    id = Column(String(26), primary_key=True, default=lambda: str(ulid.new()))
    name = Column(String(100), nullable=False)
    note = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    faces = relationship("Face", back_populates="person", cascade="all, delete-orphan", passive_deletes=True)
    trackings = relationship("Tracking", back_populates="person", cascade="all, delete-orphan")
