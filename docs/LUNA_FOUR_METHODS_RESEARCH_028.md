# Four researched routes for Luna movement — October 25, 2026 (Pacific)

## Scope and status
Owner requested research into four best-bet methods, including an original custom method, before further animation. This is research and engineering judgment, not a claim that any new route has been implemented or proven with Luna. No new animation test should be sent merely because it exports correctly.

Standing owner gates: polished movement before the next phase; preserve compact French bulldog proportions and accepted original 2D artwork; keep snow-white merle coat and blue eyes; avoid sending intermediate tests the owner must diagnose. Make only a few focused attempts on one hypothesis, then research/change angle if progress stalls. No recurring service costs, no Runway dependency. Do not revive rejected 3D appearance work.

## Diagnosis from our own attempts
The generated-pose cycle lacked consistent anatomy and purposeful pose progression. RIFE increased temporal sampling without repairing those decisions. The articulated cutout restart fixed much of the support sliding, but left a rigid torso/head assembly and an overly long/full source silhouette. A soft deformer cannot repair a wrong rest drawing by itself. Proportions must be grounded in the accepted original reference before rigging. Numerical support/length checks are necessary but insufficient; whole-character movement must meet the artistic target.

## 1. Authored 2D key poses, breakdowns and in-betweens
Use Krita or OpenToonz for deliberately constructed sequential drawings. Establish contact, settling, passing and lift/reach poses, then draw the intermediate changes. Use common construction guides for head, ribcage, pelvis, shoulder height and body length. Preserve markings/costume through controlled drawing rather than independent generation requests. Plan exposure timing with the poses.

Best use: strongest direct control over silhouette, weight, acting and joint shape; fallback when deformation is visually inadequate. Risk: maintaining detailed merle artwork and clean registration takes significant drawing/cleanup work. A tool does not supply the animator's decisions. Our ability to author coherent drawings must be demonstrated rather than assumed. Twelve drawings exposed twice in a 24fps timeline is a candidate, not a universal smoothness guarantee; add drawings where the motion demands them.

Sources:
- https://docs.krita.org/en/user_manual/animation.html
- https://krita.org/en/about/license/
- https://opentoonz.readthedocs.io/en/latest/drawing_animation_levels.html

Krita supports raster frame-by-frame animation and neighboring-frame onion skins. Its official licensing permits commercial artwork. OpenToonz supports the traditional drawing workflow.

## 2. Flexible 2D mesh rig plus replacement/corrective drawings
Use OpenToonz Plastic as the clearest existing-tool candidate. Separate skull, jaw/eyes, torso, pelvis, limbs, ears, bandana and bag. Paint protected head regions rigid, allow controlled flex in the spine/shoulders, constrain stretching and set limb overlap order. Use replacement art where a limb turns or a joint cannot bend convincingly. A whole drawing made entirely rigid or entirely flexible is not an adequate solution.

Best use: reuse rich raster artwork while allowing coordinated torso/hip/shoulder movement and secondary motion. Risk: poor mesh weights or unsuitable joint art produce rubber, collapsing contours or puppet-like motion. Corrective art and good construction remain essential. Desktop rig setup and programmatic automation/access have not been benchmarked here.

Sources:
- https://opentoonz.readthedocs.io/en/latest/create_animations_using_plastic_tool.html
- https://opentoonz.github.io/e/

Official documentation covers deformable meshes, vertex angle limits, rigidity painting, stretch controls, stacking order and linking parts to skeleton vertices. OpenToonz states it is free for commercial and noncommercial work. These features are promising remedies, not evidence of a finished Luna result.

## 3. Full-body motion reference retargeted into 2D drawings
Use legally available canine movement data/footage to guide the entire character, not just touchdown timing. Follow shoulder, hip, elbow, wrist, knee and ankle trajectories together; adapt the motion to Luna's actual short-legged proportions. Construct/redraw the 2D poses around that reference, with restrained artistic exaggeration and tracked contacts. This is reference-guided animation/rotoscoping, not copying another cartoon's character.

Available now: the Catavitello et al. 2015 supporting dataset already inspected locally contains joint coordinates, segment angles and contact timing. Our prior test used timing ratios only; it did not transfer the full measured motion. The reference subjects are not a verified Luna/French-bulldog motion capture session. Naively scaling the data could import inappropriate proportions or movement.

Best use: reduce guesswork about coordination and weight. Risk: literal tracing can be stiff and inappropriate retargeting can still look wrong. Needs stylization, clean drawing and proportion controls; data alone does not create finished animation.

Source:
Catavitello G, Ivanenko YP, Lacquaniti F (2015). Planar Covariation of Hindlimb and Forelimb Elevation Angles during Terrestrial and Aquatic Locomotion of Dogs. PLOS ONE 10(7):e0133936.
https://doi.org/10.1371/journal.pone.0133936
CC BY 4.0, credited use required. The dataset is in the prior restart asset package.

## 4. Small custom hybrid for Luna
Build a purpose-specific animation program rather than an entire new drawing application. Combine authored silhouettes from route 1, localized deformation from route 2, and coordinated reference motion from route 3.

Proposed modules:
1. Reference model: fixed approved head/torso proportions, view-specific silhouette guides, markings and neutral white coat. Reject the sausage-shaped rest drawing.
2. Pose controls: a compact library of correct contact, down, passing and lifted poses, with clean joint/occlusion artwork.
3. Contact solver: preserve support paws and prop contacts while allowing shoulder/hip/root motion.
4. Shape solver: a 2D mesh with rigid skull regions and limited torso/hip flexibility; constrain contour dimensions and detect folded triangles. Soft shape-preserving energies alone do not guarantee body proportions or volume.
5. Corrective shapes: select/blend drawn joint and silhouette corrections when a generic bend is inadequate.
6. Secondary motion: separate delayed response for ears, bandana and satchel, with restrained amplitude and settling.
7. Output/QA: explicit exposure timings, correct leg order, collision/occlusion checks, comparison to model-sheet dimensions, temporal continuity and normal-speed movement inspection.

Research foundations:
- Bounded biharmonic weights support localized controls and preserving selected features:
  https://igl.ethz.ch/projects/bbw/
- As-rigid-as-possible deformation and related methods:
  https://libigl.github.io/tutorial/
  https://igl.ethz.ch/projects/ARAP/arap_web.pdf
- Pose-space corrective deformation:
  Lewis, Cordner and Fong (2000), https://doi.org/10.1145/344779.344862

The custom animation logic can be our implementation of established techniques. This is not a claim of a novel scientific invention or a finished Runway replacement. Use free local drawing/math/export components and verify licenses of any code/model actually incorporated; a paper being readable does not license its implementation. Keep the initial build limited to one coherent stride.

Best use: control exactly the failures observed and make the workflow repeatable through code. Risk: solver and art-preparation work can become a detour. Do not build a general animation platform or insist on custom code when an existing tool meets the target sooner.

## Alternatives screened
- More whole-image interpolation over mismatched poses: not a primary remedy; cannot establish anatomy, timing or newly exposed surfaces.
- AnimeInbet: relevant line-structure research, but its README restricts code to noncommercial use and dataset to CC BY-NC-SA; excluded from production choices.
  https://github.com/lisiyao21/AnimeInbet
- TPS-Inbetween: MIT license shown for its repository, but inference also requires external GlueStick/model weights; full dependency/weight permissions and hardware fit not verified. Do not call the complete pipeline commercially cleared based only on the top-level license.
  https://github.com/Tian-one/tps-inbetween
- Synfig: another free mesh/bone implementation, not a fundamentally distinct fifth method.
  https://synfig.readthedocs.io/en/stable/layers/skeleton_deformation.html
- Blender Grease Pencil can produce 2D work, but changing application or reviving rejected 3D visuals does not solve the present drawing/coordination issue.
  https://www.blender.org/features/story-artist/

## Recommendation and bounded next gate
Engineering judgment: start with a narrow custom hybrid (#4), using #2 as the existing-tool benchmark/fallback, #3 for coordination and #1 for essential pose corrections. The reason is direct control of proportions, whole-body motion, contacts and repeatable rendering; not an assumption that custom code is superior.

First lock the reference silhouette, then prove one complete stride internally at normal speed before detailed scene expansion. If two or three focused revisions do not materially improve one specific failure, change the method instead of stacking patches. If deformation still fails, switch that region or the complete stride to authored drawings. Do not send a new clip merely to ask the owner whether known stiffness/proportion errors remain. Report candidly if the required polish cannot be reached.
