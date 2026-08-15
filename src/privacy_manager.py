import os
import logging
import requests
from pytapo import Tapo
from src.config import settings

logger = logging.getLogger(__name__)

class TuyaPrivacyManager:
    def __init__(self):
        self.client_id = os.getenv("TUYA_CLIENT_ID")
        self.secret = os.getenv("TUYA_CLIENT_SECRET")
        self.device_id = os.getenv("LSC_DEVICE_ID")
        self.base_url = os.getenv("TUYA_API_URL", "https://openapi.tuyaeu.com")

    def _get_token(self):
        url = f"{self.base_url}/v1.0/token?grant_type=1"
        resp = requests.get(url, auth=(self.client_id, self.secret))
        resp.raise_for_status()
        return resp.json()["result"]["access_token"]

    def set_privacy(self, enabled: bool):
        try:
            token = self._get_token()
            headers = {"access_token": token}
            url = f"{self.base_url}/v1.0/devices/{self.device_id}/commands"
            payload = {
                "commands": [{"code": "basic_private", "value": enabled}]
            }
            resp = requests.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            logger.info(f"Tuya privacy set to {enabled}")
        except Exception as e:
            logger.error(f"Failed to set Tuya privacy: {e}")
            raise

class TapoPrivacyManager:
    def __init__(self):
        self.ip = os.getenv("TAPO_IP")
        self.user = os.getenv("TAPO_USERNAME")
        self.password = os.getenv("TAPO_PASSWORD")

    def set_privacy(self, enabled: bool):
        try:
            tapo = Tapo(self.ip, self.user, self.password)
            tapo.setPrivacyMode(enabled)
            logger.info(f"Tapo privacy set to {enabled}")
        except Exception as e:
            logger.error(f"Failed to set Tapo privacy: {e}")
            raise

class PrivacyManager:
    def __init__(self):
        self.tuya = TuyaPrivacyManager()
        self.tapo = TapoPrivacyManager()

    def set_privacy_mode(self, camera_name: str, enabled: bool):
        """Alterna modo privacidade numa câmara específica."""
        if camera_name == "lsc_rotativa":
            self.tuya.set_privacy(enabled)
        elif camera_name == "tplink_exterior":
            self.tapo.set_privacy(enabled)
        else:
            raise ValueError(f"Câmara não suportada: {camera_name}")
