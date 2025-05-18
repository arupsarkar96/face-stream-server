import ulid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, func, Boolean, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base



# 😐 Face Table (embedding of a person)
class Face(Base):
    __tablename__ = "faces"

    id = Column(String(26), primary_key=True, default=lambda: str(ulid.new()))
    person_id = Column(String(26), ForeignKey("persons.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    embedding = Column(JSON, nullable=False)
    is_male = Column(Boolean, default=True)
    age = Column(Integer, default=0)
    photo_path = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    person = relationship("Person", back_populates="faces")
