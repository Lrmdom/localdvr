import asyncio
import logging
import signal
import sys
from concurrent.futures import ThreadPoolExecutor

from src.config import settings
from src.r2_uploader import R2Uploader
from src.frigate_listener import FrigateListener

# Configuração de logs estruturados
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("Main")

async def shutdown(loop, executor, listener):
    logger.info("A encerrar o serviço do Frigate Listener...")
    listener.stop()
    
    executor.shutdown(wait=False)
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

def main():
    logger.info("A inicializar o LocalDVR como Frigate Uploader Orchestrator.")

    # Inicializa o Uploader R2 e a Pool de Threads
    uploader = R2Uploader(
        account_id=settings.CLOUDFLARE_ACCOUNT_ID,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        bucket_name=settings.R2_BUCKET_NAME
    )
    
    # Pool para o download/upload de vídeos do Frigate
    executor = ThreadPoolExecutor(max_workers=5)

    listener = FrigateListener(uploader, executor)

    loop = asyncio.get_event_loop()
    
    listener.start()

    # Gestão de sinais de encerramento (SIGINT/SIGTERM)
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(loop, executor, listener)))

    try:
        loop.run_forever()
    finally:
        loop.close()
        logger.info("Aplicação encerrada com sucesso.")

if __name__ == "__main__":
    main()
