import ulid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.db.base import Base


# 📷 Camera Table
class Camera(Base):
    __tablename__ = "cameras"

    id = Column(String(26), primary_key=True, default=lambda: str(ulid.new()))
    location = Column(String(100), nullable=False)
    ip = Column(String(100), nullable=True)

    trackings = relationship("Tracking", back_populates="camera", cascade="all, delete-orphan")
