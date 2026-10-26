"""Register the approved 16 PNG cels without redrawing or interpolating them.

Uses a planted rear-paw patch, explicit exposures and integer translation only.
Requires Pillow, NumPy, OpenCV and FFmpeg. Never modifies source files.
"""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from cel_animation import CelScene, render

HOLDS = [12, 4, 3, 6, 4, 3, 6, 4, 4, 4, 4, 4, 6, 2, 2, 28]
LABELS = ['attentive', 'glance', 'turn', 'notice', 'anticipate',
          'react', 'surprise', 'paw lift', 'round mouth', 'open mouth',
          'small mouth', 'paw retract', 'settle', 'half blink',
          'closed blink', 'rest']


def registration(image, patch):
    # Search only around the planted rear paw. Do not track the gesturing paw.
    search = image[380:512, 20:180]
    scores = cv2.matchTemplate(search, patch, cv2.TM_CCOEFF_NORMED)
    _, confidence, _, (x, y) = cv2.minMaxLoc(scores)
    return x - 40, y - 50, float(confidence)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--rejected', type=Path)
    args = parser.parse_args()
    src = args.baseline.resolve()
    dest = args.output.resolve()
    assert src != dest and not dest.exists(), 'Use a new sibling output directory'
    assert sum(HOLDS) == 96
    (dest / 'cels').mkdir(parents=True)
    reference = cv2.imread(str(src / 'cels/pose_01.png'))
    assert reference.shape[:2] == (512, 512)
    patch = reference[430:495, 60:135]
    records, exposures, cels = [], [], {}
    at = 0
    for n, (hold, label) in enumerate(zip(HOLDS, LABELS), 1):
        source = src / f'cels/pose_{n:02d}.png'
        target = dest / f'cels/pose_{n:02d}.png'
        shutil.copy2(source, target)
        sha = hashlib.sha256(source.read_bytes()).hexdigest()
        assert sha == hashlib.sha256(target.read_bytes()).hexdigest()
        image = cv2.imread(str(target))
        dx, dy, score = registration(image, patch)
        assert score >= .97 and abs(dx) <= 3 and abs(dy) <= 2, (n, dx, dy, score)
        # PNG art is unchanged. Placement alone compensates registration drift.
        position = [-dx, -dy]
        cel = f'pose{n}'
        cels[cel] = f'cels/pose_{n:02d}.png'
        exposures.append(dict(start=at, stop=at + hold, cel=cel, position=position))
        aligned = cv2.warpAffine(image, np.float32([[1, 0, -dx], [0, 1, -dy]]),
                                 (512, 512), borderValue=(255, 255, 255))
        rx, ry, after_score = registration(aligned, patch)
        assert (rx, ry) == (0, 0), 'Registration did not settle at the reference'
        records.append(dict(cel=cel, label=label, start=at, stop=at + hold,
                            holdFrames=hold, milliseconds=hold / 24 * 1000,
                            position=position, matchConfidence=score,
                            residualPawOffset=[rx, ry], sha256=sha))
        at += hold
    spec = dict(schema=1, size=[512, 512], fps=24, frames=96,
                background=[255, 255, 255, 255], cels=cels,
                layers=[dict(id='approved drawings, registered', exposures=exposures)])
    (dest / 'sheet.json').write_text(json.dumps(spec, indent=2))
    scene = CelScene(dest / 'sheet.json')
    render(scene, dest / 'Luna_Aligned_Timing_Test_05.mp4')
    # Every drawing appears in order, for exactly its intended exposure length.
    for exposure in exposures:
        for frame in range(exposure['start'], exposure['stop']):
            assert scene.stack(frame) == [(exposure['cel'], tuple(exposure['position']))]
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(dest / 'Luna_Aligned_Timing_Test_05.mp4'),
                    '-f', 'null', '-'], check=True)
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error',
        '-select_streams', 'v:0', '-show_frames', '-show_entries',
        'frame=best_effort_timestamp_time', '-of', 'json',
        str(dest / 'Luna_Aligned_Timing_Test_05.mp4')]))
    stamps = [float(f['best_effort_timestamp_time']) for f in probe['frames']]
    assert len(stamps) == 96
    assert max(abs(t - n / 24) for n, t in enumerate(stamps)) < .000002
    rejected = []
    if args.rejected:
        for path in sorted((args.rejected / 'cels').glob('between_*.png')):
            dx, dy, score = registration(cv2.imread(str(path)), patch)
            rejected.append(dict(file=path.name, pawOffset=[dx, dy], matchConfidence=score))
    audit = dict(fps=24, outputFrames=96, seconds=4, sourceDrawings=16,
                 addedDrawings=0, sourcePixelsPreserved=True, exposures=records,
                 rejectedCandidateMeasurements=rejected,
                 timestampsVerified=True, fullDecodePassed=True,
                 limitations='Rear-paw registration is local. It does not prove anatomical or whole-body consistency, nor artistic quality. No claim of realtime visual playback.')
    (dest / 'timing-and-registration.json').write_text(json.dumps(audit, indent=2))
    # Unchanged source poses and registered composition, labeled for visual audit.
    proof = Image.new('RGB', (1024, 1152), 'white')
    draw = ImageDraw.Draw(proof)
    for n, exposure in enumerate(exposures):
        x, y = n % 4 * 256, n // 4 * 288
        proof.paste(scene.frame(exposure['start']).convert('RGB').resize((256, 256)), (x, y))
        draw.text((x + 8, y + 258), f'{n + 1:02d} {LABELS[n]} | {HOLDS[n]} frames', fill='black')
    proof.save(dest / 'registered-pose-review.png')
    print(json.dumps(dict(output=str(dest), cels=16, frames=96,
                          maxBaselineShift=[max(abs(r['position'][0]) for r in records),
                                            max(abs(r['position'][1]) for r in records)],
                          minimumConfidence=min(r['matchConfidence'] for r in records))))


if __name__ == '__main__':
    main()
