# Sully TV — DVR feasibility and verification gate (2026-10-25)

Status: **CODE AUDITED; NO SERVER DVR IMPLEMENTED OR VERIFIED.** This note is on the development branch only.

## Confirmed from current index.html
- Recording captures `player.captureStream()` with `MediaRecorder` in the browser.
- `recorder.start(1000)` collects chunks in memory; `onstop` assembles a Blob.
- Completed recordings go into browser-local IndexedDB `sully-recordings/clips`; fallback is a local download.
- UI already says **Keep this page open**. Recording cannot continue reliably after browser/tab closure, phone suspension, or device shutdown.
- A GitHub Pages/static site and service worker do not provide a continuously running recording server.

## Design decision
Do not imply browser recording is server DVR. Keep the existing local recorder and delete/playback functionality. Do not promise unattended recording until a legally permitted, persistent, server-side capture/storage/retention service exists with a sustainable zero-cost budget. A user's own always-on PC could technically run a recorder but depends on power, bandwidth, storage, authorization to record each stream, and secure remote access; it is not a free cloud DVR and is **not implemented**.

## Verification matrix (not yet run)
1. Desktop Chrome: permitted source starts/stops, playable recording, survives page reload, individual delete.
2. Android Chrome: same; verify screen lock/background behavior separately.
3. iOS Safari: capability detection, no false record button on unsupported streams.
4. Storage quota: full/denied storage fallback, no false “saved” message.
5. Playback: channel switching, HLS fallback, guide, search, language, Michelle's channel.
6. Mobile layouts: 320/390/768 px and desktop; keyboard/TV remote focus.
7. Guide CSS pilot: inspect visual layout and overflow; do not merge until tested.

## Pass criteria
A feature is not marked verified until tested in a real browser/device. Server DVR remains **blocked by architecture and operating constraints**. Never represent a simulated timer or background service worker as persistent recording.
