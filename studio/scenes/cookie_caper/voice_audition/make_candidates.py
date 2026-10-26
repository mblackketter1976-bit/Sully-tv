import os
os.environ['ORT_DISABLE_TELEMETRY']='1'
import json,hashlib
from pathlib import Path
import onnxruntime as ort
ort.disable_telemetry_events()
import soundfile as sf
from kokoro_onnx import Kokoro
root=Path(__file__).parent;models=Path('/tmp/luna-kokoro')
options=ort.SessionOptions();options.intra_op_num_threads=2;options.inter_op_num_threads=1
session=ort.InferenceSession(str(models/'kokoro-v1.0.onnx'),sess_options=options,providers=['CPUExecutionProvider'])
k=Kokoro.from_session(session,str(models/'voices-v1.0.bin'))
report=[]
for letter,voice,speed in [('A','af_sky',1.0),('B','af_nova',1.0)]:
 x,sr=k.create('Nice trick. Now give back my cookie.',voice=voice,speed=speed,lang='en-us')
 path=root/f'Luna_Younger_Voice_{letter}.wav';sf.write(path,x,sr)
 report.append(dict(option=letter,preset=voice,speed=speed,language='en-us',pitchShift=0,
                    processing='No pitch shift, reverb or echo; audition-reel level matching only',
                    seconds=len(x)/sr,sampleRate=sr,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),file=path.name))
 print(letter,voice,len(x)/sr,flush=True)
data=dict(status='Two younger-direction auditions; neither approved or permanently locked',
 rejectedPreviousDirection='af_bella sounded older than intended to the owner',
 model='Kokoro v1.0 ONNX',modelSha256=hashlib.sha256((models/'kokoro-v1.0.onnx').read_bytes()).hexdigest(),
 voiceBankSha256=hashlib.sha256((models/'voices-v1.0.bin').read_bytes()).hexdigest(),options=report)
(root/'voice-candidates.json').write_text(json.dumps(data,indent=2))
