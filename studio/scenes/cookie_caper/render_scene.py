import os
os.environ['ORT_DISABLE_TELEMETRY']='1'
import json,math,subprocess,hashlib
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import binary_fill_holes
import soundfile as sf
import onnxruntime as ort
ort.disable_telemetry_events()

ROOT=Path(__file__).parent; ASSET=ROOT/'assets';FPS=24
for name in ['rook-cache','speech-cache','proofs']:(ROOT/name).mkdir(exist_ok=True)
op=ort.SessionOptions();op.intra_op_num_threads=2;op.inter_op_num_threads=1
MODEL_ROOT=Path(os.environ.get('LUNA_SCENE_MODELS',str(ROOT/'models')))
SESSION=ort.InferenceSession(str(MODEL_ROOT/'rife49.onnx'),sess_options=op,providers=['CPUExecutionProvider'])
MATTE_SESSION=ort.InferenceSession(str(MODEL_ROOT/'u2netp.onnx'),sess_options=op,providers=['CPUExecutionProvider'])
MODEL_SHA=hashlib.sha256((MODEL_ROOT/'rife49.onnx').read_bytes()).hexdigest()
assert MODEL_SHA=='76e4cef9ab42fa7dd4e8f6e4aba47462051e3faa969e4bca6479784fbab0ac6f'
assert hashlib.sha256((MODEL_ROOT/'u2netp.onnx').read_bytes()).hexdigest()=='309c8469258dda742793dce0ebea8e6dd393174f89934733ecc8b14c76f4ddd8'

def infer(a,b,t):
 if t<.00001:return a.copy()
 if t>.99999:return b.copy()
 tensors=[np.ascontiguousarray(im.transpose(2,0,1)[None].astype('float32')/255) for im in [a,b]]
 v=SESSION.run(None,dict(img0=tensors[0],img1=tensors[1],timestep=np.array([t],dtype='float32')))[0]
 return np.clip(np.rint(v[0].transpose(1,2,0)*255),0,255).astype('uint8')

def matte(im):
 rgb=np.asarray(im.convert('RGB'))
 small=np.asarray(im.convert('RGB').resize((320,320),Image.Resampling.LANCZOS)).astype('float32')/255
 tensor=(small-np.array([.485,.456,.406],np.float32))/np.array([.229,.224,.225],np.float32)
 value=MATTE_SESSION.run(None,{MATTE_SESSION.get_inputs()[0].name:tensor.transpose(2,0,1)[None]})[0][0,0]
 value=(value-value.min())/max(.0001,float(value.max()-value.min()))
 alpha=cv2.resize(value,im.size,interpolation=cv2.INTER_CUBIC)
 alpha=np.clip((alpha-.05)/.90,0,1)
 if im.width>512:
  # Raven has no white coat: suppress white source-background remnants in
  # the negative spaces between cloak/feet, without filling these holes.
  alpha=np.minimum(alpha,np.clip((245-rgb.min(axis=2).astype(float))/45,0,1))
 rgb=np.clip((rgb.astype(float)-(1-alpha[:,:,None])*255)/np.maximum(alpha[:,:,None],.001),0,255)
 return Image.fromarray(np.dstack([rgb,np.rint(alpha*255)]).astype('uint8'),'RGBA')

ROOK_KEYS=[np.asarray(Image.open(ASSET/f'rook_{n:02d}.png').convert('RGB')) for n in range(12)]
ROOK_TIMES=[0,8,17,22,29,42,54,139,149,164,184,202]
HAND=[(100,220)]*3+[(112,195),(92,214),(93,211),(94,221),(92,219),(100,211),(66,262),(85,265),(90,270)]

def rook_at(frame):
 path=ROOT/'rook-cache'/f'{frame:03d}.png'
 if path.exists():
  try:
   with Image.open(path) as cached:return cached.convert('RGBA')
  except OSError:path.unlink(missing_ok=True)
 i=max(i for i,f in enumerate(ROOK_TIMES) if f<=frame)
 if i==11:im=ROOK_KEYS[i]
 elif i==6 and frame<138:im=ROOK_KEYS[6]
 else:
  t=(frame-ROOK_TIMES[i])/(ROOK_TIMES[i+1]-ROOK_TIMES[i]);im=infer(ROOK_KEYS[i],ROOK_KEYS[i+1],t)
 result=matte(Image.fromarray(im));pending=path.with_suffix('.partial.png');result.save(pending);pending.replace(path);return result

def hand_at(frame):
 i=max(i for i,f in enumerate(ROOK_TIMES) if f<=frame)
 if i==11 or i==6:return np.array(HAND[i],float)
 t=(frame-ROOK_TIMES[i])/(ROOK_TIMES[i+1]-ROOK_TIMES[i]);return (1-t)*np.array(HAND[i])+t*np.array(HAND[i+1])

# Copy the approved movement art into this project once, retaining exact files.
move=ASSET/'luna-move';move.mkdir(exist_ok=True)
source=Path('/workspace/scratch/743bef75a537/luna-cel-fresh-07')
smooth=Path('/workspace/scratch/743bef75a537/luna-cel-smoothing-09')
if not all((move/f'{n:03d}.png').exists() for n in range(96)):
 spec=json.loads((source/'sheet.json').read_text());ex=spec['layers'][0]['exposures']
for n in range(96):
 dest=move/f'{n:03d}.png'
 if dest.exists():continue
 derived=smooth/f'derived-frames/frame_{n:03d}.png'
 if derived.exists():im=Image.open(derived).convert('RGB')
 else:
  cel=next(e['cel'] for e in ex if e['start']<=n<e['stop']);im=Image.open(source/spec['cels'][cel]).convert('RGB')
 im.save(dest)
BASE=np.asarray(Image.open(move/'000.png').convert('RGB'))
mouthmask=Image.new('L',(512,512));md=ImageDraw.Draw(mouthmask)
md.ellipse((219,237,365,289),fill=255)
mouthmask=mouthmask.filter(ImageFilter.GaussianBlur(3));MASK=np.asarray(mouthmask)/255
SPEECH=[BASE]
for i in range(1,6):
 donor=np.asarray(Image.open(ASSET/f'mouth_registered_{i}.png').convert('RGB'))
 donor=cv2.warpAffine(donor,np.float32([[1,0,0],[0,1.25,-40]]),(512,512),borderValue=(255,255,255))
 SPEECH.append(np.rint(donor*MASK[:,:,None]+BASE*(1-MASK[:,:,None])).astype('uint8'))
 Image.fromarray(SPEECH[-1]).save(ASSET/f'luna-speech-{i}.png')
Image.fromarray(BASE).save(ASSET/'luna-speech-0.png')
cues=json.loads((ROOT/'audio/luna-mouth-cues.json').read_text())['mouthCues']
voice,sr=sf.read(ROOT/'audio/luna.wav');VOICE=np.asarray(voice)
speech_states=[]
for frame in range(240):
 t=frame/24-3
 cue=next((e['value'] for e in cues if e['start']<=t<e['end']),'X')
 lo=max(0,int(t*sr));hi=min(len(VOICE),lo+int(.045*sr));energy=float(np.sqrt(np.mean(VOICE[lo:hi]**2))) if hi>lo else 0
 shape={'X':0,'A':0,'B':1,'C':2,'D':3,'E':4,'F':4,'G':5,'H':2}[cue]
 if cue=='B' and energy>.10:shape=2
 if energy<.008:shape=0
 speech_states.append(shape)
speech_pair_cache={}

def speaking(frame):
 path=ROOT/'speech-cache'/f'{frame:03d}.png'
 if path.exists():
  try:
   with Image.open(path) as cached:return cached.convert('RGBA')
  except OSError:path.unlink(missing_ok=True)
 state=speech_states[frame];previous=speech_states[max(0,frame-1)]
 rgb=SPEECH[state]
 if previous!=state:
  key=(previous,state)
  if key not in speech_pair_cache:
   result=infer(SPEECH[previous],SPEECH[state],.5)
   result=np.rint(result*MASK[:,:,None]+BASE*(1-MASK[:,:,None])).astype('uint8');speech_pair_cache[key]=result
  rgb=speech_pair_cache[key]
 # Tiny purposeful head inclination; no planted-paw motion.
 angle=.65*math.sin((frame/24-3)*3.2)
 M=cv2.getRotationMatrix2D((290,295),angle,1)
 turned=cv2.warpAffine(rgb,M,(512,512),borderValue=(255,255,255))
 blend=np.clip((300-np.arange(512)[:,None])/24,0,1)[:,:,None]
 rgb=np.rint(turned*blend+rgb*(1-blend)).astype('uint8')
 im=matte(Image.fromarray(rgb));pending=path.with_suffix('.partial.png');im.save(pending);pending.replace(path);return im

def luna_at(frame):
 t=frame/24
 if 2.4<=t<5.8:return speaking(frame)
 if t<2.4:n=min(45,round(t*18))
 elif t<8.5:n=min(95,round(50+(t-5.8)*15))
 else:n=min(95,round(62+(t-8.5)*24))
 return matte(Image.open(move/f'{n:03d}.png'))

background=Image.open(ASSET/'background.png').convert('RGB').resize((1280,720),Image.Resampling.LANCZOS)
# Original vector-like prop, drawn at 4x and downsampled.
cookie=Image.new('RGBA',(256,256));d=ImageDraw.Draw(cookie)
d.ellipse((10,35,246,222),fill=(143,82,32),outline=(103,58,25),width=6)
d.ellipse((12,22,244,207),fill=(208,158,83),outline=(160,106,47),width=6)
rng=np.random.default_rng(42)
for _ in range(30):
 x,y=rng.uniform(35,220),rng.uniform(42,185)
 if ((x-128)/105)**2+((y-112)/76)**2<1:d.ellipse((x-3,y-3,x+3,y+3),fill=(231,186,110))
for x,y,r in [(69,85,15),(143,63,12),(186,115,13),(105,144,14),(161,162,10),(57,139,9)]:
 d.ellipse((x-r,y-r,x+r,y+r),fill=(68,40,27),outline=(110,65,35),width=3)
cookie=cookie.resize((48,48),Image.Resampling.LANCZOS);cookie.save(ASSET/'cookie.png')
if (ASSET/'cookie-art.png').exists():
 cookie=Image.open(ASSET/'cookie-art.png').convert('RGBA')
 cookie=cookie.crop(cookie.getchannel('A').getbbox()).resize((48,48),Image.Resampling.LANCZOS)
 cookie.save(ASSET/'cookie.png')

def shadow(canvas,x,y,rx,ry,alpha):
 layer=Image.new('RGBA',canvas.size);draw=ImageDraw.Draw(layer);draw.ellipse((x-rx,y-ry,x+rx,y+ry),fill=(12,15,27,alpha));layer=layer.filter(ImageFilter.GaussianBlur(6));canvas.alpha_composite(layer)

def render(frame):
 t=frame/24;canvas=background.convert('RGBA')
 shadow(canvas,426,626,130,13,95);shadow(canvas,1000,626,150,16,110)
 if not 2.4<=t<5.8 and t<8.5:
  rook=rook_at(frame);canvas.alpha_composite(rook,(630,127))
 luna=luna_at(frame).resize((358,358),Image.Resampling.LANCZOS);canvas.alpha_composite(luna,(250,273))
 if 1.20<=t<6.85:
  point=hand_at(frame)+[630,127];point[1]-=16
  size=max(.001,min(1,(t-1.20)/.16));prop=cookie.resize((max(1,round(48*size)),max(1,round(48*size))),Image.Resampling.LANCZOS)
  canvas.alpha_composite(prop,(round(point[0]-prop.width/2),round(point[1]-prop.height/2)))
 elif t>=6.85:
  start=hand_at(164)+[630,111];u=np.clip((t-6.85)/.70,0,1)
  point=(1-u)*start+u*np.array([670,493]);point[1]-=65*math.sin(math.pi*u)
  if u==1:shadow(canvas,670,509,23,4,75)
  if u>=.99:prop=cookie.resize((48,28),Image.Resampling.LANCZOS)
  else:prop=cookie.rotate(-u*35,resample=Image.Resampling.BICUBIC,expand=True)
  canvas.alpha_composite(prop,(round(point[0]-prop.width/2),round(point[1]-prop.height/2)))
 if 2.4<=t<5.8:
  # A deliberate close-up; no repeated zoom pretending to be character acting.
  canvas=canvas.crop((170,270,690,562)).resize((1280,720),Image.Resampling.LANCZOS)
 elif t>=8.5:canvas=canvas.crop((240,260,780,564)).resize((1280,720),Image.Resampling.LANCZOS)
 return canvas.convert('RGB')

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--proofs',action='store_true');p.add_argument('--render',action='store_true');a=p.parse_args()
 if a.proofs:
  for n in [0,18,36,55,60,74,82,91,105,120,137,141,156,164,174,182,194,203,205,218,239]:
   render(n).save(ROOT/'proofs'/f'frame_{n:03d}.png');print('PROOF',n,flush=True)
 if a.render:
  proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1280x720','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'picture.mp4')],stdin=subprocess.PIPE)
  for n in range(240):
   proc.stdin.write(render(n).tobytes())
   if n%24==0:print('RENDER',n,flush=True)
  proc.stdin.close();assert proc.wait()==0
  (ROOT/'scene-timeline.json').write_text(json.dumps(dict(fps=24,frames=240,seconds=10,rookPoseFrames=ROOK_TIMES,lunaSpeechStart=3,shotCuts=[2.4,5.8,8.5],candidateVoices=True,rifeModelSha256=MODEL_SHA,speechStates=speech_states),indent=2))
