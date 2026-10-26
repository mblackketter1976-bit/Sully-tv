# 2D expression test 02 — 2026-10-26

The owner approved test 01's movement and blink, then authorized eye direction and a small ear reaction. Preserve test 01 as the accepted 2D baseline. The artwork is ours; the earlier reference video's motion was Runway's.

`studio/create_luna_2d_expression.py` is a separate builder. It retains the accepted eight-second head-tilt, breathing and two-blink timing. Added a short glance toward the fry (up to 2.6 pixels left/3.2 down), then a return; a small asymmetric ear perk follows during the head reaction. Compact interior-eye deformation weights preserve surrounding fur/lids. Ear deformation follows the existing head map, keeping the ear attached. No new generative-image call, source-video motion, paid service or 3D model is used.

The actual rendered output is 1280×720 H.264, 192 frames, 24 fps, eight seconds. Raw pinned-paw and outer-background differences remain zero. Compared seven neutral/blink/return frames with the accepted output: all pixels match exactly. An initial one-level pixel difference from a zero-angle remap was removed by skipping inactive ear/gaze transforms. Representative glance, ear-reaction, blink and resting poses were inspected. Measurements refer to pre-encoding images; video compression is lossy.

Source artwork and accepted blink assets are SHA256-guarded. The builder and source package reproduce the test using local Python/OpenCV/NumPy/FFmpeg. Appearance/motion additions await owner review. This remains a small 2D acting/deformation study; it does not establish new walking, full head turns, dialogue or a complete production rig.
