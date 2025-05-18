from pydantic import BaseModel
from typing import List


class FaceBase(BaseModel):
    person_id: str
    embedding: List[float]
    is_male: bool
    age: int
    photo_path: str


class FaceCreate(FaceBase):
    pass


class FaceUpdate(BaseModel):
    embedding: List[float] | None = None
    photo_path: str | None = None


class FaceOut(BaseModel):
    id: str
    is_male: bool
    age: int
    photo_path: str

    class Config:
        from_attributes = True