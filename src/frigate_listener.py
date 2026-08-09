import os
import json
import logging
import requests
import paho.mqtt.client as mqtt
from concurrent.futures import ThreadPoolExecutor
from src.config import settings
from src.r2_uploader import R2Uploader
from datetime import datetime

logger = logging.getLogger(__name__)

class FrigateListener:
    def __init__(self, uploader: R2Uploader, executor: ThreadPoolExecutor):
        self.uploader = uploader
        self.executor = executor
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.temp_dir = settings.TEMP_STORAGE_PATH

        os.makedirs(self.temp_dir, exist_ok=True)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Conectado ao MQTT Broker com sucesso.")
            client.subscribe("frigate/events")
        else:
            logger.error(f"Falha ao conectar ao MQTT. Código de erro: {rc}")

    def download_and_upload_event(self, event_id: str, camera_name: str, label: str):
        logger.info(f"A descarregar evento {event_id} ({label}) da câmara {camera_name}")
        try:
            # Frigate API url for the clip
            clip_url = f"{settings.FRIGATE_URL}/api/events/{event_id}/clip.mp4"
            response = requests.get(clip_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                timestamp = datetime.now().strftime("%H%M%S")
                # Format: event_{label}_{timestamp}.mp4
                filename = f"event_{label}_{timestamp}.mp4"
                
                # Make sure camera dir exists
                cam_dir = os.path.join(self.temp_dir, camera_name)
                os.makedirs(cam_dir, exist_ok=True)
                
                local_path = os.path.join(cam_dir, filename)
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"Download concluído: {local_path}. A iniciar upload R2...")
                self.uploader.upload_and_cleanup(local_path, camera_name)
            else:
                logger.error(f"Erro ao obter clip do Frigate. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Exceção ao processar evento {event_id}: {str(e)}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            event_type = payload.get("type")
            after = payload.get("after", {})
            
            # Só queremos processar quando o evento termina e o vídeo está guardado
            if event_type == "end" and after.get("has_clip"):
                event_id = after.get("id")
                camera = after.get("camera")
                label = after.get("label")
                
                logger.info(f"Novo evento finalizado do Frigate detectado: {event_id} - {label}")
                
                # Descarrega e faz upload no background para não bloquear o loop MQTT
                self.executor.submit(self.download_and_upload_event, event_id, camera, label)
                
        except json.JSONDecodeError:
            pass
        except Exception as e:
            logger.error(f"Erro ao processar mensagem MQTT: {str(e)}")

    def start(self):
        logger.info(f"A iniciar FrigateListener, conectando a {settings.MQTT_HOST}:{settings.MQTT_PORT}...")
        try:
            self.mqtt_client.connect(settings.MQTT_HOST, settings.MQTT_PORT, 60)
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.error(f"Não foi possível conectar ao MQTT: {str(e)}")

    def stop(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
