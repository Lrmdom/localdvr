from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import os
from src.config import settings
from src.r2_uploader import R2Uploader
from src.tailscale_api import ts_api

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
    logger.info("Health check endpoint chamado")
    return {"status": "ok"}

@app.get("/api/cameras")
async def get_cameras():
    logger.info(f"Cameras endpoint chamado. Retornando {len(settings.cameras)} câmaras.")
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

@app.get("/api/access/status")
async def get_access_status():
    if not settings.TS_API_KEY:
        return {"configured": False, "reason": "TS_API_KEY não configurada"}
    
    device_id = await ts_api.get_device_id()
    if not device_id:
        return {"configured": False, "reason": "Dispositivo localdvr-server não encontrado no Tailscale"}
    
    shares = await ts_api.list_shares(device_id)
    return {
        "configured": True,
        "device_id": device_id,
        "active_shares": shares
    }

@app.post("/api/access/invite")
async def create_invite():
    device_id = await ts_api.get_device_id()
    if not device_id:
        return {"error": "Dispositivo não encontrado"}
    
    share = await ts_api.create_share_link(device_id)
    if not share:
        return {"error": "Falha ao gerar link de partilha. Verifique as permissões da API Key."}
    
    return share

@app.get("/api/live/{camera}")
async def get_live_stream(camera: str):
    """
    Proxy para o stream MJPEG em direto do Frigate.
    """
    import httpx
    from fastapi.responses import StreamingResponse
    
    frigate_live_url = f"{settings.FRIGATE_URL}/api/{camera}"
    
    async def stream_generator():
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream("GET", frigate_live_url, timeout=None) as response:
                    async for chunk in response.aiter_bytes():
                        yield chunk
            except Exception as e:
                logger.error(f"Erro no stream proxy para {camera}: {e}")

    return StreamingResponse(stream_generator(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/api/ptz/move")
async def ptz_move(camera: str, direction: str):
    """
    direction: 'left', 'right', 'up', 'down', 'stop'
    """
    import httpx
    # Se for a lsc_rotativa, usamos o go2rtc diretamente via Tuya PTZ
    if camera == "lsc_rotativa":
        go2rtc_url = f"http://go2rtc:1984/api/streams"
        params = {"src": camera, "ptz": direction.lower()}
        async with httpx.AsyncClient() as client:
            try:
                res = await client.post(go2rtc_url, params=params)
                return {"status": res.status_code, "detail": res.text}
            except Exception as e:
                return {"error": str(e)}
    
    # Fallback para o Frigate (ONVIF)
    frigate_url = f"{settings.FRIGATE_URL}/api/{camera}/ptz/move"
    params = {"action": direction.upper()}
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(frigate_url, params=params)
            return {"status": res.status_code, "detail": res.text}
        except Exception as e:
            return {"error": str(e)}

# Servir Frontend (Montado por último para ser a rota catch-all)
viewer_dist = os.path.join(os.path.dirname(__file__), "..", "viewer", "dist")
if os.path.exists(viewer_dist):
    app.mount("/", StaticFiles(directory=viewer_dist, html=True), name="viewer")
