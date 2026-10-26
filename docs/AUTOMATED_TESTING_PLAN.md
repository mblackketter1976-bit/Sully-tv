# Automated verification plan — Blackketter Entertainment

## Current status
The read-only `scripts/check_static.py` exists on development branch `sully-phase1-foundation-audit`. It has not yet been run against a full local repository checkout in this session.

## Run the check
From the repository root, use `python scripts/check_static.py` on Windows or `python3 scripts/check_static.py` on macOS/Linux.

The check detects missing core HTML/manifest/worker files, missing local icon references, and warns about external CDN and browser-only recording. It is not a substitute for testing a real device.

## Automated workflow proposal
Add a GitHub Actions workflow triggered by pushes and pull requests, checking out the repository and executing `python scripts/check_static.py`. Configure it to block merges only after its behavior is verified on the existing repository. Do not alter the live deployment until checks pass.

## Tests to add after source review
- JavaScript syntax and build validation
- manifest and offline shell resource validation
- accessibility and keyboard/TV-remote navigation
- screenshot comparisons at 320, 390, 768 and 1280 pixels
- playback and error recovery on authorized streams
- recording, persistence, playback and deletion
- source licensing, availability and API failures

## Notes
Direct API attempts to create the workflow were not completed in this session. Do not claim CI is active.
