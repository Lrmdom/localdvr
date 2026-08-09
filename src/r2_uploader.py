import os
import logging
import mimetypes
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
        """Envia o ficheiro para o R2 com chave estruturada por data e remove o ficheiro local."""
        if not os.path.exists(local_file_path):
            logger.error(f"Ficheiro não encontrado para upload: {local_file_path}")
            return False

        filename = os.path.basename(local_file_path)
        now = datetime.now()
        
        # Estrutura no Bucket: cameras/<nome>/YYYY/MM/DD/filename
        r2_key = f"cameras/{camera_name}/{now.strftime('%Y/%m/%d')}/{filename}"

        # Determinar o Content-Type
        content_type, _ = mimetypes.guess_type(local_file_path)
        if not content_type:
            content_type = "application/octet-stream"

        try:
            logger.info(f"A iniciar upload ({content_type}) -> R2: {r2_key}")
            self.s3_client.upload_file(
                Filename=local_file_path,
                Bucket=self.bucket_name,
                Key=r2_key,
                ExtraArgs={"ContentType": content_type}
            )
            logger.info(f"Upload concluído com sucesso: {r2_key}")

            # Remoção local segura
            os.remove(local_file_path)
            logger.info(f"Ficheiro local removido: {local_file_path}")
            return True

        except (BotoCoreError, ClientError) as e:
            logger.error(f"Erro ao enviar ficheiro {local_file_path} para o R2: {str(e)}")
            return False
    def list_objects(self, prefix: str):
        """Lista objetos no bucket com um prefixo específico."""
        try:
            logger.info(f"A listar R2 com prefixo: {prefix}")
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            contents = response.get("Contents", [])
            logger.info(f"Encontrados {len(contents)} objetos.")
            return contents
        except ClientError as e:
            logger.error(f"Erro ao listar objetos em {prefix}: {str(e)}")
            return []

    def generate_presigned_url(self, object_key: str, expiration: int = 3600):
        """Gera URL pré-assinada para acesso temporário ao objeto."""
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Erro ao gerar URL para {object_key}: {str(e)}")
            return None

