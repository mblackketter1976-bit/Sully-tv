# Fresh 24-cel test 07

The owner requested willingness to restart rather than over-patch, and snow-white fur instead of orange. They liked the corrected model and fresh 24-cel sheet. This is the assembled review test of that new direction, not an approved final animation.

`studio/build_luna_fresh_24.py` extracts a new 6x4 sheet, places the drawings using two planted-paw template anchors, and assembles explicit exposures. Global translation, uniform scale 0.9504–1.0065 and rotation -1.3203 to +1.3397 degrees correct source-sheet placement without optical-flow interpolation or anatomy morphing. No previous cels are reused.

24 drawings, 96 output frames, 24 fps, 4 seconds. Holds: first 12 frames; 2–20 three frames each; 21–23 two each; final 21. A frame rate is not a count of distinct drawings per second. Verified all 96 encoded timestamps against n/24 and full FFmpeg decode. All 24 registered poses and selected transition details inspected. White foreleg samples have neutral red/blue balance. No realtime visual playback claimed.

An independent second template search measures local residual within 2 px. Six front-paw texture correlations fall below the exploratory .90 threshold; minimum .8828. This is acknowledged model/detail variability and must not be described as every anchor passing .90. Two-anchor fitted residual zero is a construction property, not independent proof. Remaining detail/pose variations require owner review.

Saved video, new drawings, source model/sheet, exposure timings and audits: https://chatgpt.com/library?file_id=libfile_ca898b9d9710819193dffcde5bec022d&account_id=personal
