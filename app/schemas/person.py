from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.face import FaceOut


class PersonBase(BaseModel):
    name: str
    note: Optional[str] = None

class PersonCreate(PersonBase):
    pass

class PersonUpdate(PersonBase):
    pass

class PersonOut(BaseModel):
    id: str
    name: str
    note: str
    created_at: datetime
    faces: List[FaceOut] = []

    class Config:
        from_attributes = True