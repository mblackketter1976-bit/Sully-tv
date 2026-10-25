# Luna motion mechanics

This is a reusable **mechanical benchmark**, not Luna's final rig, artwork, animation or a replacement for Blender/Cartoon Animator.

`locomotion.py` describes a straight, level, four-beat walk in world coordinates. Each leg has a fixed touchdown position during stance. Hip motion is solved through two constant-length segments; impossible targets raise an error rather than stretching the leg. Swing paths meet the ground continuously. Units are metres and seconds, Z points up.

Run checks from the repository root:

```sh
python -m unittest discover -s tests -v
```

No external packages or paid services are used by this core. `benchmark()` returns sampled joint positions and measurements for a future renderer/rig adapter. The 15-second, 24-fps benchmark includes both time endpoints (361 samples); it is not an encoded video.

Limitations: straight walk only; no validated anatomy, joint limits, centre-of-mass/balance simulation, paw orientation/roll, turns, expression, dialogue, skin weights, mesh deformation or renderer adapter. The timing is synthetic and has not been fitted to Luna's real gait. Exact world contacts alone cannot establish natural or attractive animation.

Next acceptance gate: apply the contact targets to an approved character rig, evaluate the deformed mesh/feet in world coordinates, render representative poses, inspect continuity and likeness against the approved art, and only then render the short walk. Preserve source artwork and do not overwrite prior builds.
