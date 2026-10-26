# Luna living-environment test 01

Eight-second environment-only motion proof: river ripples carry reflected lights, distant tree tips sway, and small flowering foliage moves independently. Luna, The Rook and the crate intentionally hold their staging pose. Quiet original synthesized air/water ambience, no dialogue. The approved permanent Luna voice is unchanged.

Independent extracted 2D render passes use a generated foliage clean plate, sky-decontaminated leaf colors and premultiplied alpha. A conservative foreground/contact mask restores source pixels at actor/paw/hand/crate contacts, rails and nearby fixed objects. This avoids dragging characters or rails with environmental motion.

The animation renderer preserves protected source pixels before video compression and has identical raw loop endpoints at t=0 and t=8. A two-second comparison confirms separate water/tree/flower regions change. Verified 192 frames at 24 fps, 1280x720, eight seconds and full A/V decode. Some extraction/clean-backing edges remain approximate; it is not a completed character animation or full physics/depth engine. Do not claim that all actor layers already exist: the current actor/crate/foreground group is a held illustration. scene-layer-plan.json records what must be separated for later performances and camera motion.

Files: source and clean backing images, tree/flower RGBA layers, water and foreground masks/layers, static backing, layer config, scene plan, ambience and verification. Reproduction code is in the Luna GitHub branch at studio/scenes/immersive_environment/build_environment.py. Requires Pillow, NumPy, OpenCV, SciPy, soundfile and FFmpeg; no video service or model download needed once these assets are present.
