# Initial Concept

Atua como um Engenheiro de Software Sénior especialista em Python, streaming de vídeo (RTSP/FFmpeg), resiliência de processos e integração de armazenamento em nuvem (Cloudflare R2 / S3 API).

Preciso que desenvolvas um serviço completo, robusto e modular em Python projetado para ser executado num ambiente de servidor local (como um Mini PC, Raspberry Pi ou servidor doméstico). O serviço deve capturar os fluxos de vídeo RTSP de câmaras de segurança da rede local (como TP-Link Tapo e LSC/Tuya Smart), segmentar o vídeo em ficheiros MP4 e enviar automaticamente os clips finalizados para um bucket no Cloudflare R2.

---

### 1. REQUISITOS TÉCNICOS & ARQUITETURA

1. **Processamento Local & Ingestão RTSP (Zero Transcoding):**
   - Utilizar `ffmpeg` (via subprocess do Python) para capturar o stream RTSP direto da câmara na rede local.
   - Forçar a cópia direta de codecs (`-c:v copy -c:a copy` ou `-an` se não houver áudio) para garantir o menor consumo possível de CPU e memória RAM no equipamento local.
   - Segmentar a transmissão contínua em ficheiros MP4 locais temporários (ex: clips configuráveis de 5 ou 10 minutos).
   - Implementar resiliência e auto-recuperação: se a transmissão RTSP falhar, o Wi-Fi desconectar ou a câmara reiniciar, o processo deve apanhar a exceção, gerir a reconexão automática com um mecanismo de retry/backoff e retomar a captura.

2. **Integração com Cloudflare R2 (`boto3`):**
   - Utilizar a biblioteca oficial `boto3` configurada explicitamente para comunicar com o endpoint S3 do Cloudflare R2 (`https://<account_id>.r2.cloudflarestorage.com`).
   - Implementar uma fila de uploads assíncrona em segundo plano (usando `asyncio`, `concurrent.futures.ThreadPoolExecutor` ou `queue.Queue`) para que o upload dos ficheiros MP4 finalizados ocorra sem interromper a captura do stream.
   - Organizar a estrutura de pastas no Bucket R2 no formato:
     `cameras/<nome_da_camara>/YYYY/MM/DD/video_HHMMSS.mp4`
   - Implementar uma rotina de limpeza local (`os.remove`) para apagar o ficheiro temporário do disco rígido imediatamente após a confirmação de sucesso do upload para o R2.

3. **Arquitetura Modular (Suporte para Múltiplas Câmaras):**
   - Estruturar o código para permitir a adição de múltiplos feeds de câmara no mesmo serviço (ex: a câmara TP-Link via RTSP direto e notas/abstração para o ecossistema LSC/Tuya via RTSP local ou integração OpenAPI).

4. **Configuração via Ficheiro `.env`:**
   - Carregar todas as definições e credenciais a partir de variáveis de ambiente utilizando a biblioteca `python-dotenv`:
     - `CLOUDFLARE_ACCOUNT_ID`
     - `AWS_ACCESS_KEY_ID` (R2 Access Key)
     - `AWS_SECRET_ACCESS_KEY` (R2 Secret Key)
     - `R2_BUCKET_NAME`
     - `CAMERA_1_NAME`
     - `CAMERA_1_RTSP_URL` (ex: rtsp://user:pass@192.168.1.X:554/stream1)
     - `SEGMENT_DURATION_SECONDS` (ex: 300)
     - `TEMP_STORAGE_PATH` (diretório local temporário para a gravação dos clips)

---

### 2. ENTREGÁVEIS ESPERADOS

1. **Estrutura de Ficheiros e Código-Fonte em Python:**
   - `main.py` (ponto de entrada da aplicação, gestão de concorrência e inicialização).
   - Módulos organizados para o cliente R2 (`r2_uploader.py`), captura RTSP/FFmpeg (`rtsp_recorder.py`) e gestão de configuração.
   - Código limpo, assíncrono, fortemente tipado (usando Type Hints) e com registos de logs estruturados utilizando a biblioteca `logging`.
2. **`requirements.txt`:**
   - Lista detalhada de dependências em Python (`boto3`, `python-dotenv`, etc.).
3. **`.env.example`:**
   - Modelo com o exemplo de todas as variáveis de ambiente necessárias.
4. **`Dockerfile` e `docker-compose.yml`:**
   - Ficheiros de conteneurização prontos para produção baseados numa imagem Linux leve (ex: `python:3.11-slim`) com a instalação do pacote do sistema `ffmpeg`.
5. **Guia Rápido de Instalação e Execução:**
   - Passos claros para configurar o Bucket no Cloudflare R2, gerar as credenciais S3 API Tokens e rodar a aplicação via Docker ou ambiente virtual (`venv`).
