import json
import os
from typing import List
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class CameraConfig(BaseModel):
    name: str
    rtsp_url: str

class Settings(BaseSettings):
    CLOUDFLARE_ACCOUNT_ID: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    R2_BUCKET_NAME: str
    SEGMENT_DURATION_SECONDS: int = 300
    TEMP_STORAGE_PATH: str = "./temp_recordings"
    LOG_LEVEL: str = "INFO"
    CAMERAS_RAW: str = Field(alias="CAMERAS", default="[]")
    
    # MQTT & Frigate
    MQTT_HOST: str = "localhost" # 'mqtt' se rodar dentro do container na mesma rede
    MQTT_PORT: int = 1883
    FRIGATE_URL: str = "http://localhost:5050" # 'http://frigate:5000' se via docker

    @property
    def r2_endpoint_url(self) -> str:
        return f"https://{self.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com"

    @property
    def cameras(self) -> List[CameraConfig]:
        try:
            raw_data = json.loads(self.CAMERAS_RAW)
            return [CameraConfig(**item) for item in raw_data]
        except Exception:
            # Fallback para parsing manual caso as variáveis retrocompatíveis CAMERA_1 existam
            cam_name = os.getenv("CAMERA_1_NAME", "camera_default")
            cam_url = os.getenv("CAMERA_1_RTSP_URL", "")
            if cam_url:
                return [CameraConfig(name=cam_name, rtsp_url=cam_url)]
            return []

settings = Settings()
