# Specification: Video Viewer and Event Client

## Overview
Develop a web visualizer for LocalDVR. The system consists of a FastAPI backend to fetch video directories and generate presigned streaming URLs from Cloudflare R2, and a React (TypeScript + Vite) single-page application with a sleek dark-theme user interface featuring a visual timeline, calendar/date selector, camera selector, and responsive video player with custom controls. The application will be a Progressive Web App (PWA) to support installation on mobile/desktop devices and secure instant Web Push notifications triggered by camera events.

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
- **Web Push Notification Services:**
  - Expose `GET /api/notifications/vapid-public-key`: Returns the VAPID public key.
  - Expose `POST /api/notifications/subscribe`: Persist a new push subscription JSON payload (endpoint, p256dh, auth) to local storage.
  - Expose `POST /api/notifications/unsubscribe`: Remove an existing subscription payload.
  - **Push Event Dispatcher:** On receiving a Frigate event (e.g. via MQTT in `frigate_listener.py`), sign a notification payload with VAPID keys and broadcast Web Push notifications to all active subscriptions using `pywebpush`.
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
  - Wrap HTML5 `<video>` player supporting playback speed adjustment (1x, 1.5x, 2x, 4x) and continuous playback.
- **PWA Capabilities:**
  - **Installability:** Fully configured web manifest and icons to allow users to add the viewer to their mobile Home Screen or desktop applications.
  - **Service Worker:** Register a service worker that caches essential UI assets for offline launch.
  - **Notification Controls:** A button/switch to register for notifications, which requests browser permission, creates a push subscription, and sends it to the backend.
  - **Push Event Handler:** Service Worker listens to `push` events, parses the JSON payload (containing title, body, camera name, and timestamp), and displays a system-level rich notification. Clicking the notification launches or focuses the PWA and deep-links to the corresponding camera and timeline event.
- **LocalDVR Service Status:**
  - Minimal indicator of backend health and connection.

---

## 2. Technical Stack & Architecture

### Backend: FastAPI
- **Web framework:** FastAPI
- **S3 client:** boto3 (utilizing the same R2 configurations)
- **ASGI Server:** uvicorn
- **Web Push Engine:** `pywebpush` (Python implementation of Web Push protocol)
- **Subscription Store:** A lightweight storage (SQLite or a persistent local JSON file) to keep subscription metadata.

### Frontend: React (Vite)
- **Scaffolding:** Vite + React + TypeScript
- **PWA Generator:** `@vite-pwa/plugin` (integrating Workbox)
- **State Management:** React state + context (no heavy state managers needed)
- **Styles:** Modern Vanilla CSS (Clean responsive layouts, CSS variables, dark theme variables)
- **HTTP Client:** Native Fetch API / PushManager / Notifications API

### Secure Context Configuration (HTTPS)
- Service workers and the Push API are restricted by browsers to **Secure Contexts (HTTPS)** (except for `localhost`).
- Since this is hosted locally, local IP access (e.g. `http://192.168.1.50:5173`) will fail to register the service worker or subscribe to push notifications.
- **Solution:** Utilize the existing `tailscale` container in `docker-compose.yml` with Tailscale MagicDNS and HTTPS enabled to generate a valid SSL certificate for free. Access the service using the secure Tailscale domain (e.g. `https://localdvr-server.your-tailnet.ts.net:8000`).

### Deployment & Packaging
- Single-container multi-stage build:
  1. Build the React PWA into static files using `node:20-slim`.
  2. Copy built assets into Python container and serve via FastAPI static files mounting.
- Add FastAPI app launch command to existing `docker-compose.yml` or keep it running in parallel with the recording service.

---

## 3. Security & Resource Constraints
- **VAPID Keypair Security:** Web Push payloads must be signed using VAPID. The private key must be kept secure in the server environment (via `.env` variable).
- **Presigned URLs:** URLs are generated on-the-fly and expire in 1 hour. Video files are kept completely private and secure inside R2. No public read permission is required on the bucket.
- **Zero Transcoding on Client:** Videos are streamed directly in their native captured format (H.264/AAC MP4). Browsers play them directly with hardware-accelerated decoding.
- **Minimal Server RAM/CPU:** The server only lists objects from R2 and signs URLs. No CPU-heavy video processing occurs on the local server for viewing.
