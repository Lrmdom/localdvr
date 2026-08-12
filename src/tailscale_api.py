import httpx
import logging
from src.config import settings

logger = logging.getLogger(__name__)

class TailscaleAPI:
    def __init__(self):
        self.api_key = settings.TS_API_KEY
        # Tentar usar a tailnet configurada, caso contrário '-'
        self.tailnet = settings.TAILNET or "-"
        self.base_url = f"https://api.tailscale.com/api/v2/tailnet/{self.tailnet}"
        self.auth = (self.api_key, "")

    async def get_token(self):
        """
        Obtém um token de acesso usando Client ID e Client Secret (OAuth).
        """
        # Se TAILNET contém o Client ID e API_KEY contém o Secret
        client_id = settings.TAILNET
        client_secret = settings.TS_API_KEY
        
        if not client_id or not client_secret:
            return None

        url = "https://api.tailscale.com/api/v2/oauth/token"
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, data=data)
                if response.status_code == 200:
                    return response.json().get("access_token")
                logger.error(f"Erro ao obter token OAuth: {response.status_code} - {response.text}")
                return None
            except Exception as e:
                logger.error(f"Exceção ao obter token OAuth: {e}")
                return None

    async def _get_headers(self):
        token = await self.get_token()
        if token:
            return {"Authorization": f"Bearer {token}"}
        # Fallback para Basic Auth se não for OAuth
        import base64
        auth_str = f"{self.api_key}:"
        encoded = base64.b64encode(auth_str.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    async def get_device_id(self, hostname="localdvr-server"):
        headers = await self._get_headers()
        # O endpoint de devices exige a tailnet no path ou '-' para a tailnet do token
        async with httpx.AsyncClient() as client:
            try:
                logger.info(f"A procurar dispositivo {hostname} na API Tailscale...")
                # Usamos '-' como tailnet por defeito para OAuth tokens
                url = f"https://api.tailscale.com/api/v2/tailnet/-/devices"
                response = await client.get(url, headers=headers, timeout=10.0)
                
                if response.status_code == 401:
                    logger.error("Tailscale API: Erro de autenticação (401). Verifique se a TS_API_KEY é uma 'API Access Token' e não uma 'Auth Key'.")
                    return None

                if response.status_code != 200:
                    logger.error(f"Erro ao listar dispositivos Tailscale: {response.status_code} - {response.text}")
                    return None
                
                devices = response.json().get("devices", [])
                for device in devices:
                    d_hostname = device.get("hostname", "")
                    # Procura por correspondência exata ou parcial para lidar com sufixos
                    if hostname == d_hostname or d_hostname.startswith(hostname):
                        logger.info(f"Dispositivo encontrado: {d_hostname} (ID: {device.get('id')})")
                        return device.get("id")
                
                logger.warning(f"Dispositivo {hostname} não encontrado na lista de {len(devices)} dispositivos.")
                return None
            except Exception as e:
                logger.error(f"Exceção ao contactar API Tailscale: {str(e)}")
                return None

    async def create_share_link(self, device_id):
        headers = await self._get_headers()
        url = f"https://api.tailscale.com/api/v2/device/{device_id}/shares"
        async with httpx.AsyncClient() as client:
            payload = {"invite": True}
            response = await client.post(url, json=payload, headers=headers)
            if response.status_code not in [200, 201]:
                logger.error(f"Erro ao criar partilha: {response.status_code} - {response.text}")
                return None
            return response.json()

    async def list_shares(self, device_id):
        headers = await self._get_headers()
        url = f"https://api.tailscale.com/api/v2/device/{device_id}/shares"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return []
            return response.json().get("shares", [])

ts_api = TailscaleAPI()
