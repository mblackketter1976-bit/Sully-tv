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
