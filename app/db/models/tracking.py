import ulid
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, func, Integer
from sqlalchemy.orm import relationship
from app.db.base import Base

# 📌 Tracking Table (links Face + Camera)
class Tracking(Base):
    __tablename__ = "tracking"

    id = Column(String(26), primary_key=True, default=lambda: str(ulid.new()))
    person_id = Column(String(26), ForeignKey("persons.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    camera_id = Column(String(26), ForeignKey("cameras.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=True)
    similarity = Column(Float, nullable=True)
    photo = Column(String(255), nullable=False)
    time_taken = Column(Float, default=0.0)
    index_size = Column(Integer, default=0)
    timestamp = Column(DateTime, server_default=func.now())

    # Relationship to the Person table
    person = relationship("Person", back_populates="trackings")

    # Relationship to the Camera table
    camera = relationship("Camera", back_populates="trackings")

