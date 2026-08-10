from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
from src.config import settings
from src.r2_uploader import R2Uploader
from src.notifications import NotificationManager

# Configuração de logs
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(title="LocalDVR Viewer API")
notif_manager = NotificationManager()

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
        
        # Parse formats:
        # 1. video_HHMMSS.mp4 (old)
        # 2. event_{label}_{timestamp}.mp4 (medium)
        # 3. event_{label}_{timestamp}_{type}.{ext} (new)
        
        file_ext = filename.split(".")[-1]
        resource_type = "video" if file_ext == "mp4" else "snapshot"
        
        if filename.startswith("event_"):
            parts = filename.split("_")
            if len(parts) >= 4:
                # Format 3: event_{label}_{timestamp}_{type}.{ext}
                label = parts[1]
                time_part = parts[2]
                resource_type = parts[3].split(".")[0]
            elif len(parts) >= 3:
                # Format 2: event_{label}_{timestamp}.mp4
                label = parts[1]
                time_part = parts[2].split(".")[0]
            else:
                time_part = filename.replace(f".{file_ext}", "")
        else:
            # Format 1: video_HHMMSS.mp4
            time_part = filename.split("_")[-1].replace(f".{file_ext}", "")
            
        if len(time_part) == 6:
            formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
        else:
            formatted_time = time_part # Fallback se falhar
            
        videos.append({
            "id": key,
            "filename": filename,
            "label": label,
            "type": resource_type,
            "time": formatted_time,
            "timestamp": f"{date}T{formatted_time}",
            "url": uploader.generate_presigned_url(key),
            "size": obj["Size"]
        })
    
    return sorted(videos, key=lambda x: x["timestamp"])

@app.get("/api/notifications/vapid-public-key")
async def get_vapid_key():
    if not notif_manager.vapid_public_key:
        raise HTTPException(status_code=404, detail="VAPID key not configured")
    return {"publicKey": notif_manager.vapid_public_key}

@app.post("/api/notifications/subscribe")
async def subscribe(subscription: dict = Body(...)):
    notif_manager.save_subscription(subscription)
    return {"status": "ok"}

# Servir Frontend (Montado por último para ser a rota catch-all)
viewer_dist = os.path.join(os.path.dirname(__file__), "..", "viewer", "dist")
if os.path.exists(viewer_dist):
    app.mount("/", StaticFiles(directory=viewer_dist, html=True), name="viewer")
