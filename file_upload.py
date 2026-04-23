import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException
from app.core.config import get_settings

settings = get_settings()

ALLOWED_AUDIO = {"audio/mpeg", "audio/wav", "audio/flac", "audio/x-flac", "audio/mp3"}
ALLOWED_IMAGE = {"image/jpeg", "image/png", "image/webp"}

UPLOAD_DIR = "uploads"


async def save_track_file(file: UploadFile, artist_id: int) -> str:
    if file.content_type not in ALLOWED_AUDIO:
        raise HTTPException(400, f"Invalid audio format: {file.content_type}. Use MP3, WAV, or FLAC.")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise HTTPException(400, f"File too large ({size_mb:.1f}MB). Max is {settings.max_upload_size_mb}MB.")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = f"{artist_id}_{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_DIR, "tracks", filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    async with aiofiles.open(path, "wb") as f:
        await f.write(content)

    return f"/files/tracks/{filename}"


async def save_artwork_file(file: UploadFile, artist_id: int) -> str:
    if file.content_type not in ALLOWED_IMAGE:
        raise HTTPException(400, f"Invalid image format. Use JPG or PNG.")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > 20:
        raise HTTPException(400, "Artwork too large. Max 20MB.")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = f"{artist_id}_{uuid.uuid4().hex}.{ext}"
    path = os.path.join(UPLOAD_DIR, "artwork", filename)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    async with aiofiles.open(path, "wb") as f:
        await f.write(content)

    return f"/files/artwork/{filename}"
