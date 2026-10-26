# Luna: corrected 2D target — 2026-10-26

## Governing owner correction

The owner clarified provenance: the artwork was created with this assistant; only the reference motion was Runway's. Do not describe the artwork as Runway-created. The local tests use our artwork and independently programmed motion, with no Runway service/API/credits or proprietary code dependency.

The owner explicitly rejected continuing the 3D shape/model appearance direction. Earlier approval was of movement, not the desired visual style. The project target is the detailed illustrated Luna and Old Sacramento artwork in the supplied Runway references. Preserve historical 3D files as experiments; do not resume model appearance work without a new explicit instruction.

References supplied and sampled directly:
- `1156.mp4`, Library `libfile_aa8a278a4cc88191983cff3536784ec9`: primary uncluttered visual/head-acting reference.
- `1135.mp4`, Library `libfile_2cfb8ce01f288191b059fa7b9dbf221c`: captioned story reference.
- `1149.mp4`, Library `libfile_53dba7a9080081918703261692543abe`: captioned story reference.

All are 15 seconds, 1280×720, 24 fps, with audio. Sampled frames were inspected; no audio transcription/voice matching has been performed. Preserve the Frenchie proportions, smushy face, blue eyes, detailed merle fur, bandana/satchel and warm illustrated Old Sacramento setting. Do not substitute a simplified 3D toy character.

## First new local 2D test

`studio/create_luna_2d_acting.py` extracts no source-video motion. Its input is one still from 1156 at 3.75 seconds. It renders 192 new frames (8 seconds, 24 fps) using bounded 2D head deformation and chest breathing, plus two blinks. A built-in image edit created a closed-eye key pose; only masked eyelid areas are composited, registered using 204 common feature inliers. The animation code, pose timing and head movement are new; it is not the original clip replayed or retimed.

Sampled original-art, closed-eye, tilt and return poses inspected. Frame checks report zero raw-pixel differences for pinned paws and outside the performance region. H.264 compression is lossy, so these measurements refer to pre-encoding frames. No paid Runway/API calls or new recurring service were used. Rendering uses local Python, OpenCV, NumPy and FFmpeg.

This is a limited acting/deformation test, not a full reusable rig, new walk, full head turn, dialogue, or a demonstrated episode-production workflow. Nearby detail inside the feathered head boundary can deform; review that before expanding motion. Source images are unchanged and included in a separate editable test package. The owner must judge appearance and motion before scaling.
