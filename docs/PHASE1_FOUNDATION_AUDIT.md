# Sully TV — Phase 1 Foundation Audit

Status: IN PROGRESS (documentation only; no application code modified)
Branch: `sully-phase1-foundation-audit`
Production branch: `main` (unchanged by this audit)

## Confirmed from repository
- `index.html` is the primary app entry point and includes inline styling.
- `sw.js` implements a network-first cache fallback for a fixed app shell.
- `index.html` loads HLS.js from a CDN.
- `package.json` is absent at the repository root (at time of audit).

## Guardrails
1. Preserve existing production behavior and all channels.
2. Do not refactor the single-file app before a complete feature inventory and baseline tests.
3. Keep DVR promises aligned with static-hosting limits: a browser cannot guarantee recording after closure.
4. Treat catalog links, successful playback, and distribution rights as three different checks.
5. Use free services and tools; do not add recurring expenses.
6. Stage changes on a branch and validate before merging.

## Required next checks
- Inventory routes, rooms, themes, navigation, player controls, DVR, profiles, Kids TV, Luna channel, and Michele's Murder Mystery Channel.
- Record reproducible desktop and mobile smoke-test procedures.
- Validate service worker cache upgrades and rollback behavior.
- Add syntax and non-destructive smoke tests before modularization.
- Verify stream playback and rights separately; do not infer availability from directory listings.

## Release gate
No production deployment until feature inventory is complete, tests pass, and manual checks cover representative phone and desktop workflows.

## Luna Animation Studio (separate project)
- Audit existing assets and local hardware first.
- Compare free animation pipelines against a single pilot-scene test.
- Do not assume access to desktop apps through GitHub alone.
- Keep animation code and assets separate from Sully TV.
