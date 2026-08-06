import os
import logging
from datetime import datetime
import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)

class R2Uploader:
    """Cliente especializado para gestão de uploads assíncronos no Cloudflare R2."""

    def __init__(self, account_id: str, access_key: str, secret_key: str, bucket_name: str):
        self.bucket_name = bucket_name
        self.endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
        
        self.s3_client = boto3.client(
            service_name="s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="auto",
            config=Config(
                signature_version="s3v4",
                retries={"max_attempts": 5, "mode": "standard"}
            )
        )

    def upload_and_cleanup(self, local_file_path: str, camera_name: str) -> bool:
        """Envia o ficheiro MP4 para o R2 com chave estruturada por data e remove o ficheiro local."""
        if not os.path.exists(local_file_path):
            logger.error(f"Ficheiro não encontrado para upload: {local_file_path}")
            return False

        filename = os.path.basename(local_file_path)
        now = datetime.now()
        
        # Estrutura no Bucket: cameras/<nome>/YYYY/MM/DD/video_HHMMSS.mp4
        r2_key = f"cameras/{camera_name}/{now.strftime('%Y/%m/%d')}/{filename}"

        try:
            logger.info(f"A iniciar upload -> R2: {r2_key}")
            self.s3_client.upload_file(
                Filename=local_file_path,
                Bucket=self.bucket_name,
                Key=r2_key,
                ExtraArgs={"ContentType": "video/mp4"}
            )
            logger.info(f"Upload concluído com sucesso: {r2_key}")

            # Remoção local segura
            os.remove(local_file_path)
            logger.info(f"Ficheiro local removido: {local_file_path}")
            return True

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Erro ao enviar ficheiro {local_file_path} para o R2: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Erro inesperado durante upload/limpeza: {str(e)}")
            return False
