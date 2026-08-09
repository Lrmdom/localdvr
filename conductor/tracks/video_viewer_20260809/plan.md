# Implementation Plan: Video Viewer and Event Client

This document outlines the step-by-step implementation plan for the LocalDVR Video Viewer and Event Client.

---

## Phase 1: Backend Development (FastAPI)

We will implement a lightweight, highly performant FastAPI backend. It integrates with our existing Cloudflare R2 structure to list objects and generate secure presigned play URLs.

### Step 1.1: Backend API Skeleton
- File: `src/api.py`
- Create FastAPI app instance.
- Setup CORS middleware to allow local development.
- Setup logging matching project style guides.

### Step 1.2: R2 Querying Logic
- File: `src/r2_uploader.py` (or as helper inside `src/api.py`)
- Add method to list objects under prefix: `cameras/{camera_name}/{year}/{month}/{day}/`.
- Add method to generate secure presigned GET URLs for a specific S3 key with a 1-hour expiration time.
- Implement robust error handling for API timeouts and S3 client exceptions.

### Step 1.3: Endpoints
- File: `src/api.py`
- Implement `GET /api/cameras`: Read list of active cameras from environment configurations or by listing the top-level keys in R2 (`cameras/*`).
- Implement `GET /api/videos?camera=<camera_name>&date=<YYYY-MM-DD>`:
  - Parse date into R2 folder format (`YYYY/MM/DD`).
  - Fetch objects, parse filenames (e.g., `video_142030.mp4` -> `14:20:30`), generate presigned URLs, and return JSON.

### Step 1.4: Unit Tests
- File: `tests/test_api.py`
- Create tests for both endpoints. Mock boto3 S3 client responses using `unittest.mock` to ensure test speed and reliability.

---

## Phase 2: Frontend Development (React + Vite)

We will build an ultra-responsive, beautiful dark-themed SPA in `viewer/` using React, TypeScript, and modern Vanilla CSS.

### Step 2.1: Scaffolding
- Command: Create React project in `viewer/` using Vite template.
- Add standard configurations (`vite.config.ts`, `tsconfig.json`).
- Ensure no Node.js runtime is needed on production—the client runs fully in the user's browser.

### Step 2.2: Styling & Visual Theme
- File: `viewer/src/index.css`
- Establish CSS Variables for dark mode (deep grays, crisp whites, alert greens, and accents).
- Setup clean global typography and interactive state transitions.

### Step 2.3: Components
- **`CameraSelector`**: Simple, intuitive selector sidebar/dropdown.
- **`DatePicker`**: Calendar selector for easy timeline browsing.
- **`Timeline`**:
  - Horizontal bar representing 24 hours of the day (0 to 1440 minutes).
  - Map each recording segment to its accurate percentage offset `(hours * 60 + minutes) / 1440` and highlight it.
  - Show a cursor indicating currently playing video's progress.
  - Support clicking on any highlighted block to jump directly to that video.
- **`VideoPlayer`**:
  - Wrap HTML5 `<video>` player.
  - Add speed control selector (1x, 1.5x, 2x, 4x) for rapid viewing.
  - Listen to `onEnded` event to automatically load and play the next chronological clip in the playlist.
- **`SegmentList`**: List view of all MP4 chunks for the day.

### Step 2.4: Integration State
- File: `viewer/src/App.tsx`
- Tie camera/date selection to API fetch.
- Handle loading states, empty folders (no videos found), and backend connection errors.

---

## Phase 3: Packaging & Integration

### Step 3.1: FastAPI Mount Static
- File: `src/api.py`
- If directory `viewer/dist` exists, mount it using `FastAPI.mount` or fallback to serving a default placeholder page. This allows running backend and frontend on a single port.

### Step 3.2: Multi-stage Dockerfile
- File: `Dockerfile`
- Update to support multi-stage:
  - **Stage 1 (Frontend Build):** Pull node:18-slim, copy `viewer/`, install dependencies, run build (`npm run build`).
  - **Stage 2 (Final Image):** Keep current Python setup, install system `ffmpeg`, copy static assets from Stage 1 into python workdir `viewer/dist`.

### Step 3.3: Docker Compose
- File: `docker-compose.yml`
- Update configuration to run the FastAPI API server on port `8000`.
- Combine both services (recording and web viewing) so they can run concurrently in the same or separate lightweight containers.

---

## Phase 4: Verification and Launch

1. **Verify recording service continues functioning independently.**
2. **Launch API & Viewer server locally.**
3. **Verify R2 listing and presigned URL streaming in Chrome/Safari/Firefox.**
4. **Ensure playback speed modification and chronological auto-play work correctly.**
