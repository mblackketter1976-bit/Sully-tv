# Ten-second sound scene — Cookie Caper

The owner asked Sully to independently show ten seconds of a finished animated product with sound, checking and fixing issues throughout. They plan to pause PC work around 8:30pm and continue from their phone. Connection interruptions occurred; the work was preserved and resumed. This deliverable is the current finished-scene proposal for review, not a claim of flawless broadcast readiness or official G classification.

Story: on the Old Sacramento boardwalk, The Rook reveals a cookie with “A little misdirection.” Luna answers “Nice trick. Now give back my cookie.” He tosses it back to the crate and admits “Worth a try.” Ends on Luna's reaction. No narrator or humans. All-ages tone, neutral snow-white merle Luna with blue eyes, charming rather than menacing Rook.

Picture uses the fresh 24-cel Luna with local RIFE intermediates, six localized mouth drawings with Rhubarb plus energy timing, twelve new Rook poses, original painted background and illustrated cookie. Rook beak articulation remains coarser than Luna's mouth cues; source/model/detail and edge imperfections remain possible. Code is `studio/scenes/cookie_caper/`. Assets/models/audio are in the saved package, rather than a duplicate large public git payload.

Fixed during build: regular-grid slicing clipped three Rook heads, so used actual row boundaries and foot registration; white-mask hole filling wrongly retained negative spaces, so replaced it with local U2Netp semantic matting and raven white-background suppression; localized Luna mouth patch initially copied scarf detail, so restricted and fitted it to the muzzle; close-up initially exposed a disconnected cookie at screen edge, so reframed it; replaced placeholder prop with an illustrated cookie.

Audio: character dialogue, original procedural G-major musical punctuation, feather rustles, glints, cookie landing tap and quiet riverfront air. No reference-video audio, Runway, paid credits, or added voice echo/reverb. Master measured -15.67 LUFS / -3.98 dBTP before AAC. Final decoded sample peak 0.63244.

Candidate voices (NOT permanent approvals): Luna `af_bella`, speed .95, en-us; Rook `bm_george`, speed1.03, en-gb, Kokoro v1.0 ONNX. Exact model/voice-bin/WAV hashes, rates and mix gains are saved in `voice-candidates.json` and package audio reports. If owner approves, retain these settings and reference WAV as the voice lock; do not infer approval from merely producing the scene.

Verification: MP4 H.264 1280x720 yuv420p, 24fps, exactly 240 decoded frames, 10sec; AAC stereo48k metadata10sec (decoded AAC adds5.33ms padding); every video timestamp matches n/24; entire A/V decode passes, no clipping. Inspected 21 composed proofs and six decoded final frames, including speech, gesture, return and shot cuts. Did not claim realtime viewing/listening. SHA256: `606119abcc5f7ae062a0bbcd7831b4c79862f673f4fdc2f09cb6cf0ca5dd51ef`.

Video: https://chatgpt.com/library?file_id=libfile_89d2e6a8e24c81919f1d007ad79f2c95&account_id=personal

Assets, local interpolation/matting models with licenses, audio stems, captions, timing and verification: https://chatgpt.com/library?file_id=libfile_962d9302f924819187cd01a48bca5e26&account_id=personal
