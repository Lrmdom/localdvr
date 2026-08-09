from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
from src.config import settings
from src.r2_uploader import R2Uploader

# Configuração de logs
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(title="LocalDVR Viewer API")

# CORS para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar uploader
uploader = R2Uploader(
    account_id=settings.CLOUDFLARE_ACCOUNT_ID,
    access_key=settings.AWS_ACCESS_KEY_ID,
    secret_key=settings.AWS_SECRET_ACCESS_KEY,
    bucket_name=settings.R2_BUCKET_NAME
)

# API Routes (definidas primeiro)
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.get("/api/cameras")
async def get_cameras():
    return [cam.name for cam in settings.cameras]

@app.get("/api/videos")
async def get_videos(camera: str, date: str = Query(..., description="YYYY-MM-DD")):
    year, month, day = date.split("-")
    prefix = f"cameras/{camera}/{year}/{month}/{day}/"
    
    objects = uploader.list_objects(prefix)
    
    videos = []
    for obj in objects:
        key = obj["Key"]
        filename = key.split("/")[-1]
        
        label = "video"
        time_part = ""
        
        # Parse old format: video_HHMMSS.mp4 or new format: event_{label}_{timestamp}.mp4
        if filename.startswith("event_"):
            parts = filename.split("_")
            if len(parts) >= 3:
                label = parts[1]
                time_part = parts[-1].replace(".mp4", "")
        else:
            time_part = filename.split("_")[-1].replace(".mp4", "")
            
        if len(time_part) == 6:
            formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
        else:
            formatted_time = time_part # Fallback se falhar
            
        videos.append({
            "id": key,
            "filename": filename,
            "label": label,
            "time": formatted_time,
            "timestamp": f"{date}T{formatted_time}",
            "url": uploader.generate_presigned_url(key),
            "size": obj["Size"]
        })
    
    return sorted(videos, key=lambda x: x["timestamp"])

# Servir Frontend (Montado por último para ser a rota catch-all)
viewer_dist = os.path.join(os.path.dirname(__file__), "..", "viewer", "dist")
if os.path.exists(viewer_dist):
    app.mount("/", StaticFiles(directory=viewer_dist, html=True), name="viewer")
