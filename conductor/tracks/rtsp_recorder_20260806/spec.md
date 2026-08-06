# Specification: Implement RTSP Recorder Service

## Overview
Develop a robust, modular Python service to capture RTSP streams from local security cameras (e.g., TP-Link Tapo, LSC/Tuya), segment the video into MP4 files, and upload them to Cloudflare R2 automatically.

## Functional Requirements
- **Local Ingestion:** Capture RTSP streams using `ffmpeg` (via subprocess) with zero transcoding (codec copy).
- **Segmentation:** Segment continuous streams into configurable MP4 clips (e.g., 5 or 10 minutes).
- **R2 Integration:** Automatically upload clips to Cloudflare R2 using `boto3`.
- **Modularity:** Support for multiple cameras with structured bucket organization: `cameras/<camera_name>/YYYY/MM/DD/video_HHMMSS.mp4`.
- **Cleanup:** Automatically remove local files after successful upload.
- **Resilience:** Automatic retry/backoff mechanism for stream reconnection.
- **Configuration:** All settings managed via `.env` file (`python-dotenv`).

## Non-Functional Requirements
- **Resource Efficiency:** Minimize CPU and RAM usage by using codec copy.
- **Robustness:** Handle network/camera failures gracefully.
- **Concurrency:** Use asynchronous operations (`asyncio`, `ThreadPoolExecutor`) to ensure uploads do not block stream capture.
- **Observability:** Structured logging.

## Acceptance Criteria
- Service starts successfully and captures configured camera feeds.
- Clips are correctly uploaded to the specified R2 bucket.
- Files are cleaned up locally after upload.
- Resilience mechanisms successfully reconnect to interrupted streams.
- Service is containerized with Docker/Docker Compose.
