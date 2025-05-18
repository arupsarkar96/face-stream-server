import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api.route_v1 import router
from app.core.faiss_manager import FaissIndexManager
from app.db.base import Base
from app.db.models.face import Face
from app.db.session import engine, SessionLocal

Base.metadata.create_all(bind=engine)

index_manager = None  # Global reference

@asynccontextmanager
async def lifespan(app: FastAPI):
    global index_manager
    index_manager = FaissIndexManager()

    if not index_manager.files_exist():
        print("No local index found. Building from database...")

        db = SessionLocal()
        try:
            faces = db.query(Face).all()
            embeddings = []
            metadata = []

            for face in faces:
                if not face.embedding or not face.person_id:
                    continue
                emb = face.embedding
                if isinstance(emb, str):
                    try:
                        emb = json.loads(emb)
                    except json.JSONDecodeError:
                        continue
                if isinstance(emb, list) and len(emb) == 512:
                    embeddings.append(emb)
                    metadata.append({"person_id": face.person_id})
        finally:
            db.close()

        if embeddings:
            index_manager.build(embeddings, metadata)
            print("FAISS index built and saved.")
        else:
            print("No valid embeddings found in DB.")
    else:
        print("Loaded FAISS index from disk.")

    yield
    # Cleanup if needed

app = FastAPI(title="Face Stream API Docs", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router, prefix="/api/v1")