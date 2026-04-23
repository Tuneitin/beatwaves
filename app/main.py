import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import get_settings
from app.core.database import create_tables
from app.routers import auth, tracks, payments, sales, royalties

settings = get_settings()

app = FastAPI(title=settings.app_name)
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


@app.get("/")
def root():
    return {"message": "BeatWave API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "healthy"}
