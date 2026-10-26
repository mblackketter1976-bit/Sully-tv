# Meticulous registration and timing review 05

The owner requires meticulous cel alignment, sequential pose continuity and correct exposure/playback speed. Revision 05 is a review candidate, not a replacement for the preferred 03 baseline until owner review. No rejected 04 drawings are reused.

`studio/refine_luna_cel_timing.py` reproduces it from the preserved 03 drawings. It leaves all 16 source PNG bytes unchanged and applies only integer layer-position corrections measured against a planted rear-paw patch. Original paw drift was up to 2 px horizontally and 1 vertically; rejected 04 candidate paw drift reached 11 px horizontal and 4 vertical. Match correlation for original cels was >=0.978; post-correction local residual is zero. This local image match does not prove full body/model consistency.

Same 4 seconds / 24 fps / 96 output frames. Pose 13 settle now holds 6 frames (was 4), half blink 14 holds 2 (was 4), closed blink 15 holds 2 (was 3), final pose holds 28 (was 27). Other holds and original pose ordering are preserved. Four displayed blink frames span 166.7ms before reopening. No new drawings, voice, narration or lip-sync claims.

Verified source SHA equality, every exposure lookup, all 96 encoded timestamps against n/24 within 2 microseconds, complete FFmpeg decode, and all 16 labeled composed poses. Side-by-side original/revision video created and decoded. Realtime visual playback and artistic smoothness are not claimed; owner review remains needed. Missing in-betweens and model drift remain. Export verification must not be presented as artistic approval.

Review package (both videos, all cels, timing sheet, registration audit and labeled proof): https://chatgpt.com/library?file_id=libfile_25ddf0beaa948191b8bf68763e1d0880&account_id=personal
