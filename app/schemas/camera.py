from pydantic import BaseModel
from typing import Optional


class CameraBase(BaseModel):
    location: str
    ip: Optional[str] = None


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    location: Optional[str] = None
    ip: Optional[str] = None


class CameraOut(CameraBase):
    id: str

    class Config:
        from_attributes = True
