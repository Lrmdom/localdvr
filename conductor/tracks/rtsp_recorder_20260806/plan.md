# Implementation Plan: Implement RTSP Recorder Service

## Phase 1: Setup & Configuration [checkpoint: b7df14a]
- [x] Task: Set up project structure [aba3dea]
    - [x] Create `src/` directory
    - [x] Add `requirements.txt`
    - [x] Add `.env.example`
- [x] Task: Conductor - User Manual Verification 'Setup & Configuration' (Protocol in workflow.md)

## Phase 2: Core Service Implementation [checkpoint: 5d4d25c]
- [x] Task: Implement configuration management [95999e9]
    - [x] Create `src/config.py` using Pydantic
- [x] Task: Implement RTSP recording logic [3fd6b01]
    - [x] Create `src/rtsp_recorder.py` for FFmpeg interaction
- [x] Task: Conductor - User Manual Verification 'Core Service Implementation' (Protocol in workflow.md)

## Phase 3: Resilience & Upload Integration [checkpoint: 98fd00d]
- [x] Task: Implement R2 uploader [8c653c9]
    - [x] Create `src/r2_uploader.py` using boto3
- [x] Task: Implement main service entry point [55bab50]
    - [x] Create `main.py` to orchestrate recording, upload, and concurrency
- [x] Task: Conductor - User Manual Verification 'Resilience & Upload Integration' (Protocol in workflow.md)

## Phase 4: Containerization & Final Verification
- [~] Task: Add containerization
    - [~] Create `Dockerfile`
    - [~] Create `docker-compose.yml`
- [~] Task: Final verification
    - [~] Test recording and uploading with local setup
- [ ] Task: Conductor - User Manual Verification 'Containerization & Final Verification' (Protocol in workflow.md)
