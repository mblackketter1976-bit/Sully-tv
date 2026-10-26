# Accepted movement sequence — 2026-10-26

The owner accepted the stop correction and called the turn study the first WOW. Appearance remains deferred. `Luna_Walk_Stop_Turn_Look.blend` combines those accepted clips into one 432-frame, 24 fps (18-second) standalone scene. The approved sources remain byte-for-byte unchanged.

The opening 193 frames reproduce the evaluated accepted walk/stop surfaces. The accepted 240-frame turn/look/blink begins at shared frame 193. No new gait, anatomy, physical model or appearance approval is implied. A tracking camera and stationary world-space floor grid make translation visible. The file opens at frame 1 for Space-bar playback.

## Verification

Blender 5.2.2 LTS reopened the saved output. Compared every vertex of 34 character meshes for all 193 opening frames against a separately captured accepted-source cache: maximum world-space error 1.3328004e-7 scene units. Compared ten turn poses against the unchanged accepted turn source: maximum error 2.4027401e-7 scene units. Both are below the declared 1e-5 scene-unit tolerance. Prior turn contact verification remains documented in `LUNA_V41_TURN_003.md`; this comparison verifies the join preserved that motion, rather than introducing a new physical balance claim.

Rendered and visually inspected opening frame 48, join frame 193, turn frame 312 and closed blink frame 409; also rendered stop frame 121. No full rendered video or Windows performance benchmark was performed. Existing prototype materials and proportions remain.

## Rebuild

Use `studio/build_v41_sequence.py` twice with the verified Blender 5.2 runtime. First open the approved stop file and pass `--capture PRIVATE_CACHE --turn APPROVED_TURN --output NEW_BLEND`. Then open the approved turn file and pass `--opening PRIVATE_CACHE --turn APPROVED_TURN --output NEW_BLEND`. Both source SHA256 values are guarded. The cache is a trusted local intermediate, not a user-facing artifact. The two-pass process avoids keeping both historical scenes and the geometry bake active in one dependency graph.

Use `studio/verify_v41_sequence.py` first with the approved turn file and `--capture-turn`, then with the saved combined file, using the same `--opening`, `--turn-cache` and `--report` paths. Optional `--render-dir` renders the five review poses. Project binaries and caches are not committed to the public source repository.
