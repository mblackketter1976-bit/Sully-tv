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
