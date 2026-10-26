# Luna Animation Studio — Production Architecture and Quality Gates

Status: architecture investigation; no tool selected or pilot produced.
Goal: professional, consistent 2D animated episodes, read-alouds, and eventually a film. No recurring paid credits or subscriptions.

## Known workstation
- Windows 11 Home, Intel Core 7 150U (10 cores, 12 threads), 32 GB RAM.
- NVIDIA GeForce MX570 A, approximately 2 GB dedicated video memory reported; Intel integrated graphics.
- Storage free space and existing animation asset inventory not yet measured.

## Non-negotiable quality gates
1. **Model sheet:** Luna retains approved proportions, merle pattern, blue eyes, and consistent face in front/side/three-quarter views.
2. **Motion:** believable walk cycle, turns, body weight, blinks, expressions; no visible jitter or unnatural looping.
3. **Dialogue:** intelligible voice, consistent tone, synchronized mouth shapes, no echo or clipping.
4. **Composition:** coherent backgrounds, camera motion, lighting, no mismatched perspectives.
5. **Technical:** full HD target, stable frame timing, synchronized sound, clean export.
6. **Reusability:** reusable rigs, scenes, motion library, reproducible export, versioned source assets.
7. **Economics:** legally usable, zero recurring cost; benchmark performance on actual workstation.

## Selection method
Compare cutout rigs, frame-by-frame 2D, hybrid 2D/3D, and procedural animation. Test with the SAME 15-second benchmark covering a walk, turn, expression and dialogue. Evaluate visual quality first, then reproducibility, workstation performance and labor. Do not assume that an automatic lip-sync feature alone solves full character animation.

## Pilot acceptance
A completed 45–60 second scene can be commissioned only after the short benchmark passes. User approves the final look. Record actual render times, memory use, manual correction effort and defects. Do not scale to episodes before pilot approval.

## Immediate investigation
1. Check disk space and local installed applications/versions.
2. Inventory prior Blender, Cartoon Animator, images, audio, and project files.
3. Confirm asset licenses and rights.
4. Compare candidate pipelines and build a proof-of-concept plan.
5. Establish a safe local script runner only after explicit review of its permissions.

## Status honesty
Hardware: identified from screenshots. Pipeline: NOT selected. Lip-sync: NOT tested. Pilot: NOT produced. Desktop application control: NOT connected.
