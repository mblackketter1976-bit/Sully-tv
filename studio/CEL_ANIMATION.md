# Local cel assembly

Requires Python 3.10+, Pillow, and FFmpeg on PATH. Draw original cels in a drawing application; export transparent PNGs into a project directory. This tool assembles drawings; it does not create them.

Put this example `sheet.json` beside your own `background.png`, `pose-a.png`, and `pose-b.png`:

```json
{
  "schema": 1,
  "size": [1280, 720],
  "fps": 24,
  "frames": 48,
  "cels": {
    "background": "background.png",
    "a": "pose-a.png",
    "b": "pose-b.png"
  },
  "layers": [
    {"id": "background", "exposures": [{"start": 0, "stop": 48, "cel": "background"}]},
    {"id": "acting", "exposures": [
      {"start": 0, "stop": 24, "cel": "a"},
      {"start": 24, "stop": 48, "cel": "b"}
    ]}
  ]
}
```

Layers composite in list order, bottom to top. Each exposure includes its start frame and excludes its stop frame; a gap is transparent. Layer or exposure `position: [x, y]` sets integer pixel placement. Optional top-level `audio` names a local audio file. Every asset must stay within the sheet's directory. The example holds two poses for a second each; these are two drawings, not 48 drawings.

From the repository root:

```sh
python3 studio/cel_animation.py /path/to/project/sheet.json validate
python3 studio/cel_animation.py /path/to/project/sheet.json render --output /path/to/output.mp4
python3 studio/cel_animation.py /path/to/project/sheet.json onion --frame 23 --output /path/to/proof.png
```

Add `--frames-dir /path/to/frames` to render to export every composed PNG too. The onion command overlays previous/next pixel differences in red/blue; it is a timing proof, not an interactive drawing editor. Video export writes a verification JSON containing drawing hashes and separate source-cel, exposure and output-frame counts.

Verification: five unit tests pass. A separate 64×64 technical fixture exported 24 frames at 24 fps, preserved identical held PNG pixels, switched drawings at the specified frame, produced a difference proof and decoded fully through FFmpeg. This verifies assembly, not Luna's artistic quality.
