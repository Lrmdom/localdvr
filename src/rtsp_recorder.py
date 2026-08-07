import os
import time
import subprocess
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from src.r2_uploader import R2Uploader

logger = logging.getLogger(__name__)

class RTSPRecorder:
    """Gerenciador de captura RTSP via FFmpeg com zero transcoding e resiliência de rede."""

    def __init__(
        self,
        camera_name: str,
        rtsp_url: str,
        segment_duration: int,
        temp_dir: str,
        uploader: R2Uploader,
        executor: ThreadPoolExecutor
    ):
        self.camera_name = camera_name
        self.rtsp_url = rtsp_url
        self.segment_duration = segment_duration
        self.temp_dir = os.path.join(temp_dir, camera_name)
        self.uploader = uploader
        self.executor = executor
        self.is_running = True

        os.makedirs(self.temp_dir, exist_ok=True)

    def _generate_output_path(self) -> str:
        timestamp = datetime.now().strftime("%H%M%S")
        return os.path.join(self.temp_dir, f"video_{timestamp}.mp4")

    def _build_ffmpeg_cmd(self, output_path: str) -> list:
        return [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "warning",
            "-rtsp_transport", "tcp",
            "-use_wallclock_as_timestamps", "1",
            "-i", self.rtsp_url,
            "-c:v", "copy",
            "-c:a", "aac",
            "-strict", "-2",
            "-reset_timestamps", "1",
            "-movflags", "+faststart",
            "-t", str(self.segment_duration),
            output_path
        ]

    async def start_recording_loop(self):
        """Loop contínuo de gravação de segmentos com retry exponencial em caso de falha."""
        retry_delay = 2
        max_retry_delay = 60

        logger.info(f"[{self.camera_name}] Serviço de gravação iniciado.")

        while self.is_running:
            current_output = self._generate_output_path()
            cmd = self._build_ffmpeg_cmd(current_output)

            logger.info(f"[{self.camera_name}] A gravar segmento: {os.path.basename(current_output)}")
            start_time = time.time()

            try:
                # Executa o FFmpeg como subprocesso assíncrono
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )

                _, stderr = await process.communicate()
                elapsed = time.time() - start_time

                if process.returncode == 0 and os.path.exists(current_output):
                    retry_delay = 2  # Reset do delay em caso de sucesso
                    
                    # Envia o ficheiro para o R2 em background sem bloquear o loop principal
                    asyncio.get_event_loop().run_in_executor(
                        self.executor,
                        self.uploader.upload_and_cleanup,
                        current_output,
                        self.camera_name
                    )
                else:
                    err_msg = stderr.decode().strip() if stderr else "Erro desconhecido"
                    logger.warning(f"[{self.camera_name}] FFmpeg encerrou com código {process.returncode}. Erro: {err_msg}")
                    
                    if os.path.exists(current_output) and os.path.getsize(current_output) == 0:
                        os.remove(current_output)

                    # Se a falha ocorreu imediatamente, aciona o backoff
                    if elapsed < 5:
                        logger.info(f"[{self.camera_name}] A aguardar {retry_delay}s antes de reconectar...")
                        await asyncio.sleep(retry_delay)
                        retry_delay = min(retry_delay * 2, max_retry_delay)

            except Exception as e:
                logger.error(f"[{self.camera_name}] Erro crítico no processo de captura: {str(e)}")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)

    def stop(self):
        self.is_running = False
