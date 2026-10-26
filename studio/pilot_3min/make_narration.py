import argparse,json,hashlib,os
from pathlib import Path
# Official runtime privacy opt-out MUST precede import/initialization:
# https://github.com/microsoft/onnxruntime/blob/main/docs/Privacy.md
os.environ['ORT_DISABLE_TELEMETRY']='1'
import onnxruntime as ort
ort.disable_telemetry_events()
from kokoro_onnx import Kokoro
import soundfile as sf
p=argparse.ArgumentParser();p.add_argument('--model-dir',type=Path,required=True);a=p.parse_args()
root=Path(__file__).parent;story=json.loads((root/'story.json').read_text())
opts=ort.SessionOptions();opts.intra_op_num_threads=2;opts.inter_op_num_threads=1
session=ort.InferenceSession(str(a.model_dir/'kokoro-v1.0.onnx'),sess_options=opts,providers=['CPUExecutionProvider'])
k=Kokoro.from_session(session,str(a.model_dir/'voices-v1.0.bin'))
report=[]
for i,shot in enumerate(story['shots']):
 if not shot['text']:continue
 dest=root/'audio'/('narration_%02d.wav'%i)
 if not dest.exists():
  samples,sr=k.create(shot['text'],voice=story['narrator'],speed=.96,lang='en-us');sf.write(dest,samples,sr)
 samples,sr=sf.read(dest);seconds=len(samples)/sr
 available=shot['end']-shot['say']-.15
 if seconds>available:
  # Slight delivery-rate adjustment, never truncate a spoken line.
  samples,sr=k.create(shot['text'],voice=story['narrator'],speed=min(1.18,.96*seconds/available*1.02),lang='en-us');sf.write(dest,samples,sr);seconds=len(samples)/sr
 assert shot['say']+seconds<=shot['end']+.15,(i,seconds,available)
 report.append({'shot':i,'start':shot['say'],'seconds':seconds,'text':shot['text'],'file':dest.name})
 print('NARRATION',i,round(seconds,2),flush=True)
(root/'audio/narration-timing.json').write_text(json.dumps(report,indent=2))
print('NARRATION_READY',len(report),flush=True)
