"""Smooth selected held-cel gaps locally with a pinned RIFE v4.9 ONNX model.

RIFE and its weights are MIT licensed. This produces calculated intermediate
video frames, not newly drawn cels. See model-provenance.json for attribution.
"""
import os
# Must be set before importing the runtime, including process initialization.
os.environ['ORT_DISABLE_TELEMETRY'] = '1'
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import onnxruntime as ort
ort.disable_telemetry_events()
from cel_animation import CelScene

MODEL_SHA = '76e4cef9ab42fa7dd4e8f6e4aba47462051e3faa969e4bca6479784fbab0ac6f'
MODEL_URL = 'https://huggingface.co/edgetools/rife/resolve/321b593c5f36c26f5b08fa2838dcf5eece382fa0/rife49.onnx'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--model',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    assert hashlib.sha256(a.model.read_bytes()).hexdigest()==MODEL_SHA,'Wrong model version'
    out=a.output
    assert not out.exists(),'Use a new output directory'
    for name in ['source-cels','derived-frames','licenses']:(out/name).mkdir(parents=True,exist_ok=True)
    settings=ort.SessionOptions()
    settings.intra_op_num_threads=2
    settings.inter_op_num_threads=1
    session=ort.InferenceSession(str(a.model),sess_options=settings,providers=['CPUExecutionProvider'])
    scene=CelScene(a.source/'sheet.json')
    exposures=scene.spec['layers'][0]['exposures']
    keys=[np.asarray(scene.frame(e['start']).convert('RGB')) for e in exposures]
    tensors=[np.ascontiguousarray(im.transpose(2,0,1)[None].astype(np.float32)/255) for im in keys]
    def tween(i,t):
        if t==0:return keys[i].copy()
        value=session.run(None,dict(img0=tensors[i],img1=tensors[i+1],
                                  timestep=np.array([t],dtype=np.float32)))[0]
        return np.clip(np.rint(value[0].transpose(1,2,0)*255),0,255).astype(np.uint8)
    frames=[]
    derived=[]
    for n in range(96):
        i,t=None,0
        if 9<=n<12:i,t=0,(n-8)/4
        elif 12<=n<69:
            i=max(i for i,e in enumerate(exposures) if e['start']<=n)
            t=(n-exposures[i]['start'])/(exposures[i+1]['start']-exposures[i]['start'])
        image=tween(i,t) if i is not None else np.asarray(scene.frame(n).convert('RGB'))
        if t:
            derived.append(dict(frame=n,leftCel=i+1,rightCel=i+2,timestep=t))
            Image.fromarray(image).save(out/f'derived-frames/frame_{n:03d}.png')
        frames.append(image)
        if n%12==0:print(f'Frame {n}/96',flush=True)
    assert len(derived)==41
    for i,e in enumerate(exposures):assert np.array_equal(frames[e['start']],keys[i])
    for n in list(range(9))+list(range(69,96)):
        assert np.array_equal(frames[n],np.asarray(scene.frame(n).convert('RGB')))
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24',
        '-video_size','512x512','-framerate','24','-i','pipe:0','-an','-c:v','libx264',
        '-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'Luna_Smooth_Movement_Test_09.mp4')],stdin=subprocess.PIPE)
    for image in frames:proc.stdin.write(image.tobytes())
    proc.stdin.close()
    assert proc.wait()==0
    subprocess.run(['ffmpeg','-v','error','-i',str(out/'Luna_Smooth_Movement_Test_09.mp4'),'-f','null','-'],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
        '-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',
        str(out/'Luna_Smooth_Movement_Test_09.mp4')]))
    stamps=[float(f['best_effort_timestamp_time']) for f in probe['frames']]
    assert len(stamps)==96 and max(abs(t-n/24) for n,t in enumerate(stamps))<.000002
    for path in (a.source/'cels').glob('*.png'):shutil.copy2(path,out/'source-cels'/path.name)
    source_spec=json.loads((a.source/'sheet.json').read_text())
    source_spec['cels']={name:'source-cels/'+Path(path).name for name,path in source_spec['cels'].items()}
    (out/'source-sheet.json').write_text(json.dumps(source_spec,indent=2))
    if (a.model.parent/'LICENSE').exists():shutil.copy2(a.model.parent/'LICENSE',out/'licenses/RIFE-MIT.txt')
    if (a.model.parent/'README.md').exists():shutil.copy2(a.model.parent/'README.md',out/'licenses/ONNX-model-card.md')
    provenance=dict(model='RIFE v4.9 ONNX',sha256=MODEL_SHA,pinnedUrl=MODEL_URL,
        source='https://github.com/hzwer/Practical-RIFE',
        export='https://huggingface.co/yuvraj108c/rife-onnx',
        mirror='https://huggingface.co/edgetools/rife',license='MIT',
        execution='Local CPUExecutionProvider; ORT_DISABLE_TELEMETRY=1 before import and runtime opt-out',
        numpyVersion=np.__version__,onnxRuntimeVersion=ort.__version__)
    (out/'model-provenance.json').write_text(json.dumps(provenance,indent=2))
    report=dict(sourceDrawings=24,derivedFrames=derived,derivedFrameCount=41,
        totalFrames=96,fps=24,seconds=4,exactRawSourceKeyPosesPreserved=24,
        exactRawBlinkFramesPreserved=list(range(69,75)),exactRawFinalHoldPreserved=list(range(75,96)),
        initialHoldFrames=9,fullDecodePassed=True,encodedTimestampsVerified=True,
        method='Local RIFE inference; calculated intermediate frames, not 41 additional drawings.',
        sourceHashes={path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in (out/'source-cels').glob('*.png')},
        limitation='Source-pixel assertions are before lossy video encoding. Sampling does not prove every anatomical detail or realtime perceived smoothness.')
    (out/'smoothing-audit.json').write_text(json.dumps(report,indent=2))
    proof=Image.new('RGB',(1536,1296),'white')
    draw=ImageDraw.Draw(proof)
    paw=Image.new('RGB',(1536,1296),'white')
    pd=ImageDraw.Draw(paw)
    for j,item in enumerate(derived):
        x,y=j%6*256,j//6*184
        image=Image.fromarray(frames[item['frame']])
        proof.paste(image.resize((176,176)),(x+40,y))
        draw.text((x+8,y+170),f'Frame {item["frame"]}',fill='black')
        paw.paste(image.crop((260,250,512,512)).resize((170,170)),(x+40,y))
        pd.text((x+8,y+170),f'Frame {item["frame"]}',fill='black')
    proof.save(out/'all-derived-frames-review.png')
    paw.save(out/'all-derived-paw-details.png')
    print(json.dumps(dict(output=str(out),sourceDrawings=24,derivedFrames=41,frames=96)),flush=True)


if __name__=='__main__':main()
