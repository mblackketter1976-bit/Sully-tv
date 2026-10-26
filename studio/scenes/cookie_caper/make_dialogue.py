import os
os.environ['ORT_DISABLE_TELEMETRY']='1'
import json,hashlib
from pathlib import Path
import onnxruntime as ort
ort.disable_telemetry_events()
from kokoro_onnx import Kokoro
import soundfile as sf

root=Path(__file__).parent
model=Path(os.environ.get('KOKORO_MODEL_DIR','/tmp/luna-kokoro'))
options=ort.SessionOptions();options.intra_op_num_threads=2;options.inter_op_num_threads=1
session=ort.InferenceSession(str(model/'kokoro-v1.0.onnx'),sess_options=options,providers=['CPUExecutionProvider'])
k=Kokoro.from_session(session,str(model/'voices-v1.0.bin'))
lines=[
 dict(id='rook_1',character='The Rook',text='A little misdirection.',voice='bm_george',lang='en-gb',speed=1.03,start=.6),
 dict(id='luna',character='Luna',text='Nice trick. Now give back my cookie.',voice='af_bella',lang='en-us',speed=.95,start=3.0),
 dict(id='rook_2',character='The Rook',text='Worth a try.',voice='bm_george',lang='en-gb',speed=1.03,start=7.0)
]
for line in lines:
 audio,sr=k.create(line['text'],voice=line['voice'],speed=line['speed'],lang=line['lang'])
 dest=root/'audio'/(line['id']+'.wav');sf.write(dest,audio,sr)
 (root/'audio'/(line['id']+'.txt')).write_text(line['text'])
 line.update(file=dest.name,sampleRate=sr,samples=len(audio),seconds=len(audio)/sr,
             sha256=hashlib.sha256(dest.read_bytes()).hexdigest())
 print(line['id'],line['seconds'],flush=True)
report=dict(status='Candidate character voices, not permanently approved',lines=lines,
 model='Kokoro v1.0 ONNX',modelSha256=hashlib.sha256((model/'kokoro-v1.0.onnx').read_bytes()).hexdigest(),
 voicesSha256=hashlib.sha256((model/'voices-v1.0.bin').read_bytes()).hexdigest(),
 voiceProcessing='No pitch shift, no added reverb, no echo; level mix only',
 license='Kokoro model Apache-2.0; kokoro-onnx wrapper MIT',
 telemetry='ORT_DISABLE_TELEMETRY=1 set before runtime import; runtime opt-out too')
(root/'audio/voice-candidates.json').write_text(json.dumps(report,indent=2))
