# Luna on the Streets — The Secret Under Old Sac

Three-minute opening experiment, made under the owner's milestone-ownership instruction. The owner approved the earlier 2D movement/blink and authorized an independent attempt at the first three minutes. This is a review prototype, not a claim of production-ready or Runway-equivalent capability.

## Result and scope

The cut tells one continuous opening through 17 timed shots: Old Sacramento, Luna and the fry, three taps, a paw-marked key, and a glowing brass box under the boardwalk. New narrator speech, procedural celesta/plucked score, wood/metal effects, captions and a title are assembled locally. Luna's established character voice is not replaced; this opening uses a separate narrator and no spoken character dialogue.

The picture uses illustrated 2D assets and locally programmed motion: head/eye/ear acting, breathing, a limited paw-placement approach, camera compositions, dust and light effects. The generated listening pose is separately illustrated, not a continuous animated transition. It remains limited animation with substantial held illustrations and camera moves; walking, full-body continuity and broad expression/scene interaction are not solved at production quality. The opening is an experiment to judge, not a padded replay of an eight-second test or the source Runway video.

## Inputs and provenance

The approved artwork was created with the assistant; only the earlier reference clip's motion was Runway's. The approved input still and accepted blink key remain preserved. Background plate, transparent character layer, listening pose and clue/box inserts were created with the built-in image tool for this experiment. No Runway service, API, credits, source-video motion or source-video audio is used.

The actor cutout is registered to the approved still with feature matching. Layered 2D deformation permits head and paw motion without bending the background. Its paw placement is a prototype skin deformation, not an anatomically validated reusable rig. Source images, timing, scripts and generated audio are included for review and rebuild.

## Rebuild

Requires Python 3, NumPy, OpenCV (`opencv-python-headless`), Pillow, soundfile, kokoro-onnx, ONNX Runtime and FFmpeg with libx264/libass. Install dependencies in your own environment. This package does not contain installed tools or model weights.

1. Use existing `audio/narration_*.wav` to rebuild the existing result without speech inference. For new text, download the Kokoro model/voice files from the official release links below and run `make_narration.py --model-dir MODEL_DIRECTORY`.
2. Run `make_sound.py`; it writes the original soundtrack/mix and SRT captions.
3. Run `render_picture.py --output picture.mp4`.
4. Normalize the mix and mux it with picture and optional ASS captions using the FFmpeg commands in `BUILD_NOTES.txt`.

Set `ORT_DISABLE_TELEMETRY=1` before importing ONNX Runtime. `make_narration.py` does so in its first import block and also calls the supported telemetry-disable API. An initial unconfigured inference attempt was blocked by automatic approval review for unexpected telemetry. The final narration completed using the documented startup opt-out. Do not remove that opt-out or claim network traffic was independently audited; no packet-capture audit was performed.

## Tool sources and licenses

- Kokoro wrapper: https://github.com/thewh1teagle/kokoro-onnx — MIT.
- Kokoro model/voices: https://huggingface.co/hexgrad/Kokoro-82M — Apache 2.0. Narrator: `af_heart`.
- Model: https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
- Voices: https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
- Runtime privacy control: https://github.com/microsoft/onnxruntime/blob/main/docs/Privacy.md
- OpenCV: https://opencv.org/license/ ; NumPy: https://numpy.org/doc/stable/license.html ; FFmpeg: https://ffmpeg.org/legal.html . Dependencies and model binaries are not redistributed here.

All score/foley in this package is composed procedurally for this cut. No existing soundtrack was sampled. No new paid account or recurring service was used. The built-in image tool remains the asset-generation tool used in this session; this is not an independent generative-image/video model.

## Verification and honest limits

See `final-verification.json`, `asset-manifest.json`, `audio/narration-timing.json` and `audio/sound-verification.json`. Shot proofs and selected decoded final frames were inspected; footage duration/frame count, stream metadata, audio peak/length and shot continuity are checked. No complete human-style playback review or actual Windows performance benchmark is claimed. Caption timing follows segment durations and approximate phrase timing, not forced word alignment. The next gate is the owner's review of whether the result merits continuing or should be narrowed and rebuilt more slowly.
