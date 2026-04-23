import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import get_settings
from app.core.database import create_tables
from app.core.logging_config import setup_logging
from app.routers import auth, tracks, payments, sales, royalties, artists

settings = get_settings()
setup_logging()

app = FastAPI(
    title=settings.app_name,
    description="Music distribution platform for African artists",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads/tracks", exist_ok=True)
os.makedirs("uploads/artwork", exist_ok=True)

app.mount("/files", StaticFiles(directory="uploads"), name="files")

app.include_router(auth.router)
app.include_router(tracks.router)
app.include_router(payments.router)
app.include_router(sales.router)
app.include_router(royalties.router)
app.include_router(artists.router)


@app.get("/")
def root():
    return {"message": "BeatWave API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}
