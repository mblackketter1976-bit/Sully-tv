# Active Blackketter Entertainment work — 2026-10-26

> OWNER DIRECTION: Luna is 2D illustrated animation matching the supplied 1156/1135/1149 Runway references. 3D appearance work was explicitly rejected; earlier movement approval did not approve the 3D visual direction. Read `docs/LUNA_2D_TARGET_006.md` on the Luna branch before continuing Luna.

Both projects remain active. Preserve the charter, accepted movement files and working features.

## Sully TV
- Branch `sully-phase1-foundation-audit`; draft https://github.com/mblackketter1976-bit/Sully-tv/pull/1 .
- Licensed partial TVmaze schedules for three exactly mapped US networks, source/license credit, browser refresh/cache/failure preservation and current-data download remain implemented.
- Guide navigation now sits in normal page flow with 44px action targets. Duplicate room controls and overlapping floating navigation are hidden only while the guide is open.
- Verified 25 Python tests, JS normalization, isolated and full-HTML browser tests at 1280px/390px. Phone/desktop screenshots inspected. Functional run: https://github.com/mblackketter1976-bit/Sully-tv/actions/runs/40247545090 .
- Limits: partial episode coverage; no assertion listings match each stream; no real device/Safari/install test. The owner-approved navigation repair is live on main (13344a0). The sourced-guide build remains in development.
- Evidence: `docs/TV_GUIDE_PROVIDER_003.md`, `data/TV_GUIDE_LICENSE.md`.

## Luna
- Branch `luna-grounded-motion-benchmark`; draft https://github.com/mblackketter1976-bit/Sully-tv/pull/2 . Studio sources are on that branch.
- Actual uploaded V41 inspected in Blender 5.2.2 LTS. Historical V6 remains reference-only.
- Owner accepted `Luna_V41_Stop_Contact_Test.blend`, then `Luna_V41_Turn_Weight_Blink_Test.blend` (first WOW). Aesthetics explicitly deferred.
- New `Luna_Walk_Stop_Turn_Look.blend`: 18 seconds, approved walk/stop joined to approved turn/look/blink; both accepted sources unchanged. Reopened verification compares all 193 opening frames and ten turn poses; world vertex errors below 2.5e-7 scene units. Representative renders inspected.
- Deliverable: https://chatgpt.com/library?file_id=libfile_8292cdce421c8191bf92157f724cbab4&account_id=personal . Open and press Space. No scripts need running for playback.
- Evidence on Luna branch: `docs/LUNA_V41_AUDIT_002.md`, `docs/LUNA_V41_TURN_003.md`, `docs/LUNA_V41_SEQUENCE_004.md`. Rebuilders under `studio/`.
- Limits: movement prototype, existing art/proportions, mesh-pose approach, no calibrated physical mass model or Windows playback benchmark. Do not ask again for the already supplied V41 or treat movement approval as final appearance approval.

## Current handoff — 2026-10-26
- Accepted live navigation: one bottom bar for Back, Home, Categories, Search and Top, responsive quick controls/search, restored app icons. Main navigation CI and Pages deployment passed; public HTTP verified.
- Guide development now incorporates that exact accepted navigation, removes duplicate guide controls and makes dock Search focus the station field. Python, guide browser and four-width navigation tests passed in run 40249222384. Real provider fetch returned 52 current/future episode entries across three reviewed networks; coverage remains partial. No guide release was made.
- Luna appearance is now requested. First native 3D visual proposal: rest-coordinate silver merle, retained blue eyes, sculpted bat ears, warm studio. All 432 frames preserve evaluated paw vertices and root matrices exactly (zero difference from accepted sequence). Representative poses inspected; six-second rendered turn excerpt and full 18-second Blender scene are being prepared for owner appearance review. Preserve earlier motion files and do not assume final likeness approval. See docs/LUNA_VISUAL_005.md on the Luna branch.

## Luna correction and first 2D test
- Primary reference: 1156.mp4 (Library libfile_aa8a278a4cc88191983cff3536784ec9); captioned references 1135/1149 also supplied.
- New Luna_2D_Acting_Test_01.mp4 uses one approved still, local 2D deformation, edited eyelid patches, two blinks and subtle breathing. Eight seconds, 24 fps, 1280×720. It does not replay or retime the source clip. Raw paws and outer background are pinned; no full walking/turn rig or episode pipeline is claimed.
- Historical 3D files remain preserved as experiments only. New 2D test awaits owner review.

## Accepted 2D baseline and expression follow-up
The owner approved local 2D test 01 movement and blink. Preserve it. Artwork was created with the assistant; only earlier reference motion was Runway. Test 02 adds a small fry-directed glance and asymmetric ear perk while retaining accepted timing. Seven sampled neutral/blink/return images match baseline exactly; raw paws/outer-background differences remain zero. Test 02 awaits review. No Runway dependency or new image-generation call. See LUNA_2D_EXPRESSION_007.md.

## Authorized ownership challenge — first three minutes
The owner started the three-minute opening challenge with “lets see it” and confirmed “go.” A 17-shot, 180-second narrated limited-2D prototype has been assembled; it is not a finished production cartoon or a demonstrated Runway replacement. Preserve the accepted 2D test 01. New narrator is separate from Luna’s established voice. Original local score/foley, no Runway service or source-video motion. See LUNA_OWNERSHIP_CHALLENGE_008.md and source under studio/pilot_3min. Owner review determines whether to continue or slow down.

## Latest owner series rules — dialogue, voice and cast
Dialogue-led animal cartoon; only Mike and Nicol are the humans who understand Luna. Narration only when a specific scene needs explanation. The narrator prototype is not the series format. Lock Luna’s permanent character voice only after explicit sample approval, saving exact settings and a reference. No new character voice is currently approved. Blue/Duke/Sterling animal sketches are proposals, not final cast/likeness approvals. YouTube movement link supplied but not viewed: browser auto-review blocked a Google-origin access request, so an uploaded clip/excerpt is needed. See LUNA_SERIES_BIBLE_009.md before continuing.

## Movement reference now supplied and inspected
The owner uploaded 1785.mp4 (Library libfile_b5601b9604b881919630e5e6938df141), resolving the need for accessible video after the Google-origin browser block. Local timeline/consecutive samples show pose-to-pose acting, prop interaction, meaningful holds/quick accents and expressive mouth/body changes. Keep our illustrated art; do not copy the reference cartoon’s designs/footage. The narrated prototype is below this acting target. Next gate is a short speaking/acting proof with deliberate mouth/expression poses and a purposeful paw/prop action, before expanding length again. See LUNA_MOVEMENT_REFERENCE_010.md.


## Authored cel workflow — 2026-10-26
The owner authorizes traditional frame-by-frame drawing and custom production tools. See `LUNA_CEL_WORKFLOW_011.md` and `studio/CEL_ANIMATION.md`. The new local PNG-cel compositor passed five unit tests and a 24-frame FFmpeg export/decode smoke test. It provides assembly and timing; a new Luna acting sequence is still to be drawn and judged.


## Latest Luna review deliverable: ten-second Cookie Caper sound scene
Owner requested an independently completed ten-second picture-and-sound example. Delivered 1280x720/24fps, 240 frames, ten seconds, dialogue-led G-target cookie gag with The Rook and snow-white Luna. Candidate voices are not locked. See `LUNA_TEN_SECOND_SOUND_SCENE_017.md` for result, actual verification and remaining limits.

Video: https://chatgpt.com/library?file_id=libfile_89d2e6a8e24c81919f1d007ad79f2c95&account_id=personal

Asset/audio package: https://chatgpt.com/library?file_id=libfile_962d9302f924819187cd01a48bca5e26&account_id=personal


## Permanent Luna voice — APPROVED, October 25, 2026 (Pacific)
The owner explicitly approved the younger Voice B audition with “That's Luna.” This is now Luna's permanent character voice. Canonical settings: `studio/voices/luna/voice-lock.json`. Base Kokoro v1.0 ONNX / af_nova / speed1.0 / en-us, followed by Praat formant1.18, target median310Hz, range1.08, duration1.0 and the documented level rule. Preserve this pipeline and approved reference WAV rather than the older af_bella scene voice or unprocessed adult B. Model/voice-bank/reference hashes and exact runtime versions are recorded. Reference WAV: https://chatgpt.com/library?file_id=libfile_463bcad4e1488191837470d46d52b62f&account_id=personal . This supersedes earlier candidate status only for Luna. Rook's voice is not approved by this decision. Do not change Luna's age/tone/voice identity without the owner's direction.


## Latest environment-motion proof
Eight-second immersive staging proof with independent water/reflections and foliage, protected actor/prop contacts, and quiet ambience. Actors intentionally hold pose; future performance layers are documented rather than claimed complete. Approved Luna voice remains locked. See `LUNA_ENVIRONMENT_MOTION_023.md`.

Video: https://chatgpt.com/library?file_id=libfile_8ede3994732481918958032d2c82fa86&account_id=personal
Layers: https://chatgpt.com/library?file_id=libfile_fc223bfd1c9481919d8235a277a052aa&account_id=personal


## The Rook — female direction, October 25, 2026 (Pacific)
The owner now prefers the main villain to be female: “I wonder if we should make the villain female. I like that better I think.” Proceed with The Rook as she/her. Preserve the existing majestic raven design Nicol called majestically beautiful: iridescent blue-green feathers, elegant cloak, beak and silver clasp. No visual redesign or stereotyped gender cues are needed. She is charming, witty, courteous and mischievous, with family-friendly schemes. Earlier male pronouns and bm_george audition are historical, not a locked identity or permanent voice. Her voice remains uncast; Luna's approved permanent voice is unchanged.

The owner enthusiastically praised the immersive environment-motion proof (“Wow!!”, “That looks like disney”) and requested opening animation. Keep that accepted visual/environment direction, retaining original character identity. Opening pass 01 adds registered eye-expression drawings, independent blinks, localized head response and cookie-hand offer. It is restrained 2D deformation, not full-body redrawn cel acting or a finished episode opening.

See LUNA_OPENING_024.md for the ten-second opening pass and verification.


## Latest Luna walk study
Owner requested Luna walking. Six-second boardwalk walk study uses six selected pose drawings, 18 inferred intermediates in a 24-frame cycle, eye-based horizontal registration, support-line placement, forward travel, contact shadow, foreground post overlap, original synthesized paw taps and ambience. First satchel registration and five-key attempt were revised for head drift and a ghosted leg transition; all final 24 cycle frames inspected. Full A/V decode and 144-frame export verified. Still approximate support/stride matching, not a verified no-slip rig or production walk approval. Luna voice and female Rook direction retained. See LUNA_BOARDWALK_WALK_026.md.

Video: https://chatgpt.com/library?file_id=libfile_27c51a5a76148191bafd31dc297d1b33&account_id=personal
Assets: https://chatgpt.com/library?file_id=libfile_466fb92891648191bdfd1dec81de98c5&account_id=personal
