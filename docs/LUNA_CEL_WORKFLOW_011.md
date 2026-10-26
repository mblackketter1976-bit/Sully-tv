# Authored-cel route — 2026-10-26

The owner explicitly authorizes traditional frame-by-frame animation, even if thousands of sketches are necessary, and building tools Sully can use to execute it. Quality and faithful performance determine the method; drawing count is not itself a quality claim. Keep the approved illustrated appearance, dialogue-led format and permanent-voice approval gate.

## Choice

Use mature free drawing applications where they already solve drawing, onion skinning and timing. Krita documents frame-by-frame raster animation and onion skinning; OpenToonz documents drawing levels and exposure sheets. Do not rebuild an entire drawing application to avoid using these existing capabilities.

- https://docs.krita.org/en/user_manual/animation.html
- https://docs.krita.org/en/reference_manual/dockers/onion_skin.html
- https://opentoonz.readthedocs.io/en/latest/drawing_animation_levels.html
- https://opentoonz.readthedocs.io/en/latest/working_in_xsheet.html

## New local building block

`studio/cel_animation.py` assembles authored transparent PNG cels using a JSON exposure sheet, streams frames to FFmpeg, optionally includes audio, renders numbered PNGs and creates previous/next difference proofs. It does not redraw Luna, generate in-between art, morph images or pretend that repeated output frames are distinct sketches. It loads source drawings lazily with a bounded 16-image cache so thousands of cels need not all occupy memory at once.

Each layer has explicit start/stop exposures (start inclusive, stop exclusive), cel identifiers and optional pixel positions. Holds on one, two or other numbers of frames are explicit. Transparent gaps on a layer are supported; overlapping exposures, unknown/missing drawings and out-of-range exposures are rejected. Reports separately count used source cels and output frames, and hash the source art. Multiple expression/body layers can share a background while important acting poses are redrawn.

The tests verify actual composited pixels and intentional holds, not artistic quality. No new finished Luna drawing sequence is claimed by creating this tool. The existing deformation examples remain useful tests but do not become hand-drawn animation by being exported as images.

## Next proof

Create a small set of consistent original Luna key drawings and speaking mouth/expression cels, review silhouettes and model consistency, then add only the in-betweens needed for a short dialogue/action scene. Check speech timing, meaningful holds, paw/prop contact and artwork stability against the uploaded movement reference. If the drawing quality or workflow fails, correct that short test before scaling to a long scene. Do not lock a candidate voice until the owner approves its sample.
