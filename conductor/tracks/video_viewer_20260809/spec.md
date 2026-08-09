# Specification: Video Viewer and Event Client

## Overview
Develop a web visualizer for LocalDVR. The system consists of a FastAPI backend to fetch video directories and generate presigned streaming URLs from Cloudflare R2, and a React (TypeScript + Vite) single-page application with a sleek dark-theme user interface featuring a visual timeline, calendar/date selector, camera selector, and responsive video player with custom controls.

---

## 1. Functional Requirements

### 1.1 Backend API (FastAPI)
- **Camera Registry:**
  - Expose `GET /api/cameras` to list configured camera names (parsed from env or derived from bucket folder structure).
- **Video & Event Directory:**
  - Expose `GET /api/videos` with query parameters `camera` (string) and `date` (string `YYYY-MM-DD`).
  - Retrieve list of MP4 files from Cloudflare R2 matching: `cameras/{camera}/{year}/{month}/{day}/video_{HHMMSS}.mp4`.
  - On the fly, generate short-lived (e.g., 1 hour) secure presigned URLs for each segment.
  - Return JSON array of segments, each containing:
    - `id`: unique file key/path
    - `filename`: e.g., `video_143000.mp4`
    - `time`: e.g., `14:30:00` (parsed from filename)
    - `timestamp`: complete ISO timestamp (date + time)
    - `url`: the generated presigned URL
    - `size`: size in bytes
- **Static Assets Host:**
  - Serve built React frontend assets from `viewer/dist` at the root path (`/`).

### 1.2 Frontend Application (React SPA)
- **Layout & Aesthetic:**
  - Modern Dark Mode by default.
  - Clean responsive grid layout (Sidebar for Camera + Date selection; Main panel for Video Player and Interactive Timeline).
- **Camera Selection:**
  - Easy-to-use camera selector showing all active security cameras.
- **Date Selector:**
  - Datepicker to select which day's recordings to view (default to today).
- **Interactive Timeline:**
  - A visual 24-hour timeline representing the selected day.
  - Blocks/bars showing recorded segments on the timeline. Clicking on a block loads and plays that segment instantly.
- **Segment Playlist:**
  - A chronological list of all segments for the day, allowing easy navigation.
- **Video Player:**
  - Native HTML5 `<video>` player supporting:
    - Custom play, pause, seek, volume controls.
    - Playback speed adjustment (1x, 1.5x, 2x, 4x) to easily scan hours of recording.
    - Continuous playback (auto-load and auto-play the next sequential segment when the current one ends).
- **LocalDVR Service Status:**
  - Minimal indicator of backend health and connection.

---

## 2. Technical Stack & Architecture

### Backend: FastAPI
- **Web framework:** FastAPI
- **S3 client:** boto3 (utilizing the same R2 configurations)
- **ASGI Server:** uvicorn

### Frontend: React (Vite)
- **Scaffolding:** Vite + React + TypeScript
- **State Management:** React state + context (no heavy state managers needed)
- **Styles:** Modern Vanilla CSS (Clean responsive layouts, CSS variables, dark theme variables)
- **HTTP Client:** Native Fetch API

### Deployment & Packaging
- Single-container multi-stage build:
  1. Build the React SPA into static files using `node:18-slim`.
  2. Copy built assets into Python container and serve via FastAPI static files mounting.
- Add FastAPI app launch command to existing `docker-compose.yml` or keep it running in parallel with the recording service.

---

## 3. Security & Resource Constraints
- **Presigned URLs:** URLs are generated on-the-fly and expire in 1 hour. Video files are kept completely private and secure inside R2. No public read permission is required on the bucket.
- **Zero Transcoding on Client:** Videos are streamed directly in their native captured format (H.264/AAC MP4). Browsers play them directly with hardware-accelerated decoding.
- **Minimal Server RAM/CPU:** The server only lists objects from R2 and signs URLs. No CPU-heavy video processing occurs on the local server for viewing.
