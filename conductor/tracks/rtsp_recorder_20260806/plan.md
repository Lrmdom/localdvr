# Implementation Plan: Implement RTSP Recorder Service

## Phase 1: Setup & Configuration [checkpoint: b7df14a]
- [x] Task: Set up project structure [aba3dea]
    - [x] Create `src/` directory
    - [x] Add `requirements.txt`
    - [x] Add `.env.example`
- [x] Task: Conductor - User Manual Verification 'Setup & Configuration' (Protocol in workflow.md)

## Phase 2: Core Service Implementation
- [x] Task: Implement configuration management [95999e9]
    - [x] Create `src/config.py` using Pydantic
- [~] Task: Implement RTSP recording logic
    - [~] Create `src/rtsp_recorder.py` for FFmpeg interaction
- [ ] Task: Conductor - User Manual Verification 'Core Service Implementation' (Protocol in workflow.md)

## Phase 3: Resilience & Upload Integration
- [ ] Task: Implement R2 uploader
    - [ ] Create `src/r2_uploader.py` using boto3
- [ ] Task: Implement main service entry point
    - [ ] Create `main.py` to orchestrate recording, upload, and concurrency
- [ ] Task: Conductor - User Manual Verification 'Resilience & Upload Integration' (Protocol in workflow.md)

## Phase 4: Containerization & Final Verification
- [ ] Task: Add containerization
    - [ ] Create `Dockerfile`
    - [ ] Create `docker-compose.yml`
- [ ] Task: Final verification
    - [ ] Test recording and uploading with local setup
- [ ] Task: Conductor - User Manual Verification 'Containerization & Final Verification' (Protocol in workflow.md)
