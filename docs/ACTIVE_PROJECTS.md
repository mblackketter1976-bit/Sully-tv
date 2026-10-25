# Active Blackketter Entertainment work — 2026-10-25

Both projects remain active. Keep separate review/release decisions; preserve the charter and working features.

## Sully TV
- Branch: `sully-phase1-foundation-audit`; draft https://github.com/mblackketter1976-bit/Sully-tv/pull/1 .
- Built: licensed partial TVmaze schedule adapter, first real snapshot (40 entries/3 exactly mapped US networks), explicit attribution/CC BY-SA data license, browser refresh with cache/failure preservation, start/end labels, same-cell short-show display, restored app PNG icons.
- Verified: 25 Python tests; JS source tests; isolated and full-HTML browser tests at desktop/phone widths including refresh/cache/failure/current-data download; static integrity zero errors. Latest functional run: https://github.com/mblackketter1976-bit/Sully-tv/actions/runs/40243454864 .
- Limits: incomplete episode coverage, no confirmed correspondence to what each stream is playing, no actual device/Safari/install test. Live branch has not been changed. Owner approval is required before live deployment.
- Current evidence and licensing: `TV_GUIDE_PROVIDER_003.md`, `data/TV_GUIDE_LICENSE.md`.

## Luna studio
- Branch: `luna-grounded-motion-benchmark`; draft https://github.com/mblackketter1976-bit/Sully-tv/pull/2 . Read studio files using that branch, not the Sully branch.
- Built: original contact core, explicit Blender adapter, evaluated skinned-mesh diagnostic with baked 15-second action. Prior source/artwork preserved.
- Verified: six motion tests; Blender 4.0.2 run https://github.com/mblackketter1976-bit/Sully-tv/actions/runs/40242575280 passed at 361 frame samples and 360 half-frame samples. The diagnostic render was inspected. Sampled sole error below 1e-6 m; baked half-frame stance error 0.000733 m, within a declared 1 mm fixture tolerance. Combined local suite after branch synchronization passed 31 tests.
- Limits: diagnostic geometry only. No approved rigged Luna file is confirmed accessible; no final likeness, natural gait, full character render, dialogue or pilot. Actual Windows workstation/runtime compatibility remains untested.
- Required next input: inspect the current editable character project (`.blend` or Cartoon Animator `.ctProject`). Windows project folders are not directly accessible from this session. Do not rebuild approved art or repeat rejected primitive/cartoon-filter attempts as if they were production progress.
- Detailed evidence: `docs/LUNA_MOTION_VERIFICATION_001.md` on the Luna branch.
