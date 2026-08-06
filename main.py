import asyncio
import logging
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

from src.config import settings
from src.r2_uploader import R2Uploader
from src.rtsp_recorder import RTSPRecorder

# Configuração de logs estruturados
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("Main")

async def shutdown(loop, executor, recorders):
    logger.info("A encerrar o serviço de gravação...")
    for recorder in recorders:
        recorder.stop()
    
    executor.shutdown(wait=False)
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

def main():
    cameras = settings.cameras
    if not cameras:
        logger.error("Nenhuma câmara configurada. Verifique o ficheiro .env.")
        sys.exit(1)

    logger.info(f"A inicializar o gravador para {len(cameras)} câmara(s).")

    # Inicializa o Uploader R2 e a Pool de Threads para uploads paralelos
    uploader = R2Uploader(
        account_id=settings.CLOUDFLARE_ACCOUNT_ID,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        bucket_name=settings.R2_BUCKET_NAME
    )
    
    executor = ThreadPoolExecutor(max_workers=len(cameras) * 2)
    recorders = []

    loop = asyncio.get_event_loop()

    for cam in cameras:
        recorder = RTSPRecorder(
            camera_name=cam.name,
            rtsp_url=cam.rtsp_url,
            segment_duration=settings.SEGMENT_DURATION_SECONDS,
            temp_dir=settings.TEMP_STORAGE_PATH,
            uploader=uploader,
            executor=executor
        )
        recorders.append(recorder)
        loop.create_task(recorder.start_recording_loop())

    # Gestão de sinais de encerramento (SIGINT/SIGTERM)
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(loop, executor, recorders)))

    try:
        loop.run_forever()
    finally:
        loop.close()
        logger.info("Aplicação encerrada com sucesso.")

if __name__ == "__main__":
    main()
