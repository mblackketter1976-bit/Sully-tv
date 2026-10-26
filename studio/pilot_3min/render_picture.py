import argparse,json,math,subprocess,time
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
from rig import ActorRig,camera,ease,keyed,pulse
ROOT=Path(__file__).parent
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'picture.mp4');p.add_argument('--proof',action='store_true');a=p.parse_args()
story=json.loads((ROOT/'story.json').read_text());shots=story['shots'];rig=ActorRig()
assets={name:cv2.resize(cv2.imread(str(ROOT/'assets'/file)),(1280,720)) for name,file in {'background':'background-registered.png','clue':'clue.png','listen':'listen.png','below':'below.png'}.items()}
yy,xx=np.mgrid[:720,:1280].astype(np.float32)
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
fonts={s:ImageFont.truetype(bold if s>=34 else font_path,s) for s in [23,25,28,34,42,58,72]}
def text_center(draw,text,y,font,fill,stroke=0):
 box=draw.textbbox((0,0),text,font=font,stroke_width=stroke);x=(1280-(box[2]-box[0]))/2;draw.text((x,y),text,font=font,fill=fill,stroke_width=stroke,stroke_fill=(6,15,25,255))
blink_times=[24.5,30.7,46.2,58.3,67.4,73.4,124.3,129.6,157.2,163.1,178.7]
def closure(t):
 for b in blink_times:
  u=t-b
  if 0<u<.12:return ease(u/.12)
  if .12<=u<.20:return 1.
  if .20<=u<.37:return 1-ease((u-.20)/.17)
 return 0.
tilts=[(0,0),(23,0),(29,-1.6),(32,0),(43,2),(47,3),(51,-1),(54,0),(60,2),(64,0),(66,-3),(70,-3),(74,1),(76,0),(122,0),(125,3.4),(129,-1.7),(132,0),(155,0),(159,-2),(163,-1),(166,0),(175,0),(177,-2.2),(180,-1)]
def actor(t,walk=False):
 gaze=(0,0)
 if 34<t<51:gaze=(-2.6,2.9)
 elif 54<t<60:gaze=(-2.0,-1.7)
 elif 65<t<75:gaze=(0,-1)
 elif 122<t<128:gaze=(-2,3)
 elif 157<t<164:gaze=(-2.5,-1.8)
 ear=sum(1.8*pulse(t,b,.65) for b in [65.7,68.0,70.2,123.2,158.7,176.2])
 paw=.7*pulse(t,48,.9)+.6*pulse(t,126,.8)
 return rig.frame(max(0,t-19) if walk else t,walk=walk,tilt=keyed(t,tilts),gaze=gaze,blink=closure(t),ear=ear,paw=paw)
def render(t):
 shot=next(s for s in shots if s['start']<=t<s['end']);kind=shot['scene'];u=(t-shot['start'])/(shot['end']-shot['start'])
 if kind in ['establish','title']:
  frame=camera(assets['background'],1.12-.08*ease(u),650+22*ease(u),350)
 elif kind=='arrive':frame=actor(t,True)
 elif kind=='fry':frame=camera(assets['background'],2.65+.15*ease(u),355,601)
 elif kind=='temptation':frame=camera(actor(t),1.40+.10*ease(u),691,337)
 elif kind=='boots':frame=camera(actor(t),1.12,570-30*ease(u),398)
 elif kind=='alert':frame=camera(actor(t),1.48+.08*ease(u),705,306)
 elif kind in ['listen','listen_close']:
  src=assets['listen'];weight=np.exp(-((xx-740)/195)**4-((yy-360)/160)**4).astype(np.float32)
  sway=.9*math.sin(2*math.pi*t/3.1);frame=cv2.remap(src,xx+.45*sway*weight,yy+sway*weight,cv2.INTER_CUBIC)
  frame=camera(frame,1.04+.10*ease(u) if kind=='listen' else 1.32+.08*ease(u),720,380 if kind=='listen' else 390)
 elif kind=='gap':frame=camera(assets['background'],2.0+.15*ease(u),760,590)
 elif kind in ['clue','key_return']:
  src=assets['clue'].astype(np.float32)
  glint=(.18+.45*pulse(t,112.4,1.4)+.6*pulse(t,168.0,1.5))*np.exp(-((xx-552)/33)**2-((yy-478)/17)**2)
  src+=glint[:,:,None]*np.array([50,95,130],np.float32)
  frame=camera(np.clip(src,0,255).astype(np.uint8),1.05+.17*ease(u),640,417)
 elif kind in ['below','keyhole']:
  src=assets['below'].astype(np.float32)
  glow=(.15+.14*math.sin(t*1.8))*np.exp(-((xx-988)/53)**2-((yy-388)/65)**2)
  src+=glow[:,:,None]*np.array([70,75,8],np.float32)
  for n in range(13):
   px=int(220+(n*67+t*(2+n%3))%950);py=int(115+(n*41+t*(1+n%2))%310)
   cv2.circle(src,(px,py),1,(130,195,230),-1)
  frame=camera(np.clip(src,0,255).astype(np.uint8),1.02+.15*ease(u) if kind=='below' else 1.65+.1*ease(u),670 if kind=='below' else 990,365 if kind=='below' else 390)
 elif kind=='wonder':frame=camera(actor(t),1.35+.1*ease(u),690,345)
 elif kind=='resolve':frame=camera(actor(t),1.10+.06*ease(u),665,360)
 elif kind=='hook':frame=camera(actor(t),1.28+.13*ease(u),695,325)
 else:raise ValueError(kind)
 # Deliberate photographic composition; modest matte leaves captions off paws.
 frame[:18]=0;frame[-42:]=0
 if kind=='title':
  im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert('RGBA');dark=Image.new('RGBA',im.size,(3,12,24,105));im=Image.alpha_composite(im,dark);d=ImageDraw.Draw(im)
  text_center(d,'LUNA',210,fonts[72],(255,225,164,255),2)
  text_center(d,'ON THE STREETS',296,fonts[42],(255,246,225,255),1)
  text_center(d,'THE SECRET UNDER OLD SAC',375,fonts[28],(240,220,178,255),1)
  text_center(d,'Created by Michael Blackketter',485,fonts[23],(228,231,235,255))
  frame=cv2.cvtColor(np.array(im.convert('RGB')),cv2.COLOR_RGB2BGR)
 # Short fade-in/out only; no repeated clips or stretched source-video motion.
 fade=min(ease(t/1.1),ease((180-t)/1.2))
 if fade<1:frame=np.rint(frame.astype(np.float32)*fade).astype(np.uint8)
 return frame,kind

if a.proof:
 for t in [3,15,22,27,36,47,59,68,80,92,103,115,126,137,148,159,170,177]:
  frame,kind=render(t);cv2.imwrite(str(ROOT/'review'/('shot_%03d_%s.png'%(t,kind))),frame)
 print('PICTURE_PROOFS_READY',flush=True)
else:
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','bgr24','-video_size','1280x720','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)],stdin=subprocess.PIPE)
 started=time.monotonic()
 for i in range(4320):
  frame,kind=render(i/24);proc.stdin.write(frame.tobytes())
  if i%240==0:print('PICTURE_SECONDS',i/24,'renderElapsed',round(time.monotonic()-started,1),kind,flush=True)
 proc.stdin.close();assert proc.wait()==0
 print('PICTURE_READY',4320,flush=True)
