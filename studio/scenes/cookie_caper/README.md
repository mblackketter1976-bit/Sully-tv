# Luna and The Rook — Cookie Caper

A complete ten-second family-friendly scene with picture, character dialogue, original music and foley. This is Sully's current finished-scene proposal for owner review, not a claim of broadcast-ready perfection or an official G classification.

The Rook: “A little misdirection.”
Luna: “Nice trick. Now give back my cookie.”
The Rook: “Worth a try.”

No narrator. Snow-white Luna with blue eyes. Rook is charming and mischievous. The cookie is revealed in his palm, tossed back, and lands on the crate. Shot cuts at the first frames after 2.4, 5.8 and 8.5 seconds.

Candidate voices: Luna af_bella at speed 0.95 en-us; Rook bm_george at speed 1.03 en-gb, Kokoro v1.0 ONNX. No pitch shift or added voice reverb. Exact model/voice hashes, WAV hashes, sample rates, line timings and mix gains are in audio/voice-candidates.json and audio/mix-verification.json. They are NOT permanent approved voices. Preserve these records and approved reference WAV if the owner chooses a voice.

Animation: 24 fresh Luna drawings plus locally calculated RIFE intermediates; six localized speech-mouth drawings driven by Rhubarb and audio energy; twelve new registered Rook poses with RIFE interpolation; small head inclination; cookie trajectory; cutout matting. Rook beak movement follows body pose acting and is less precise than Luna's mouth timing. Remaining fine model/detail changes and small matte/edge imperfections may be visible.

Fixes during this attempt: incorrect Rook grid slices clipped three heads; recut on actual row boundaries and aligned feet. Replaced silhouette-hole filling that wrongly retained white air spaces with local model matting. Restricted Luna's mouth patch after it copied part of the scarf. Corrected close-up framing so the cookie would not float disconnected at the edge. Replaced flat placeholder cookie with illustrated prop.

Verified: ten-second container, 240 decoded video frames at 24 fps, 1280x720 H.264 yuv420p, AAC stereo 48kHz, all video timestamps, full A/V decode, finite audio with decoded peak 0.6324 (no clipping). Audio metadata is 10s; AAC decoding has 5.33ms padding. Master measured -15.67 LUFS / -3.98 dBTP before AAC. Inspected 21 composed proofs and six decoded final frames. No claim of full realtime viewing or listening.

Code is stored in the Luna GitHub branch under studio/scenes/cookie_caper/ (not duplicated in this assets package). Extract assets alongside that code. Python requires Pillow, NumPy, OpenCV, scipy, soundfile and onnxruntime, plus FFmpeg. The included models allow picture rendering without redownloading weights. Voice WAVs and mixed audio are preserved; regenerating speech requires the separately distributed Kokoro weights. ORT_DISABLE_TELEMETRY=1 is set before runtime import and runtime opt-out is applied.

Final video is Luna_and_The_Rook_Cookie_Caper_10s.mp4. Captions are provided separately, not burned into the cartoon.
