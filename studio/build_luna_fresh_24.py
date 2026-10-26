"""Assemble a fresh 6x4 drawing sheet with two planted-paw registration anchors.

Similarity placement corrects whole-cel scale/rotation/translation only. It does
not synthesize in-betweens, morph anatomy, or recolor the generated artwork.
"""
import argparse
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
from cel_animation import CelScene, render

HOLDS = [12] + [3] * 19 + [2, 2, 2, 21]
ANCHORS = [(50, 135, 430, 500, 0, 220), (180, 270, 430, 510, 100, 360)]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--sheet-art', type=Path, required=True)
    p.add_argument('--model', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output
    for folder in ['raw', 'cels', 'source']:
        (out / folder).mkdir(parents=True, exist_ok=True)
    shutil.copy2(a.sheet_art, out / 'source/fresh-24-sheet.png')
    shutil.copy2(a.model, out / 'source/snow-white-model.png')
    art = Image.open(a.sheet_art).convert('RGB')
    w, h = art.size
    assert w / 6 == h / 4, 'Expected square cells in a 6x4 sheet'
    for n in range(24):
        x, y = n % 6, n // 6
        art.crop((round(x*w/6), round(y*h/4), round((x+1)*w/6), round((y+1)*h/4))).resize(
            (512, 512), Image.Resampling.LANCZOS).save(out / f'raw/cel_{n+1:02d}.png')
    ref = cv2.imread(str(out / 'raw/cel_01.png'))
    targets = np.array([[(x0+x1)/2, (y0+y1)/2] for x0,x1,y0,y1,_,_ in ANCHORS])
    records = []
    exposures = []
    at = 0
    for n, hold in enumerate(HOLDS, 1):
        image = cv2.imread(str(out / f'raw/cel_{n:02d}.png'))
        locations, confidence = [], []
        for (x0,x1,y0,y1,sx0,sx1), target in zip(ANCHORS, targets):
            patch = ref[y0:y1, x0:x1]
            scores = cv2.matchTemplate(image[380:512, sx0:sx1], patch, cv2.TM_CCOEFF_NORMED)
            _, score, _, (x,y) = cv2.minMaxLoc(scores)
            assert score > .90, (n, score)
            locations.append(target + [x+sx0-x0, y+380-y0])
            confidence.append(score)
        locations = np.array(locations)
        v = complex(*(locations[1]-locations[0]))
        desired = complex(*(targets[1]-targets[0]))
        ratio = desired / v
        scale, angle = abs(ratio), math.degrees(math.atan2(ratio.imag, ratio.real))
        assert .92 < scale < 1.08 and abs(angle) < 3, (n, scale, angle)
        linear = np.array([[ratio.real, -ratio.imag], [ratio.imag, ratio.real]])
        shift = targets[0] - linear @ locations[0]
        matrix = np.column_stack([linear, shift])
        residual = locations @ linear.T + shift - targets
        assert np.max(np.abs(residual)) < .00001
        composed = cv2.warpAffine(image, matrix, (512,512), flags=cv2.INTER_LANCZOS4,
                                   borderMode=cv2.BORDER_CONSTANT, borderValue=(255,255,255))
        # Confirm moving-pose art doesn't recolor the planted white foreleg.
        rgb = cv2.cvtColor(composed, cv2.COLOR_BGR2RGB)
        coat = rgb[390:440, 205:245].astype(float)
        light = coat.mean(axis=2) > 160
        warm = float(np.median((coat[:,:,0] - coat[:,:,2])[light]))
        assert warm < 12, (n, warm)
        path = out / f'cels/cel_{n:02d}.png'
        cv2.imwrite(str(path), composed)
        name = f'cel{n:02d}'
        exposures.append(dict(start=at, stop=at+hold, cel=name))
        records.append(dict(cel=name, start=at, stop=at+hold, hold=hold,
            matchConfidence=confidence, matchedSourceAnchors=locations.tolist(),
            targetAnchors=targets.tolist(), similarityMatrix=matrix.tolist(),
            scale=scale, rotationDegrees=angle, fittedAnchorResidual=residual.tolist(),
            whiteForelegMedianRedMinusBlue=warm,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        at += hold
    assert at == 96 and len(exposures) == 24
    spec = dict(schema=1,size=[512,512],fps=24,frames=96,background=[255,255,255,255],
        cels={f'cel{n:02d}':f'cels/cel_{n:02d}.png' for n in range(1,25)},
        layers=[dict(id='fresh snow-white performance', exposures=exposures)])
    (out / 'sheet.json').write_text(json.dumps(spec, indent=2))
    scene = CelScene(out / 'sheet.json')
    render(scene, out / 'Luna_Fresh_24_Cel_Test_07.mp4')
    subprocess.run(['ffmpeg','-v','error','-i',str(out/'Luna_Fresh_24_Cel_Test_07.mp4'),'-f','null','-'],check=True)
    probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
        '-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',
        str(out/'Luna_Fresh_24_Cel_Test_07.mp4')]))
    stamps = [float(f['best_effort_timestamp_time']) for f in probe['frames']]
    assert len(stamps)==96 and max(abs(t-n/24) for n,t in enumerate(stamps)) < .000002
    audit = dict(drawings=24, frames=96, fps=24, seconds=4, exposures=records,
        fullDecodePassed=True, encodedTimestampsVerified=True,
        original16DrawingsReused=False, rejected32DrawingsReused=False,
        limitations='Two template anchors constrain global placement; fitted zero residual is mathematical, not independent pixel/whole-body proof. Remaining model/detail/pose variations need artistic review. No claim of realtime playback.')
    (out / 'registration-and-timing.json').write_text(json.dumps(audit, indent=2))
    proof = Image.new('RGB',(1536,1152),'white')
    draw = ImageDraw.Draw(proof)
    for n,e in enumerate(exposures):
        x,y=n%6*256,n//6*288
        proof.paste(scene.frame(e['start']).convert('RGB').resize((256,256)),(x,y))
        draw.text((x+8,y+258),f'{n+1:02d} | frames {e["start"]}-{e["stop"]-1} | hold {HOLDS[n]}',fill='black')
    proof.save(out/'registered-24-review.png')
    print(json.dumps(dict(drawings=24,frames=96,seconds=4,
        scaleRange=[min(r['scale'] for r in records),max(r['scale'] for r in records)],
        rotationRange=[min(r['rotationDegrees'] for r in records),max(r['rotationDegrees'] for r in records)],
        minConfidence=min(min(r['matchConfidence']) for r in records))))


if __name__=='__main__':
    main()
