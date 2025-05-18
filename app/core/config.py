from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = "HS256"
    REDIS_HOST: str = os.getenv("REDIS_HOST")
    REDIS_MATCHING_QUEUE: str = "FACE_MATCH"
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    S3_HOST: str = os.getenv("S3_HOST")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY")
    S3_BUCKET_FACE: str = os.getenv("S3_BUCKET_FACE")
    S3_BUCKET_DETECTED: str = os.getenv("S3_BUCKET_DETECTED")

settings = Settings()
