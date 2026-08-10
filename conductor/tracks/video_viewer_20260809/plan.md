# Implementation Plan: Video Viewer and Event Client

This document outlines the step-by-step implementation plan for the LocalDVR Video Viewer and Event Client.

---

## Phase 1: Backend Development (FastAPI)

We will implement a lightweight, highly performant FastAPI backend. It integrates with our existing Cloudflare R2 structure to list objects and generate secure presigned play URLs, and manages PWA Web Push subscription metadata.

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

### Step 1.3: Subscription Storage & VAPID Config
- File: `src/notifications.py` (New file)
- Implement subscription data store (either simple persistent local JSON file or a lightweight SQLite table).
- Handle VAPID keys generation and persistence. If VAPID keys are missing in the environment or files, generate them automatically.
- Integrate `pywebpush` client to construct and send authenticated payloads to subscriber browser push service endpoints.

### Step 1.4: Endpoints
- File: `src/api.py`
- Implement `GET /api/cameras`: Read list of active cameras.
- Implement `GET /api/videos?camera=<camera_name>&date=<YYYY-MM-DD>`: Query segments from R2.
- Implement Web Push API endpoints:
  - `GET /api/notifications/vapid-public-key`: Return the VAPID public key.
  - `POST /api/notifications/subscribe`: Accept JSON body with push subscription endpoint and credentials, store it locally.
  - `POST /api/notifications/unsubscribe`: Accept endpoint identifier, remove it from store.

### Step 1.5: Frigate MQTT Event Broadcast integration
- File: `src/frigate_listener.py`
- Inject the push dispatcher into `FrigateListener`.
- When an event occurs (e.g. `person` detected, event begins or ends), trigger Web Push broadcast. The notification body should contain details such as camera name, event type, timestamp, and a deep-link url.

### Step 1.6: Unit Tests
- File: `tests/test_api.py`
- Create tests for R2 endpoints and Notification endpoints.
- Mock boto3 S3 responses and mock `pywebpush.webpush` HTTP requests to keep tests offline, fast, and reliable.

---

## Phase 2: Frontend Development (React + Vite)

We will build an ultra-responsive, beautiful dark-themed SPA in `viewer/` using React, TypeScript, and modern Vanilla CSS. We will construct it as an installable PWA with push notification support.

### Step 2.1: Scaffolding
- Command: Create React project in `viewer/` using Vite template.
- Add standard configurations (`vite.config.ts`, `tsconfig.json`).
- Ensure no Node.js runtime is needed on production—the client runs fully in the user's browser.

### Step 2.2: PWA Configuration (Vite-PWA)
- File: `viewer/vite.config.ts` and `viewer/package.json`
- Install `@vite-pwa/plugin`.
- Configure `VitePWA` plugin:
  - Set `registerType: 'autoUpdate'`.
  - Provide complete `manifest` configuration (name, short_name, theme_color, background_color, start_url, display: "standalone", icons).
  - Configure caching of static assets (JS, CSS, HTML, SVG, PNG) using Workbox strategies.

### Step 2.3: Service Worker custom code for Push handling
- File: `viewer/src/sw.ts` (or standard Service Worker template)
- Listen to the standard `push` browser event:
  - Parse received JSON payload containing notification text, title, and actions.
  - Call `self.registration.showNotification(title, options)`.
- Listen to `notificationclick` event:
  - Prevent default behavior.
  - Inspect action parameters and deep-link payload.
  - Open PWA window if not open, and navigate to the correct camera and date/time event.

### Step 2.4: Styling & Visual Theme
- File: `viewer/src/index.css`
- Establish CSS Variables for dark mode (deep grays, crisp whites, alert greens, and accents).
- Setup clean global typography and interactive state transitions.

### Step 2.5: Components
- **`CameraSelector`**: Simple, intuitive selector sidebar/dropdown.
- **`DatePicker`**: Calendar selector for easy timeline browsing.
- **`Timeline`**:
  - Horizontal bar representing 24 hours of the day (0 to 1440 minutes).
  - Map each recording segment to its accurate percentage offset `(hours * 60 + minutes) / 1440` and highlight it.
  - Show a cursor indicating currently playing video's progress.
  - Support clicking on any highlighted block to jump directly to that video.
- **`VideoPlayer`**: Wrap HTML5 `<video>` player supporting playback speed adjustment (1x, 1.5x, 2x, 4x) and continuous playback.
- **`NotificationToggle`**: Simple UI element to request notifications permissions, call browser subscribe APIs, and POST the subscription payload to the backend server.
- **`SegmentList`**: List view of all MP4 chunks for the day.

### Step 2.6: Integration State
- File: `viewer/src/App.tsx`
- Tie camera/date selection to API fetch.
- Handle loading states, empty folders (no videos found), and backend connection errors.
- Sync active notification states and subscriptions.

---

## Phase 3: Packaging & Integration

### Step 3.1: FastAPI Mount Static
- File: `src/api.py`
- If directory `viewer/dist` exists, mount it using `FastAPI.mount` or fallback to serving a default placeholder page. This allows running backend and frontend on a single port.

### Step 3.2: Multi-stage Dockerfile
- File: `Dockerfile`
- Update to support multi-stage:
  - **Stage 1 (Frontend Build):** Pull node:20-slim, copy `viewer/`, install dependencies, run build (`npm run build`).
  - **Stage 2 (Final Image):** Keep current Python setup, install system `ffmpeg` and Python packages (including `pywebpush`), copy static assets from Stage 1 into python workdir `viewer/dist`.

### Step 3.3: Docker Compose
- File: `docker-compose.yml`
- Update configuration to run the FastAPI API server on port `8000`.
- Combine both services (recording and web viewing) so they can run concurrently in the same or separate lightweight containers.

### Step 3.4: Secure local tunnels (Tailscale HTTPS Setup)
- Document setup steps to connect to the PWA over HTTPS:
  - Ensure the Tailscale container has access key auth.
  - Run `tailscale cert localdvr-server.your-tailnet.ts.net` to verify automated Let's Encrypt setup.
  - Configure the backend or reverse-proxy to serve secure traffic.

---

## Phase 4: Verification and Launch

1. **Verify recording service continues functioning independently.**
2. **Launch API & Viewer server locally.**
3. **PWA installation test:** Open browser over local HTTPS, confirm "Add to Home Screen" option is available.
4. **Push notifications test:** Trigger a test MQTT event on MQTT broker, confirm immediate pop-up notification delivery on both desktop and mobile platforms.
5. **Ensure video playback speed modification and chronological auto-play work correctly.**
