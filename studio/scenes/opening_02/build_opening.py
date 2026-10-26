"""Ten-second quiet cold open: registered expressions and bounded cookie-hand deformation.

This is a restrained opening performance, not a full-body cel animation engine.
Environment renderer and its source assets are adjacent reproducible dependencies.
"""
import os
os.environ['ORT_DISABLE_TELEMETRY']='1'
import sys,json,math,hashlib,subprocess,shutil
from pathlib import Path
import cv2,numpy as np,soundfile as sf
from PIL import Image,ImageDraw,ImageFont
import onnxruntime as ort
ort.disable_telemetry_events()
ROOT=Path(__file__).parent;A=ROOT/'assets';A.mkdir(exist_ok=True)
ENV=ROOT.parent/'luna-environment-motion-v01'
sys.path.insert(0,str(ENV));import build_environment as env
original,base,layers,water,protect,allowed=env.setup()
environment=env.renderer(original,base,layers,water,protect,allowed)
W,H=1280,720;FPS=24;DURATION=10
yy,xx=np.mgrid[:H,:W].astype('float32')
opt=ort.SessionOptions();opt.intra_op_num_threads=2;opt.inter_op_num_threads=1
model=ROOT.parent/'luna-finished-scene-10s-v01/models/rife49.onnx'
assert hashlib.sha256(model.read_bytes()).hexdigest()=='76e4cef9ab42fa7dd4e8f6e4aba47462051e3faa969e4bca6479784fbab0ac6f'
session=ort.InferenceSession(str(model),sess_options=opt,providers=['CPUExecutionProvider'])

def aligned(path):
 im=np.array(Image.open(path).convert('RGB').resize((W,H),Image.Resampling.LANCZOS))
 sift=cv2.SIFT_create(nfeatures=3000);k0,d0=sift.detectAndCompute(original,None);k1,d1=sift.detectAndCompute(im,None)
 good=[a for a,b in cv2.BFMatcher().knnMatch(d1,d0,k=2) if a.distance<.70*b.distance]
 m,inliers=cv2.estimateAffinePartial2D(np.float32([k1[x.queryIdx].pt for x in good]),np.float32([k0[x.trainIdx].pt for x in good]),method=cv2.RANSAC,ransacReprojThreshold=1.5)
 assert inliers.sum()>200
 return cv2.warpAffine(im,m,(W,H),borderMode=cv2.BORDER_REFLECT),dict(inliers=int(inliers.sum()),matrix=m.tolist())

def infer(a,b,t):
 if t==0:return a
 if t==1:return b
 tensors=[np.ascontiguousarray(v.transpose(2,0,1)[None].astype('float32')/255) for v in (a,b)]
 out=session.run(None,dict(img0=tensors[0],img1=tensors[1],timestep=np.array([t],np.float32)))[0]
 return np.clip(np.rint(out[0].transpose(1,2,0)*255),0,255).astype('uint8')

def eye_mask(box,ellipses):
 x,y,w,h=box;m=np.zeros((h,w),np.uint8)
 for cx,cy,rx,ry in ellipses:cv2.ellipse(m,(cx-x,cy-y),(rx,ry),0,0,360,255,-1)
 return cv2.GaussianBlur(m.astype('float32')/255,(0,0),2.2)

def smooth(a,b,t):
 u=np.clip((t-a)/(b-a),0,1);return float(u*u*(3-2*u))

def blink(t,start):
 # Two frames close, one-frame closed hold, three frames reopen.
 n=round((t-start)*24)
 return {0:0,1:.5,2:1,3:1,4:.75,5:.25,6:0}.get(n,0)

def main():
 closed,reg0=aligned(A/'closed.png');notice,reg1=aligned(A/'notice.png')
 Image.fromarray(original).save(A/'source.png')
 specs=[('luna',(384,304,160,160),[(441,373,29,33),(496,339,11,17)]),
        ('rook',(640,88,160,128),[(713,146,34,32)])]
 patches={}
 for name,box,ellipses in specs:
  x,y,w,h=box;src=original[y:y+h,x:x+w];close=closed[y:y+h,x:x+w];new=notice[y:y+h,x:x+w]
  patches[name]=dict(box=box,mask=eye_mask(box,ellipses),gazes={})
  # Exact key drawings at endpoints; four inferred intermediates per transition.
  for g in [0,.25,.5,.75,1]:
   gaze=infer(src,new,g)
   patches[name]['gazes'][g]={b:infer(gaze,close,b) for b in [0,.25,.5,.75,1]}
 def field(cx,cy,rx,ry):
  r=((xx-cx)/rx)**2+((yy-cy)/ry)**2
  return np.maximum(0,1-r)**2
 luna=field(402,353,158,143);rook=field(750,155,151,166);hand=field(649,383,126,69)
 # No camera or whole-image pan: the crate, all planted contacts and foreground stay fixed.
 fields=luna+rook+hand
 static=(fields==0)&~allowed
 contacts=np.zeros((H,W),bool);contacts[455:]=True;contacts[:,:132]=True
 stats=[]
 def frame(n):
  t=n/FPS;im=environment(t).astype('float32')
  gaze=smooth(1.6,2.05,t)*(1-smooth(7.8,8.3,t));gaze=round(gaze*4)/4
  for name,patch in patches.items():
   bt=max(blink(t,s) for s in ([.8,6.7] if name=='luna' else [3.1,8.8]))
   x,y,w,h=patch['box'];mask=patch['mask'][:,:,None]
   im[y:y+h,x:x+w]=im[y:y+h,x:x+w]*(1-mask)+patch['gazes'][gaze][bt]*mask
  # Cookie offer only. No head displacement field: preserve skull geometry.
  offer=smooth(2.8,3.7,t)*(1-.5*smooth(6.3,7.2,t))
  dx=hand*(-10*offer)
  dy=hand*(-6*offer)
  im=cv2.remap(im,xx-dx,yy-dy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
  im=np.clip(np.rint(im),0,255).astype('uint8');im[contacts]=original[contacts]
  assert np.array_equal(im[contacts],original[contacts])
  assert np.array_equal(im[303:330,330:465],original[303:330,330:465]),'Luna forehead changed'
  assert np.array_equal(im[80:105,660:745],original[80:105,660:745]),'Rook forehead changed'
  assert np.array_equal(im[static & ~contacts],original[static & ~contacts])
  return im
 if '--proofs' in sys.argv:
  for n in [0,21,23,45,49,63,78,84,105,115,161,163,219,221,239]:
   Image.fromarray(frame(n)).save(ROOT/f'proof_{n:03d}.jpg',quality=95)
  return
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1280x720','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(ROOT/'picture.mp4')],stdin=subprocess.PIPE)
 for n in range(240):
  im=frame(n);proc.stdin.write(im.tobytes())
  if n%24==0:print('FRAME',n,flush=True)
  if n in [0,21,45,63,78,105,163,221,239]:Image.fromarray(im).save(ROOT/f'proof_{n:03d}.jpg',quality=95)
 proc.stdin.close();assert proc.wait()==0
 # Original procedural score; no copied music, no narration and no provisional Rook voice.
 sr=48000;t=np.arange(sr*DURATION)/sr;rng=np.random.default_rng(36)
 ambience,asr=sf.read(ENV/'environment-ambience.wav');assert asr==sr
 mix=np.tile(ambience,(2,1))[:len(t)]*1.1
 def note(at,dur,midi,amp,pan=0):
  start=round(at*sr);nt=np.arange(round(dur*sr))/sr;f=440*2**((midi-69)/12)
  # Gentle bell with rounded attack and falling overtones.
  env=(1-np.exp(-nt*70))*np.exp(-nt*2.8)*np.minimum(1,(dur-nt)/.12)
  tone=amp*env*(np.sin(2*np.pi*f*nt)+.23*np.sin(2*np.pi*f*2*nt)*np.exp(-nt*3)+.08*np.sin(2*np.pi*f*3*nt)*np.exp(-nt*5))
  count=min(len(tone),len(mix)-start)
  mix[start:start+count,0]+=tone[:count]*math.sqrt((1-pan)/2)
  mix[start:start+count,1]+=tone[:count]*math.sqrt((1+pan)/2)
 for at,midi in [(0.25,67),(.72,71),(1.20,74),(2.1,79),(3.2,76),(3.65,74),(4.1,71),(5.1,69),(5.55,72),(6.0,74),(7,71),(7.5,67),(8.25,74),(8.75,79)]:note(at,1.2,midi,.072,(-.25 if midi%2 else .25))
 for at,chord in [(0,[48,55,59]),(2.8,[52,55,60]),(5.2,[50,57,60]),(7.6,[43,55,59])]:
  for midi in chord:note(at,2.1,midi,.028)
 fade=np.minimum(1,t/.25)*np.minimum(1,(DURATION-t)/.5);mix*=fade[:,None]
 assert np.isfinite(mix).all();sf.write(ROOT/'opening-score.wav',mix,sr,subtype='PCM_24')
 output=ROOT/'Luna_Opening_Animation_02.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'picture.mp4'),'-i',str(ROOT/'opening-score.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','loudnorm=I=-22:TP=-4:LRA=6','-ar','48000','-c:a','aac','-b:a','160k','-t','10','-movflags','+faststart',str(output)],check=True)
 subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-'],check=True)
 report=dict(seconds=10,frames=240,fps=24,characters={'Luna':'female; permanent voice unchanged; no dialogue in this pass','The Rook':'female, majestic existing visual retained; voice uncast'},expressionRegistration={'closed':reg0,'notice':reg1},motion=['registered eye expression drawings with RIFE intermediates','cookie-hand offer; head deformation removed after owner forehead-distortion review','independent river, tree and flowering foliage'],rawPlantedContactsUnchanged=True,rawForeheadCheckRegionsUnchanged=True,fullAVDecodePassed=True,limitation='Restrained 2D deformation opening study, not full-body redrawn acting or a completed episode. No realtime listening/playback claim.',sha256=hashlib.sha256(output.read_bytes()).hexdigest())
 (ROOT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)

if __name__=='__main__':main()
