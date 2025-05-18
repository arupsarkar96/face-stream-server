from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.schemas.camera import CameraOut
from app.schemas.person import PersonOut


class TrackingBase(BaseModel):
    camera_id: Optional[str] = None
    photo: str
    similarity: Optional[float] = None
    person_id: Optional[str] = None
    index_size: int
    time_taken: float


class TrackingCreate(TrackingBase):
    pass


class TrackingUpdate(BaseModel):
    person_id: Optional[str] = None
    similarity: Optional[float] = None


class TrackingOut(BaseModel):
    id: str
    similarity: Optional[float] = None
    photo: str
    time_taken: float
    index_size: int
    timestamp: datetime
    person: PersonOut = None

    class Config:
        from_attributes = True

class TrackingOutWithRelations(TrackingOut):
    camera: CameraOut | None = None

class TrackingMatchOut(BaseModel):
    id: str
    similarity: float
    photo: str
    time_taken: int
    index_size: int
    timestamp: datetime
    person: PersonOut