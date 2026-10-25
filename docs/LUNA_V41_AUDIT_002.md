# V41 project inspection and stop-contact test — 2026-10-25

## Input and preservation
User supplied `Luna_3D_Studio_V41.blend` after being asked for the current editable project. Earlier V6 material remains historical reference only and was not run or changed.

Original input SHA256: `e6680e9c517af50315372c555bef563c83029acbe2a9589402d7f450ec10ed04`. The original uploaded bytes were verified unchanged after testing. The project binary and derived test copy are kept with the user's files, not committed to this public code repository.

Used official Blender 5.2.2 LTS, downloaded from Blender's release directory and verified against the official SHA256 manifest. Auto-execution was disabled. Earlier tests using Blender 4.0.2 do not establish compatibility with this 5.2 file; this inspection and correction were actually executed on 5.2.2.

## Direct observations
- Original timeline: frames 1–32400 at 24 fps (22m30s).
- Objects: 534 meshes, 102 cameras, 40 lights, 26 empties, 13 font objects, 4 curves; zero armatures.
- Luna hierarchy: 56 objects. Four continuous leg surfaces use 1359/1360/1359/1359 shape keys, including Basis. No bone skeleton or vertex-group rig was present on those surfaces.
- Existing scene rendered successfully. Its current visual state is a blocking prototype, not the approved poster-quality character.

## Important correction to the working assumption
Do not discard the existing walk merely because it lacks bones. Actual world-coordinate samples show flat-sole walking intervals with effectively fixed paw positions. The opening walk already contains a useful contact solution.

At the final stop, frames 121–133 ease the paws approximately 0.14 scene units toward neutral while keeping their soles low. That visibly slides the feet on the ground. A broad low-height window alone is not a definitive stance detector; tighter windows separated successful walking contacts from the stopping defect.

## Scoped fix and execution evidence
`studio/fix_v41_stop.py` only accepts the reviewed input hash and Blender 5.2. It creates a separate full-copy scene, independently copies edited animation/shape data, holds the existing paw world positions from frame 121 through 193, and adjusts each reviewed continuous leg surface from fixed shoulder to moved ankle. It does not replace the character artwork or redesign the story.

New file: `Luna_V41_Stop_Contact_Test.blend` (28,065,802 bytes). It contains `V41_Original_Story`, `V41_Stop_Contact_Test`, an embedded readme/verification report and the rebuild script. Trial render output points to a separate relative folder. The original 22m30s story remains available; the selected test scene covers the opening 193 frames.

Verified by execution and a second rebuild:
- Paw world-position drift over 145 integer/half-frame stop samples: 1.49e-8 scene units.
- Terminal limb-ring offset relative to its paw: maximum change 5.96e-8 scene units before subdivision.
- Original-story paw actions preserved at inspected frames; opening foot poses before the stop preserved.
- Original input SHA256 unchanged.
- Reloaded test copy and rendered original/corrected frame 133 with identical diagnostic camera/settings. Both renders inspected visually; the contact correction retains overlapping ankle/paw surfaces without an obvious new gap in that view.

These measurements concern scene coordinates; physical metre scale has not been independently calibrated. The ring test is before subdivision and is not a claim of full-character deformation quality. Body weight transfer, final likeness, natural gait, all later story scenes, voice, and Windows workstation playback remain unverified or unfinished. No finished pilot/movie is claimed.

## Next action
User can open the separate test file in Blender and play the selected opening test scene. Preserve original source and review this small motion change before expanding. Continue the visual likeness gate against the approved character references. The existing mesh-pose workflow should be compared with an armature approach before committing to a wholesale rig replacement.
