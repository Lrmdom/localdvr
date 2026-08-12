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

    def download_and_upload_resource(self, event_id: str, camera_name: str, label: str, resource_type: str, event_start_time: int):
        """
        resource_type pode ser 'clip' ou 'snapshot'
        """
        logger.info(f"A descarregar {resource_type} do evento {event_id} ({label}) da câmara {camera_name}")
        
        extension = "mp4" if resource_type == "clip" else "jpg"
        url_suffix = "clip.mp4" if resource_type == "clip" else "snapshot.jpg"
        
        try:
            resource_url = f"{settings.FRIGATE_URL}/api/events/{event_id}/{url_suffix}"
            response = requests.get(resource_url, stream=True, timeout=30)
            
            if response.status_code == 200:
                # Usa o start_time do evento, convertido para formato HHMMSS
                timestamp = datetime.fromtimestamp(event_start_time).strftime("%H%M%S")
                filename = f"event_{label}_{timestamp}_{resource_type}.{extension}"
                
                cam_dir = os.path.join(self.temp_dir, camera_name)
                os.makedirs(cam_dir, exist_ok=True)
                
                local_path = os.path.join(cam_dir, filename)
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"Download de {resource_type} concluído: {local_path}. A iniciar upload R2...")
                self.uploader.upload_and_cleanup(local_path, camera_name)
            else:
                logger.error(f"Erro ao obter {resource_type} do Frigate. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Exceção ao processar {resource_type} do evento {event_id}: {str(e)}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode('utf-8'))
            event_type = payload.get("type")
            after = payload.get("after", {})
            
            # Só queremos processar quando o evento termina
            if event_type == "end":
                event_id = after.get("id")
                camera = after.get("camera")
                label = after.get("label")
                start_time = after.get("start_time")
                has_clip = after.get("has_clip", False)
                has_snapshot = after.get("has_snapshot", False)
                
                logger.info(f"Evento finalizado detetado: {event_id} - {label} (Clip: {has_clip}, Snapshot: {has_snapshot})")
                
                # Descarrega Clip se existir
                if has_clip:
                    self.executor.submit(self.download_and_upload_resource, event_id, camera, label, "clip", start_time)
                
                # Descarrega Snapshot se existir
                if has_snapshot:
                    self.executor.submit(self.download_and_upload_resource, event_id, camera, label, "snapshot", start_time)
                
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
