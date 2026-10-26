# Phone-session contact pass and series finish level

The owner returned on their phone and authorized continuing tonight, with PC work tomorrow. They liked Cookie Caper, but found the cookie's landing clumsy/blocky. They clarified the series should be a nice, lively cartoon mainly for children, compelling for parents, without pursuing movie-level perfection. Fix distractions and move the story forward; cinematic polish is for the movie.

Revision 02 keeps the ten-second scene, character acting and audio master. The cookie's projected height and roll now change continuously during its flight, rather than switching abruptly from a rotated 48px sprite to a flat 28px sprite at impact. It contacts at 7.55s, makes a small damped bounce, slides 2.2px, and settles against a fixed tabletop plane with a contact shadow. This is simple cartoon motion, not a full physics simulation. The original delivered scene is unchanged.

Verified contact position/height continuity, no mathematical ground penetration over sampled settling trajectory, 240 frames/24fps/10sec, full video/audio decode, and decoded audio peak0.63244. Six decoded landing details inspected. No full realtime playback claim. Parent scene beak-sync/detail limitations remain. Voices are still candidates, not permanently locked.

Three damaged derived-cache PNGs were detected during the first render retry. Source assets and accepted final clip were preserved. Derived frames were regenerated. The renderer now replaces cache files atomically and regenerates unreadable cache images, preventing a damaged temporary image from permanently blocking a resumed render.

Code: `studio/scenes/cookie_caper/cookie_contact_pass.py` and the cache-handling update to `render_scene.py`. Use the previously saved Cookie Caper assets/audio package beside those scripts; no repeat purchase, installation or owner physical step required for this session's work.

Video: https://chatgpt.com/library?file_id=libfile_3c2f8e69d20c819182dd4e871cfc1551&account_id=personal
