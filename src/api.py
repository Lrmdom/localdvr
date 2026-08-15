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
    
    grouped_events = {}
    
    for obj in objects:
        key = obj["Key"]
        filename = key.split("/")[-1]
        
        # Parse filename to get group key
        # Format: event_{label}_{timestamp}_{type}.{ext}
        if not filename.startswith("event_"):
            continue
            
        parts = filename.split("_")
        if len(parts) < 4:
            continue
            
        label = parts[1]
        time_part = parts[2]
        resource_type = parts[3].split(".")[0]
        event_key = f"{label}_{time_part}"
        
        if event_key not in grouped_events:
            formatted_time = f"{time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
            grouped_events[event_key] = {
                "id": event_key,
                "label": label,
                "time": formatted_time,
                "timestamp": f"{date}T{formatted_time}",
                "snapshot_url": None,
                "video_url": None
            }
        
        url = uploader.generate_presigned_url(key)
        if resource_type == "snapshot":
            grouped_events[event_key]["snapshot_url"] = url
        elif resource_type == "clip":
            grouped_events[event_key]["video_url"] = url
            
    # Converter para lista e ordenar
    events = list(grouped_events.values())
    return sorted(events, key=lambda x: x["timestamp"], reverse=True)

@app.get("/api/access/status")
async def get_access_status():
    if not settings.TS_API_KEY:
        return {"configured": False, "reason": "TS_API_KEY não configurada"}
    
    device_id = await ts_api.get_device_id()
    if not device_id:
        return {"configured": False, "reason": "Dispositivo localdvr-server não encontrado no Tailscale"}
    
    shares = await ts_api.list_shares(device_id)
    invitations = await ts_api.list_invitations()
    return {
        "configured": True,
        "device_id": device_id,
        "active_shares": shares,
        "active_invitations": invitations
    }

@app.get("/api/access/users")
async def get_users():
    return await ts_api.list_users()

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

import tinytuya
import os

@app.post("/api/ptz/move")
async def ptz_move(data: dict):
    """
    data: {"camera": str, "direction": str}
    """
    logger.info(f"PTZ request received: {data}")
    camera_name = data.get("camera")
    direction = data.get("direction", "stop").lower()

    if camera_name == "lsc_rotativa":
        try:
            # Inicializar câmara Tuya com OutletDevice
            d = tinytuya.OutletDevice(
                dev_id=os.getenv("LSC_DEVICE_ID"),
                address=os.getenv("LSC_IP"),
                local_key=os.getenv("LSC_LOCAL_KEY")
            )
            version = os.getenv("LSC_VERSION", "3.3")
            d.set_version(float(version))
            
            # Garantir que o modo de privacidade está desativado (DP 105)
            d.set_value(105, False)
            
            # Mapeamento DP 119
            commands = {
                "up": 0,
                "right": 2,
                "down": 4,
                "left": 6
            }
            
            if direction in commands:
                # Enviar comando no DP 119
                d.set_value(119, commands[direction])
            
            return {"status": 200, "detail": f"PTZ command {direction} sent to Tuya"}
            
        except Exception as e:
            logger.error(f"Tuya error: {e}")
            return {"status": 500, "error": str(e)}

    # Fallback para o Frigate (ONVIF via API Frigate)
    frigate_url = f"{settings.FRIGATE_URL}/api/{camera_name}/ptz/move"
    params = {"action": direction.upper()}
    logger.info(f"Sending to Frigate: {frigate_url} with params {params}")
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(frigate_url, params=params)
            logger.info(f"Frigate response: {res.status_code} {res.text}")
            return {"status": res.status_code, "detail": res.text}
        except Exception as e:
            logger.error(f"Error calling Frigate: {e}")
            return {"status": 500, "error": str(e)}

# Servir Frontend (Montado por último para ser a rota catch-all)
viewer_dist = os.path.join(os.path.dirname(__file__), "..", "viewer", "dist")
if os.path.exists(viewer_dist):
    app.mount("/", StaticFiles(directory=viewer_dist, html=True), name="viewer")
