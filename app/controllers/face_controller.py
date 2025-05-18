import os
from datetime import datetime, UTC
from typing import Optional, List

import numpy as np
import ulid
from PIL import Image
from fastapi import UploadFile, HTTPException
from insightface.app import FaceAnalysis
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.faiss_manager import FaissIndexManager
from app.core.storage import minio_client
from app.crud import crud_face, crud_tracking, crud_person
from app.schemas.face import FaceOut, FaceCreate
from app.schemas.person import PersonOut
from app.schemas.tracking import TrackingCreate, TrackingMatchOut

UPLOAD_DIR = "uploads"
FACE_DIR = os.path.join(UPLOAD_DIR, "faces")
TEMP_DIR = os.path.join(UPLOAD_DIR, "temps")
CCTV_DIR = os.path.join(UPLOAD_DIR, "cctv")

for path in [UPLOAD_DIR, FACE_DIR, TEMP_DIR, CCTV_DIR]:
    os.makedirs(path, exist_ok=True)

app_face = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
app_face.prepare(ctx_id=-1)

index_manager = FaissIndexManager()

async def create_face_and_embedding(person_id: str, file: UploadFile, db: Session) -> FaceOut:
    """Register a new face for a person, store embedding and save crop."""
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in {"jpg", "jpeg", "png", "webp"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    case_id = str(ulid.new())
    filename = f"{case_id}.{ext}"
    face_name = f"{case_id}.jpeg"
    image_path = os.path.join(UPLOAD_DIR, filename)
    face_path = os.path.join(FACE_DIR, face_name)

    with open(image_path, "wb") as f:
        f.write(await file.read())

    try:
        image = Image.open(image_path).convert("RGB")
        image_np = np.array(image)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to process image")

    faces = app_face.get(image_np)
    if not faces:
        raise HTTPException(status_code=400, detail="No face detected")

    face = faces[0]
    bbox = face.bbox.astype(int)
    cropped_face = image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
    cropped_face.save(face_path)

    embedding = face.embedding.tolist()
    face_record = FaceCreate(
        person_id=person_id,
        embedding=embedding,
        photo_path=filename,
        is_male=face.gender,
        age=face.age
    )
    face_db = crud_face.create(db, face_record)
    minio_client.fput_object(settings.S3_BUCKET_FACE, filename, face_path)
    index_manager.add_embedding(embedding, person_id)
    os.remove(image_path)
    os.remove(face_path)
    return face_db

async def track_faces_and_embeddings(file: UploadFile, db: Session) -> List[TrackingMatchOut]:
    """Detect all faces and track each by comparing against the index."""
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in {"jpg", "jpeg", "png", "webp"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    case_id = str(ulid.new())
    filename = f"{case_id}.{ext}"
    temp_path = os.path.join(TEMP_DIR, filename)

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        image = Image.open(temp_path).convert("RGB")
        image_np = np.array(image)
    except Exception:
        os.remove(temp_path)
        raise HTTPException(status_code=400, detail="Failed to process image")

    faces = app_face.get(image_np)
    if not faces:
        os.remove(temp_path)
        raise HTTPException(status_code=400, detail="No face detected")

    results = []

    for i, face in enumerate(faces):
        bbox = face.bbox.astype(int)
        cropped_face = image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))

        # Save each face with unique filename
        face_filename = f"{case_id}_face_{i}.{ext}"
        face_path = os.path.join(TEMP_DIR, face_filename)
        cropped_face.save(face_path)

        embedding = face.embedding.tolist()
        result = index_manager.search(embedding, top_k=10)

        if not result.matches:
            os.remove(face_path)
            continue  # skip unmatched faces, optionally log or collect

        match = result.matches[0]
        person = crud_person.get(db, match.person_id)

        match_out = TrackingMatchOut(
            id=f"{case_id}_face_{i}",
            similarity=match.similarity,
            photo=face_filename,
            time_taken=result.search_time_ms,
            index_size=result.entries_searched,
            timestamp=datetime.now(UTC),
            person=PersonOut.model_validate(person)
        )
        results.append(match_out)
        os.remove(face_path)

    os.remove(temp_path)

    if not results:
        raise HTTPException(status_code=404, detail="No matches found for any faces")

    return results

def process_faces_from_image(file_path: str, camera_id: Optional[str], db: Session):
    try:
        image = Image.open(file_path).convert("RGB")
        image_np = np.array(image)
    except Exception as e:
        print(e)
        return

    faces = app_face.get(image_np)
    if not faces:
        print("❌ No face found")
        return
    print(f"😀 {len(faces)} Faces found ")

    for face in faces:
        try:
            bbox = face.bbox.astype(int)
            cropped_face = image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))

            face_id = str(ulid.new())
            cropped_filename = f"{face_id}.jpg"
            cropped_path = os.path.join(TEMP_DIR, cropped_filename)
            cropped_face.save(cropped_path)

            face_embedding = face.embedding.tolist()
            search_result = index_manager.search(face_embedding, top_k=10)

            if not search_result.matches:
                print("❌ NO FACE MATCH FOUND")
                os.remove(cropped_path)
                continue

            match = search_result.matches[0]
            print(f"✅ Match found: {match.person_id}")

            face_data = TrackingCreate(
                person_id=match.person_id,
                camera_id=camera_id,
                photo=cropped_filename,
                similarity=match.similarity,
                time_taken=search_result.search_time_ms,
                index_size=search_result.entries_searched
            )
            crud_tracking.create(db, face_data)
            minio_client.fput_object(settings.S3_BUCKET_DETECTED, cropped_filename, cropped_path)
            os.remove(cropped_path)
        except Exception as e:
            print(e)
            continue
    os.remove(file_path)
