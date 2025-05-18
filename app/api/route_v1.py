import os
from typing import Optional

import ulid
from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session

from app.controllers.face_controller import create_face_and_embedding, track_faces_and_embeddings, process_faces_from_image
from app.crud import crud_person, crud_tracking, crud_camera
from app.dependencies.db import get_db
from app.schemas.camera import CameraOut, CameraCreate
from app.schemas.face import FaceOut
from app.schemas.person import PersonCreate, PersonOut
from app.schemas.tracking import TrackingOut, TrackingOutWithRelations, TrackingMatchOut

router = APIRouter()

# Person Endpoints
@router.get("/persons", response_model=list[PersonOut], tags=["Persons"])
def get_persons(db: Session = Depends(get_db)):
    return crud_person.get_multi(db)

@router.post("/persons", response_model=PersonOut, tags=["Persons"])
def create_person(person_in: PersonCreate, db: Session = Depends(get_db)):
    return crud_person.create(db, person_in)

@router.get("/persons/{person_id}", response_model=PersonOut, tags=["Persons"])
def get_person(person_id: str, db: Session = Depends(get_db)):
    db_person = crud_person.get(db, person_id)
    if not db_person:
        raise HTTPException(status_code=404, detail="Person not found")
    return db_person

# Face Endpoints
@router.post("/faces", response_model=FaceOut, tags=["Faces"])
async def create_face(person_id: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await create_face_and_embedding(db=db, person_id=person_id, file=file)

# Tracking Endpoints
@router.post("/tracking", response_model=list[TrackingMatchOut], tags=["Tracking"])
async def create_tracking(file: UploadFile = File(...), db: Session = Depends(get_db)):
    return await track_faces_and_embeddings(db=db, file=file)

@router.post("/tracking/cctv", response_model=dict, tags=["CCTV Feed"])
async def process_cctv_feed(
    background_tasks: BackgroundTasks,
    camera_id: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)):
    """
    Receives CCTV image and processes it in background.
    """
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in {"jpg", "jpeg", "png", "webp"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    case_id = str(ulid.new())
    filename = f"{case_id}.{ext}"
    file_path = os.path.join("uploads/cctv", filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # ✅ This runs after response
    background_tasks.add_task(process_faces_from_image, file_path, camera_id, db)

    return {"message": "We have received the image, and it is being processed."}

@router.get("/tracking", response_model=list[TrackingOutWithRelations], tags=["Tracking"])
def get_tracking_list(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_tracking.get_multi(db, skip=skip, limit=limit)

@router.get("/tracking/{tracking_id}", response_model=TrackingOutWithRelations, tags=["Tracking"])
def get_tracking(tracking_id: str, db: Session = Depends(get_db)):
    tracking = crud_tracking.get(db, tracking_id)
    if not tracking:
        raise HTTPException(status_code=404, detail="Tracking record not found")
    return tracking

# Camera Endpoints
@router.post("/cameras", response_model=CameraOut, tags=["Cameras"])
def create_camera(camera_in: CameraCreate, db: Session = Depends(get_db)):
    return crud_camera.create(db, camera_in)

@router.get("/cameras/{camera_id}", response_model=CameraOut, tags=["Cameras"])
def get_camera(camera_id: str, db: Session = Depends(get_db)):
    return crud_camera.get(db, camera_id)
