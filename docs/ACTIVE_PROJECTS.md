# Active Blackketter Entertainment work — 2026-10-26

Both projects remain active. Preserve the charter, accepted movement files and working features.

## Sully TV
- Branch `sully-phase1-foundation-audit`; draft https://github.com/mblackketter1976-bit/Sully-tv/pull/1 .
- Licensed partial TVmaze schedules for three exactly mapped US networks, source/license credit, browser refresh/cache/failure preservation and current-data download remain implemented.
- Guide navigation now sits in normal page flow with 44px action targets. Duplicate room controls and overlapping floating navigation are hidden only while the guide is open.
- Verified 25 Python tests, JS normalization, isolated and full-HTML browser tests at 1280px/390px. Phone/desktop screenshots inspected. Functional run: https://github.com/mblackketter1976-bit/Sully-tv/actions/runs/40247545090 .
- Limits: partial episode coverage; no assertion listings match each stream; no real device/Safari/install test. The owner-approved navigation repair is live on main (13344a0). The sourced-guide build remains in development.
- Evidence: `docs/TV_GUIDE_PROVIDER_003.md`, `data/TV_GUIDE_LICENSE.md`.

## Luna
- Branch `luna-grounded-motion-benchmark`; draft https://github.com/mblackketter1976-bit/Sully-tv/pull/2 . Studio sources are on that branch.
- Actual uploaded V41 inspected in Blender 5.2.2 LTS. Historical V6 remains reference-only.
- Owner accepted `Luna_V41_Stop_Contact_Test.blend`, then `Luna_V41_Turn_Weight_Blink_Test.blend` (first WOW). Aesthetics explicitly deferred.
- New `Luna_Walk_Stop_Turn_Look.blend`: 18 seconds, approved walk/stop joined to approved turn/look/blink; both accepted sources unchanged. Reopened verification compares all 193 opening frames and ten turn poses; world vertex errors below 2.5e-7 scene units. Representative renders inspected.
- Deliverable: https://chatgpt.com/library?file_id=libfile_8292cdce421c8191bf92157f724cbab4&account_id=personal . Open and press Space. No scripts need running for playback.
- Evidence on Luna branch: `docs/LUNA_V41_AUDIT_002.md`, `docs/LUNA_V41_TURN_003.md`, `docs/LUNA_V41_SEQUENCE_004.md`. Rebuilders under `studio/`.
- Limits: movement prototype, existing art/proportions, mesh-pose approach, no calibrated physical mass model or Windows playback benchmark. Do not ask again for the already supplied V41 or treat movement approval as final appearance approval.

## Current handoff — 2026-10-26
- Accepted live navigation: one bottom bar for Back, Home, Categories, Search and Top, responsive quick controls/search, restored app icons. Main navigation CI and Pages deployment passed; public HTTP verified.
- Guide development now incorporates that exact accepted navigation, removes duplicate guide controls and makes dock Search focus the station field. Python, guide browser and four-width navigation tests passed in run 40249222384. Real provider fetch returned 52 current/future episode entries across three reviewed networks; coverage remains partial. No guide release was made.
- Luna appearance is now requested. First native 3D visual proposal: rest-coordinate silver merle, retained blue eyes, sculpted bat ears, warm studio. All 432 frames preserve evaluated paw vertices and root matrices exactly (zero difference from accepted sequence). Representative poses inspected; six-second rendered turn excerpt and full 18-second Blender scene are being prepared for owner appearance review. Preserve earlier motion files and do not assume final likeness approval. See docs/LUNA_VISUAL_005.md on the Luna branch.
