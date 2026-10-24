# Sully TV DVR — server recording foundation

The existing `index.html` is a static GitHub Pages application. Its `MediaRecorder` captures the video element in the **viewer's browser**. Closing the browser ends that capture; GitHub Pages cannot continue it.

## Free recording host

A computer that stays powered on can run FFmpeg and store recordings on its disk. No subscription is needed. This is a separate service, not a replacement for the working site.

### Prerequisites

- FFmpeg installed and accessible on PATH.
- Python 3.10+.
- Streams that permit recording and that FFmpeg can access directly. Some providers block recording or require DRM; do not bypass DRM.

### Local recording test

```sh
mkdir -p recordings
ffmpeg -nostdin -i "DIRECT_PERMITTED_STREAM_URL" -t 00:05:00 -c copy recordings/test.ts
```

This records for five minutes even if a phone browser closes, provided the **computer and FFmpeg process** stay running. Use a direct stream URL that you have rights to record, not a website URL.

### Next integration

1. Implement an authenticated local DVR API that accepts a selected channel URL and duration, starts FFmpeg as a detached managed job, and reports status.
2. Expose a recordings list, playback endpoint and DELETE endpoint with safe file identifiers.
3. Connect Sully TV's Record button to that API only after a DVR host address and access method are configured; retain the existing browser recorder as fallback.
4. For access from phones away from home, configure a secure private network connection. Do not publicly expose an unauthenticated recorder or arbitrary URL fetch endpoint.
5. Test supported HLS streams, storage capacity, reconnection and mobile browser compatibility.

**Important:** A continuously running free remote cloud DVR is not provided by GitHub Pages or by this repository. Running a home/store computer is the zero-subscription alternative. Recording availability depends on source rights, stream format, network reliability and disk space.

## Existing features to preserve

- Nicol's Station
- Robinson's Horror Channel
- Michele's Murder Mystery Channel (one L)
- Live channels, On Demand, favorites and history
- My Recordings with existing per-recording Delete button
- Mobile responsive layout and install shortcut

The current recordings are stored in browser IndexedDB, and deleting one there removes it from that browser only. Server recordings will need a separate server-side deletion route.


## DVR API prototype (added)

The repository now contains `dvr_server.py`. This is a **local prototype**, not yet connected to the website or deployed. The PC must remain on, with FFmpeg and the Python server running.

On Windows PowerShell, after installing FFmpeg and Python:

```powershell
$env:SULLY_DVR_TOKEN = python -c "import secrets; print(secrets.token_urlsafe(32))"
python dvr_server.py
```

Keep the generated token private. In a second PowerShell window, use the same token to call the API (do not share it or commit it). Endpoints:

- `POST /api/recordings` with JSON `{"url":"https://example.org/permitted-stream.m3u8","title":"My show","duration_seconds":1800}`
- `GET /api/recordings`
- `GET /api/recordings/{id}/download`
- `DELETE /api/recordings/{id}` (completed jobs only)

All requests require `Authorization: Bearer YOUR_TOKEN`. Default bind is `127.0.0.1:8765`; this intentionally is not accessible directly from a remote phone. A secure access design is required before linking the GitHub Pages site.

**Current limitations:** The server stores video files on disk but holds its recording index only in memory. After restarting the Python server, existing video files remain on disk but will not appear in the API list. There is no stop-recording endpoint yet; jobs stop after the requested duration. No cross-device web UI, automatic startup, durable job catalog, HTTPS tunnel, or real-world stream test has been implemented. The current browser recorder remains the website's only active recording interface.
