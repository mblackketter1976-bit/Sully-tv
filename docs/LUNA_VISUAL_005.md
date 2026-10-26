# Luna appearance and accepted motion — 2026-10-26

The owner requested an aesthetically pleasing Luna with smooth movement today. This is a separate first appearance proposal over the accepted 18-second walk/stop/turn/look sequence, preserving earlier movement files.

## Visual changes

- Silver/charcoal merle on warm ivory, using a stored per-vertex rest-coordinate attribute instead of world-space coordinates, so markings travel with the character.
- Retained blue irises; glossy eye/nose materials, warm muzzle/chest, muted pink ear interiors and teal collar.
- Rebuilt four outer/inner ear meshes into tapered bat-ear silhouettes. Each cached opening pose transfers its original affine motion onto the new rest shape; turn/head transforms remain unchanged.
- Smooth shading, selective surface subdivision, warm studio floor and three soft lights. Paws deliberately retain their original evaluated surfaces to preserve contact.
- Material-preview viewport, embedded readme/rebuilder and relative output path. No runtime scripts required for playback.

The first ear stretching approach looked too long. A second reconstruction exposed the outer ear through the inner patch; a constant offset then made that patch appear detached in three-quarter view. The final patch follows the convex front of the outer ear with a small surface offset. Representative three-quarter/front/blink poses were re-rendered and inspected. Appearance is proposed for owner review, not claimed as a final approved likeness. No approved poster/photo reference was retrieved in the current Library search, so prior prototype geometry and the established blue-eye/Frenchie/merle constraints grounded this pass.

## Actual saved-file checks

Blender 5.2.2 LTS evaluated all 432 frames and compared 1,054,080 paw vertices with the accepted sequence: maximum world-space difference zero. Root matrices also match exactly. New materials and ear topology intentionally differ. This is a preservation check, not a new calibrated mass or anatomy validation. The saved file was opened for final render and verification.

Representative rendered three-quarter, front-turn and closed-blink poses were inspected. Deliver a still and a six-second 24 fps rendered turn excerpt alongside the full 18-second editable Blender scene. The short video uses every source frame 217–360 without interpolation; it is not the complete sequence or a Windows playback benchmark. Render settings are in `studio/render_visual_preview.py`; full-resolution still settings are in `studio/render_visual_poster.py`.

Rebuilder: `studio/style_v41_luna.py`, opened with the accepted `Luna_Walk_Stop_Turn_Look.blend` and `--output NEW_BLEND --render-dir REVIEW_DIR`. `studio/check_visual_motion.py` captures accepted paw reference data, finalizes the separate output and compares all frames. Earlier files are never overwritten. All source and render tooling is local/free; no paid AI generation or recurring service was used.
