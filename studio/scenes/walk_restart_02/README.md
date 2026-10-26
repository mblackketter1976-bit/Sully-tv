# Luna walk restart 02 — short mechanics proof

The first walk was rejected by the owner as unnatural and clumsy. The full WORKING_PRINCIPLES.md was reread. That six-second image-morphed cycle is preserved as rejected, not an approved movement baseline. This restart does not reuse its generated poses or RIFE gait.

Four-second 1280×720/24fps study. One consistent Luna head/torso drawing is combined with independently articulated raster legs. Source leg pieces rotate rigidly about joints; two-link inverse kinematics preserves bone lengths. Each paw moves through a support phase fixed to the world, followed by a low arcing swing with continuous velocity. Near/far legs alternate, the body rocks rigidly by 0.65 degrees, and soft taps follow touchdown times. No face/head mesh deformation or picture interpolation. The floor/near post overlap stays fixed. The boardwalk is reused from the earlier scene; this test focuses on movement, not additional environmental animation. No voice changes or dialogue. The Rook remains female.

## Reference and attribution

Catavitello G, Ivanenko YP, Lacquaniti F (2015), Planar Covariation of Hindlimb and Forelimb Elevation Angles during Terrestrial and Aquatic Locomotion of Dogs. PLOS ONE 10(7): e0133936. https://doi.org/10.1371/journal.pone.0133936 . Open-access CC BY; https://creativecommons.org/licenses/by/4.0/ . Original supporting dataset retained unmodified in canine-reference-data.zip. Attribution applies to the reference data, not ownership of Luna's original character art.

Used DogS walking second-stride contact events: hind [39,65,81], fore [45,67,84], recorded at 60fps. Fore touchdown lag is 6/42 of the reference hind stride. Fore and hind support fractions are 22/39 and 26/42. Those timing ratios guide this animation, retimed to 0.9-second strides; actual joint trajectories and dog likeness were not copied. Contralateral timing is modeled half a cycle later. Synthetic swing paths, stride length, body motion, joint placement and illustration retargeting are our approximations, not measured French bulldog motion.

## Actual checks and limits

All 96 frames exported and fully decoded. Rig support positions stay fixed to the world and limbs retain lengths to floating-point tolerance. Two or more feet support the rig throughout. 108 encoded near-paw patch comparisons report at most one pixel shift; these comparisons measure local paw images, not the entire gait's naturalness. Audio decodes without clipping. Consecutive-cycle and 14 decoded export samples inspected; no realtime visual playback/listening claim.

This is a mechanics proof and partial progress, not a finished natural cartoon walk. Rigid torso/satchel performance and visible joint transitions still need artistic refinement. Correct foot locks and export checks alone do not establish appealing acting. Do not expand this into an episode or mark the walk approved without meeting the visible movement standard.

## Source and reproduction

Source build_walk.py and verify_output.py are maintained in GitHub, studio/scenes/walk_restart_02. Runtime: NumPy, OpenCV, SciPy, Pillow, soundfile, ONNX Runtime, FFmpeg. Existing U2netp model is in the earlier Cookie Caper asset package; its SHA is checked, and telemetry is disabled before runtime import and through the runtime opt-out. No Runway, paid API, or new model is needed. Place this directory beside luna-finished-scene-10s-v01/models, luna-walk-v01/assets/boardwalk.png and luna-environment-motion-v01/environment-ambience.wav, or recreate those dependency folders from their existing packages. Original and legless-body image-tool outputs, extracted parts, reference dataset, audio, motion traces and verification are in this package. Standing-source prompt requested the same white/merle blue-eyed Luna in a neutral side view; body-source edit removed the limbs to expose the belly/chest. Original upper/head pixels were restored before layer extraction.
