"""Registered authored walk poses, inferred intermediates and ground-plane travel."""
import os
os.environ['ORT_DISABLE_TELEMETRY']='1'
import json,math,subprocess,hashlib,shutil
from pathlib import Path
import cv2,numpy as np,soundfile as sf
from PIL import Image,ImageDraw,ImageFilter
import onnxruntime as ort
ort.disable_telemetry_events()
R=Path(__file__).parent;A=R/'assets';A.mkdir(exist_ok=True);C=R/'cycle';C.mkdir(exist_ok=True)
W,H=1280,720;FPS=24;SECONDS=6
model=R.parent/'luna-finished-scene-10s-v01/models'
op=ort.SessionOptions();op.intra_op_num_threads=2;op.inter_op_num_threads=1
rife=ort.InferenceSession(str(model/'rife49.onnx'),sess_options=op,providers=['CPUExecutionProvider'])
segment=ort.InferenceSession(str(model/'u2netp.onnx'),sess_options=op,providers=['CPUExecutionProvider'])

def matte(rgb):
 small=cv2.resize(rgb,(320,320)).astype('float32')/255
 tensor=(small-np.array([.485,.456,.406],np.float32))/np.array([.229,.224,.225],np.float32)
 v=segment.run(None,{segment.get_inputs()[0].name:tensor.transpose(2,0,1)[None]})[0][0,0]
 v=(v-v.min())/max(.0001,float(v.max()-v.min()))
 alpha=np.clip((cv2.resize(v,(rgb.shape[1],rgb.shape[0]),interpolation=cv2.INTER_CUBIC)-.035)/.93,0,1)
 # Discard detached segmentation flecks while retaining the connected dog.
 count,labels,stats,_=cv2.connectedComponentsWithStats((alpha>.12).astype('uint8'))
 largest=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]));keep=(labels==largest).astype('uint8')
 keep=cv2.dilate(keep,np.ones((3,3),np.uint8));alpha*=keep
 color=np.clip((rgb.astype(float)-(1-alpha[:,:,None])*255)/np.maximum(.001,alpha[:,:,None]),0,255)
 return Image.fromarray(np.dstack([color,np.rint(alpha*255)]).astype('uint8'),'RGBA')

def infer(a,b,t):
 if t==0:return a
 ins=[np.ascontiguousarray(im.transpose(2,0,1)[None].astype('float32')/255) for im in (a,b)]
 v=rife.run(None,dict(img0=ins[0],img1=ins[1],timestep=np.array([t],np.float32)))[0]
 return np.clip(np.rint(v[0].transpose(1,2,0)*255),0,255).astype('uint8')

def main():
 sheet=np.array(Image.open(A/'walk-sheet.png').convert('RGB'));sh,sw=sheet.shape[:2]
 # Generated repeats are excluded. These six keys have coherent near-foreleg
 # progression: forward contact -> under shoulder -> back -> lifted -> reach.
 order=[0,1,2,5,6,7];keys=[];registration=[]
 for n in order:
  x0=(n%4)*sw//4;x1=(n%4+1)*sw//4;y0=(n//4)*sh//2;y1=(n//4+1)*sh//2
  cell=sheet[y0:y1,x0:x1];rgba=matte(cell);aa=np.array(rgba.getchannel('A'))
  ys,xs=np.where(aa>200);bottom=int(ys.max())
  # Identify body colors and register the blue near-eye, not moving paws.
  rr,gg,bb=cell[:,:,0].astype(float),cell[:,:,1].astype(float),cell[:,:,2].astype(float)
  yy,xx=np.mgrid[:cell.shape[0],:cell.shape[1]]
  olive=(rr>35)&(rr<175)&(gg>rr*.65)&(gg<rr*1.20)&(bb<gg*.70)&(xx<cell.shape[1]*.56)&(yy>cell.shape[0]*.28)&(yy<cell.shape[0]*.66)&(aa>220)
  # Use the blue near-eye as the horizontal registration anchor so
  # changing bag silhouettes do not rock the head back and forth.
  blue=(bb>rr*1.20)&(gg>rr*1.10)&(bb>90)&(gg>65)&(xx>cell.shape[1]*.60)&(yy<cell.shape[0]*.52)&(aa>220)
  count,labels,stats,cent=cv2.connectedComponentsWithStats(blue.astype('uint8'))
  candidates=[i for i in range(1,count) if stats[i,cv2.CC_STAT_AREA]>8]
  assert candidates
  eye=max(candidates,key=lambda i:stats[i,cv2.CC_STAT_AREA]);anchor=float(cent[eye,0])
  dx=round(370-anchor);dy=480-bottom
  canvas=Image.new('RGB',(512,512),'white');canvas.paste(Image.fromarray(cell),(dx,dy));rgb=np.array(canvas)
  Image.fromarray(rgb).save(A/f'key_{n:02d}.png');keys.append(rgb)
  registration.append(dict(sourceCell=n,blueEyeAnchorX=anchor,groundY=bottom,placement=[dx,dy]))
 timing=[0,6,10,14,18,22,24]
 for f in range(24):
  path=C/f'{f:03d}.png'
  if path.exists():continue
  i=max(i for i,t in enumerate(timing[:-1]) if t<=f);t=(f-timing[i])/(timing[i+1]-timing[i])
  rgb=infer(keys[i],keys[(i+1)%len(keys)],t);rgba=matte(rgb)
  # Pin the common support line without scaling/deforming any head or limb.
  alpha=np.array(rgba.getchannel('A'));ys,xs=np.where(alpha>200);dy=480-int(ys.max())
  out=Image.new('RGBA',(512,512));out.alpha_composite(rgba,(0,dy));out.save(path)
  print('CYCLE',f,flush=True)
 bg=np.array(Image.open(A/'boardwalk.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS))
 sprites=[Image.open(C/f'{n:03d}.png').convert('RGBA').resize((348,348),Image.Resampling.LANCZOS) for n in range(24)]
 yy,xx=np.mgrid[:H,:W].astype('float32');water=np.zeros((H,W),np.uint8)
 cv2.fillPoly(water,[np.int32([(149,345),(258,345),(251,367),(149,367)])],255)
 # Exclude posts and rope, preserve recognizable structural edges.
 water[:,:145]=0;water=cv2.GaussianBlur(water.astype('float32')/255,(0,0),1)
 foreground=np.zeros((H,W),np.uint8);foreground[:,:107]=255
 # Same-distance horizontal track across the near wooden boardwalk.
 ground=645;speed=125.;start=-45;scale=348/512
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1280x720','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(R/'picture.mp4')],stdin=subprocess.PIPE)
 for f in range(FPS*SECONDS):
  t=f/FPS;dx=1.2*np.sin(yy*.27+t*3);flow=cv2.remap(bg,xx+dx.astype('float32'),yy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
  base=np.rint(bg*(1-water[:,:,None])+flow*water[:,:,None]).astype('uint8');canvas=Image.fromarray(base).convert('RGBA')
  left=round(start+speed*t);top=round(ground-480*scale)
  shadow=Image.new('RGBA',(W,H));d=ImageDraw.Draw(shadow);center=left+180*scale
  d.ellipse((center-91,ground-5,center+100,ground+7),fill=(28,20,24,65));shadow=shadow.filter(ImageFilter.GaussianBlur(5));canvas.alpha_composite(shadow)
  canvas.alpha_composite(sprites[f%24],(left,top));rgb=np.array(canvas.convert('RGB'));rgb[foreground>0]=bg[foreground>0]
  assert np.array_equal(rgb[foreground>0],bg[foreground>0])
  proc.stdin.write(rgb.tobytes())
  if f in [0,12,24,36,48,60,72,84,96,108,120,132,143]:Image.fromarray(rgb).save(R/f'proof_{f:03d}.jpg',quality=95)
 proc.stdin.close();assert proc.wait()==0
 # Quiet original wooden foot taps, synced to two support phases per stride.
 sr=48000;n=sr*SECONDS;mix=np.zeros((n,2));rng=np.random.default_rng(54)
 amb,asr=sf.read(R.parent/'luna-environment-motion-v01/environment-ambience.wav');assert asr==sr;mix+=amb[:n]*.7
 for at in np.arange(0,SECONDS,.5):
  u=np.arange(round(.10*sr))/sr;tap=(.022*rng.normal(0,1,len(u))+.04*np.sin(2*np.pi*210*u))*np.exp(-u*55)*(1-np.exp(-u*600))
  lo=round(at*sr);count=min(len(tap),n-lo);mix[lo:lo+count]+=tap[:count,None]
 sf.write(R/'walk-sound.wav',mix,sr,subtype='PCM_24')
 output=R/'Luna_Boardwalk_Walk_01.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'picture.mp4'),'-i',str(R/'walk-sound.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','loudnorm=I=-27:TP=-6:LRA=6','-c:a','aac','-b:a','160k','-ar','48000','-t','6','-movflags','+faststart',str(output)],check=True)
 subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-'],check=True)
 report=dict(seconds=6,fps=24,frames=144,sourceSheetCells=8,usedCells=order,keyPoseFrames=timing[:-1],cycleFrames=24,registration=registration,groundLine=ground,pixelsPerSecond=speed,foregroundOcclusionPinned=True,headMeshDeformation=False,fullAVDecodePassed=True,limitation='First illustrated walk-cycle study; six selected drawings with inferred intermediates, approximate support registration and footfall sound. Not a verified no-slip quadruped rig.',sha256=hashlib.sha256(output.read_bytes()).hexdigest())
 (R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)

if __name__=='__main__':main()
