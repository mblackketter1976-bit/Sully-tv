# Movement-only turn, weight-shift and blink study — 2026-10-25

## Accepted baseline and scope
The owner approved movement in `Luna_V41_Stop_Contact_Test.blend` and explicitly deferred aesthetics. Preserve that file and approval scope. This study is a separate artifact, not an appearance-approved character, production pilot or replacement movie timeline.

Source SHA256: `e0101fcdeda9c58533b60acbf21afc720bca14271ab7cf26bee3391d8a6f9d5b`.

## Built
`studio/build_v41_turn_study.py` snapshots the evaluated visible V41 character geometry into a standalone study, retaining its materials and blue eyes. It removes historical action/shape stacks from the snapshot rather than making the owner load the full movie scene for a ten-second test. It retains the existing continuous-mesh leg approach; no final rig architecture was selected.

- 240 frames at 24 fps (10 seconds).
- Twelve individually lifted paw placements produce a controlled 45-degree turn.
- Body translation biases gently toward the supporting-paw centroid, capped at 0.035 scene units; this is procedural weight-shift motion, not a calibrated mass/physics simulation.
- Head lift/look and a blink. Upper/lower eyelid cap surfaces occlude each eye; eye geometry is not shrunk for the new blink.
- Frame markers, selected camera view and material-colored solid viewport for simple playback.
- Relative render-output folder, embedded readme and rebuild script.

## Test/fix evidence
The first 90-degree turn kept paw contacts numerically but showed excessive sideways leg bending in rendered pose 120. That version was not delivered. Revised to 45 degrees with anticipatory touchdown headings; reran the build, contact checks and representative renders. The revised pose visibly reduces the bend. This is not an anatomical validation or a claim that every joint is final.

Executed twice on official, checksum-verified Blender 5.2.2 LTS. Final measurements:
- Maximum sampled paw-centre target error: 1.33e-7 scene units over all 240 frames.
- Maximum baked half-frame drift in qualifying constant-stance intervals: 3.77e-5 scene units, below a declared 0.001-unit diagnostic tolerance.
- Minimum evaluated paw-sole height: 0.0090000257; diagnostic floor placed at that same height. No sampled paw penetrates this flat floor.
- At frame 200, four gaze-axis ray checks first hit pupils; at closed frame 217 the same checks first hit upper/lower eyelids. Eight expected results confirmed.
- Inspected representative rendered poses for start, mid-turn, finish and closed blink. Final revised renders checked at 120/200/217. No complete rendered video or actual Windows playback benchmark is claimed.
- Approved source file bytes verified unchanged.

Saved `Luna_V41_Turn_Weight_Blink_Test.blend` (1,183,642 bytes) as a separate user-facing file. The earlier accepted file and original V41 remain intact. Project binaries are not committed to this public repository.

## Limits and next gate
Appearance is still the V41 prototype; lid shape/material and anatomy are not final. No calibrated physical units, validated centre of mass, muscle/joint limits, full-body collision system, dialogue, soundtrack or finished pilot. Limb topology and procedural texture stability need further review. User should assess the movement before expansion; do not treat movement approval as approval of final aesthetics.
