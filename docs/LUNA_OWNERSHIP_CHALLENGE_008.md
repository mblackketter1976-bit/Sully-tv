# First three-minute opening: ownership experiment — 2026-10-26

The owner started the challenge with “lets see it,” then confirmed continuing with “go.” Sully owned the story, source preparation, local animation, voice/tool choice, music/foley, edit, checks and deliverable packaging without routine owner decisions. This document records the attempted outcome; it does not declare a finished production cartoon or an equivalent replacement for a generative-video service.

## Actual result

`Luna_First_Three_Minutes_Prototype_01.mp4`: a coherent 180-second opening, 17 shots, 1280×720, 24 fps. Story: Luna's fry investigation is interrupted by three taps, a paw-marked key and a brass box under the Old Sacramento boardwalk. The final encoded file contains a new narrator, original procedural score/foley and caption track rendered into picture. The owner must judge whether this is worth continuing.

The approved illustrated 2D appearance and earlier acting are the basis, not the rejected 3D model. Background/actor separation lets the character move without deforming the whole background. Added a limited paw-placement approach, head/eye/ear acting, breathing, listening-pose motion, original camera compositions, dust and light effects. A listening pose is a separately generated illustration joined through cuts, not a continuously solved change of pose. This remains limited 2D animation with held illustrations, substantial camera moves and a prototype skin-deformation gait. Full-body acting, walking quality, persistent scene interaction and general rig reuse remain unresolved. Do not claim production-level animation or that Runway has been matched/exceeded.

## Audio and dependencies

Luna's established character voice was preserved by using a separate narrator and no character-spoken dialogue. Narration was synthesized locally with Kokoro/ONNX Runtime, `af_heart`; no identity cloning or source-clip audio was used. Model/wrapper licenses were checked through their primary sources. No Runway service, credits, API, proprietary code or source-video motion was used. The built-in image tool supplied new project artwork; the animation/compositing/edit and score/foley are local code. This is not an independently trained generative-image/video model.

An initial speech attempt was rejected by automatic approval review because ONNX Runtime attempted telemetry to Microsoft. Unconfigured inference was not retried. Microsoft's current primary privacy documentation identifies `ORT_DISABLE_TELEMETRY=1` before initialization as preventing the 1DS uploader/events/identifier. The script was changed to set this before import, the supported disable API was also called, and the explicitly configured retry completed all 16 narration segments. No packet-capture/network audit is claimed. Retain that startup control on any new speech execution.

## Checks and handoff

Verified 17 contiguous shot intervals cover exactly 0–180 seconds. Narration segment lengths fit shot windows; speech was regenerated at modestly adjusted delivery rates where necessary instead of truncating words. Procedural mix length/peaks were measured, then mastered with FFmpeg. Source asset hashes and original-code/source files are packaged. Representative scene proofs and decoded final frames were inspected; full-file decode, frame count, streams and caption bounds are checked before delivery. No complete human-style audiovisual viewing or actual Windows performance benchmark is claimed.

The source package includes story/timing, original assets, registered layers, generated narration, score/mix, captions, scripts, README, rebuild notes and verification reports. Model and dependency binaries are not bundled; existing generated speech permits rebuilding without importing the speech runtime. Preserve the earlier approved eight-second tests. If the owner rejects this attempt, retire the approach as a three-minute-production solution, keep useful assets/evidence, and return to smaller rig/acting tests under the philosophy.
