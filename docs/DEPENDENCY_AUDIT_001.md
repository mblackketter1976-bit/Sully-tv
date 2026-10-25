# Dependency and resilience audit — Sully TV (2026-10-25)

Status: initial source inspection, not browser-verified.

## Confirmed source observations
- `index.html` loads HLS.js from `https://cdn.jsdelivr.net/npm/hls.js@1/dist/hls.min.js`. If that CDN fails, JavaScript HLS playback may be affected on browsers lacking native support. Next step: inspect the actual player fallback path, review HLS.js license, and evaluate self-hosting a pinned build with integrity checks. Do not assume bundling alone solves live stream availability.
- `manifest.webmanifest` exists and declares standalone display, scope, start URL and three icon references. Manifest syntax is valid JSON based on manual inspection, but referenced assets and installation are not yet verified.
- `sw.js` uses a network-first cache strategy for a small app shell, with cache name `sully-tv-shell-v1`. The shell includes the main HTML, manifest, SVG icon and cinematic logo image. The worker catches precache errors and still calls skipWaiting, so missing shell assets can leave an incomplete offline cache without a visible install failure.
- The worker only intercepts same-origin GET requests for shell paths. It does not cache remote streams or implement background DVR.
- The first several hundred lines of `index.html` show extensive accumulated CSS overrides, responsive navigation rules, and custom theming. This warrants visual regression tests before cleanup.
- `service-worker.js` is not present at the tested path; `sw.js` is present. Confirm actual registration path in later JS before changing anything.

## New regression safety net
`scripts/check_static.py` is a standard-library-only, read-only smoke check. It checks expected core files, basic HTML markers, manifest icon file references, and flags CDN/browser recording dependencies. It is not a browser test, has not yet been executed against a full checkout, and does not establish PWA installability or stream functionality.

## Next technical actions
1. Obtain a full repository checkout; run the static check and resolve any missing asset errors.
2. Inspect the complete JS, source URLs, error handling, service worker registration, and third-party API calls.
3. Build a legal-source inventory and identify unavailable streams, content-rights concerns, and graceful fallbacks.
4. Add browser tests for phone/tablet/desktop, guide navigation, player, install, recording and deletion.
5. Evaluate pinned self-hosted HLS.js, cache updates, and modularizing repeated CSS with snapshot-based verification.

## Release discipline
No live deployment changes were made. This audit is a working document and must be updated with measured test results.
