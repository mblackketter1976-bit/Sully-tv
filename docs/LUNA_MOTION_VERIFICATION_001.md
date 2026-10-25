# Luna recovery and grounded-walk benchmark — 2026-10-25

## Evidence inspected
- Repository studio handoff and engineering charter.
- Saved `Luna_V42_Articulated_Rig_Proof.html`: simple vector mechanical illustration explicitly marked non-final. Its own notes say grounded contacts remain outstanding; paw positions are sine-driven.
- Recovered prior Blender source builds V45–V54. Inspected V53 walking code and V54's complete character-study source and visual-target note. Version numbers alone do not identify an approved/current pipeline.
- Viewed `Luna_Movie_Poster_Blue_Eyes.png`: cinematic likeness/finish reference. It is not evidence that a matching articulated asset exists.

## Findings
- V53 changes leg rotations and paw translations independently with sine functions while the root travels. No world-space stance constraint is present in that walk section; this is a source-level explanation for sliding/disconnected motion, not a fresh render result.
- V54 is a separate static study: procedural merged forms, camera renders, no deforming armature or gait. Do not market it as a tested rig or final art.
- The repository handoff understated the existence of prior attempts. Preserve all of them and inventory approval/execution state separately from version labels.

## Implemented and tested
`studio/locomotion.py` is an original, renderer-independent two-link contact prototype. It keeps each planted paw at one world point and solves connected hip–knee–foot positions with constant segment lengths. Invalid targets fail explicitly.

Six motion tests passed locally: all paws lift/plant; stance drift; segment lengths; liftoff/touchdown continuity; repeatability; invalid/unreachable input handling. Full suite: 25 tests passed locally including the 19 Sully guide tests.

Default 15-second straight-walk benchmark at 24 fps:
- 361 sampled poses including both endpoints
- maximum measured stance drift: 0 metres
- maximum segment-length error: 3.89e-16 metres (floating-point precision)
- minimum foot height: 0 metres
- root translation: 3.75 metres

These measurements describe computed joint targets only. They do not verify a skinned mesh, render, real biomechanics, visual quality, software performance on the Windows workstation, or production readiness. No character art was regenerated or altered. No pilot/movie produced.

## Build/adopt assessment
Observed Blender IK documentation: https://docs.blender.org/manual/en/5.0/animation/constraints/tracking/ik_solver.html . It describes chain target following, pole targets, chain length and optional stretching. Actual Blender runtime behavior has not been tested in this environment.

Working decision: HYBRID / provisional. Keep established renderer/rig tools replaceable and use a small independently testable contact contract. This does not justify replacing Blender's general IK solver or selecting the final 2D/3D production pipeline. No third-party code copied into this prototype.

Next: inventory approved layered art and actual rig files, adapt verified contact targets to the selected rig, then inspect a short rendered walk. Full 15-second benchmark must eventually include turn, expression and dialogue. The 45–60-second pilot remains gated on visual approval.
