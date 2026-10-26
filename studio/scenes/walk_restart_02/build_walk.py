"""Fixed-shape artwork, independent articulated legs and exact stance foot locks.

Animation timing informed by Catavitello et al. 2015 dog motion data.
This is a 2D cutout/IK proof, not a learned image-interpolation gait.
"""
import os
os.environ['ORT_DISABLE_TELEMETRY']='1'
import json,math,hashlib,subprocess,zipfile
from pathlib import Path
from io import BytesIO
import numpy as np,cv2,soundfile as sf
from scipy.io import loadmat
from PIL import Image,ImageDraw,ImageFilter
import onnxruntime as ort
ort.disable_telemetry_events()
R=Path(__file__).parent;A=R/'assets';A.mkdir(exist_ok=True)
SW,SH=768,512;FPS=24;PERIOD=.9;STRIDE=140.;SECS=4
op=ort.SessionOptions();op.intra_op_num_threads=2;op.inter_op_num_threads=1
model=R.parent/'luna-finished-scene-10s-v01/models/u2netp.onnx'
assert hashlib.sha256(model.read_bytes()).hexdigest()=='309c8469258dda742793dce0ebea8e6dd393174f89934733ecc8b14c76f4ddd8'
session=ort.InferenceSession(str(model),sess_options=op,providers=['CPUExecutionProvider'])

def matting(rgb):
 small=cv2.resize(rgb,(320,320)).astype('float32')/255
 tensor=(small-np.array([.485,.456,.406],np.float32))/np.array([.229,.224,.225],np.float32)
 v=session.run(None,{session.get_inputs()[0].name:tensor.transpose(2,0,1)[None]})[0][0,0]
 v=(v-v.min())/max(.0001,float(v.max()-v.min()));alpha=np.clip((cv2.resize(v,(SW,SH),interpolation=cv2.INTER_CUBIC)-.03)/.94,0,1)
 n,labels,stats,_=cv2.connectedComponentsWithStats((alpha>.15).astype('uint8'));idx=1+int(np.argmax(stats[1:,cv2.CC_STAT_AREA]));alpha*=cv2.dilate((labels==idx).astype('uint8'),np.ones((3,3),np.uint8))
 color=np.clip((rgb.astype(float)-(1-alpha[:,:,None])*255)/np.maximum(.001,alpha[:,:,None]),0,255)
 return np.dstack([color,np.rint(alpha*255)]).astype('uint8')

def mask_polygon(poly):
 mask=np.zeros((SH,SW),np.uint8);cv2.fillPoly(mask,[np.array(poly,np.int32)],255);return mask.astype(float)/255

def asset_layers():
 rgb=np.array(Image.open(A/'standing-source.png').convert('RGB').resize((SW,SH),Image.Resampling.LANCZOS));source=matting(rgb)
 clean=np.array(Image.open(A/'body-source.png').convert('RGB').resize((SW,SH),Image.Resampling.LANCZOS))
 sift=cv2.SIFT_create(nfeatures=2000);k0,d0=sift.detectAndCompute(rgb,None);k1,d1=sift.detectAndCompute(clean,None)
 good=[a for a,b in cv2.BFMatcher().knnMatch(d1,d0,k=2) if a.distance<.72*b.distance]
 M,inside=cv2.estimateAffinePartial2D(np.float32([k1[x.queryIdx].pt for x in good]),np.float32([k0[x.trainIdx].pt for x in good]),method=cv2.RANSAC,ransacReprojThreshold=1.5)
 assert int(inside.sum())>100
 clean=cv2.warpAffine(clean,M,(SW,SH),borderValue=(255,255,255))
 # Keep original head, ears, neck, back and bag RGB. Use clean plate only where
 # removed limbs revealed previously concealed belly/chest.
 blend=np.zeros((SH,SW),np.float32);blend[295:]=1;blend=cv2.GaussianBlur(blend,(0,0),5)
 clean=np.rint(rgb*(1-blend[:,:,None])+clean*blend[:,:,None]).astype('uint8')
 body=matting(clean)
 forepoly=[(393,317),(445,307),(467,327),(469,358),(462,400),(468,446),(488,459),(491,478),(472,488),(432,489),(412,479),(405,452),(400,418),(395,384),(390,346)]
 hindpoly=[(146,337),(216,331),(229,345),(208,366),(181,385),(169,415),(166,445),(181,451),(185,467),(169,480),(126,482),(110,470),(111,450),(118,422),(119,397),(130,376),(140,352)]
 defs={'fore':dict(poly=forepoly,root=[430,327],joint=[418,388],wrist=[438,452],contact=[447,486],cuts=[385,447]),
       'hind':dict(poly=hindpoly,root=[175,342],joint=[155,394],wrist=[143,449],contact=[145,480],cuts=[393,447])}
 pieces={}
 yy=np.arange(SH)[:,None]
 for name,d in defs.items():
  alpha=source[:,:,3].astype(float)/255*mask_polygon(d['poly'])
  # Feather the concealed top attachment, retaining original fur everywhere else.
  top=317 if name=='fore' else 337;alpha*=np.clip((yy-top)/7,0,1)
  cuts=d['cuts'];parts=[]
  for n,window in enumerate([yy<cuts[0]+11,(yy>cuts[0]-11)&(yy<cuts[1]+3),yy>cuts[1]-10]):
   im=source.copy();im[:,:,3]=np.rint(alpha*window*255).astype('uint8');parts.append(im);Image.fromarray(im).save(A/f'{name}-{n}.png')
  d['contact'][1]=int(np.where(parts[2][:,:,3]>200)[0].max())
  pieces[name]=parts
 Image.fromarray(body).save(A/'body-layer.png')
 return body,pieces,defs,dict(inliers=int(inside.sum()),matrix=M.tolist())

def ik(root,target,l1,l2,sign):
 delta=target-root;distance=float(np.linalg.norm(delta));assert distance<l1+l2-.001,('unreachable',distance,l1+l2)
 assert distance>abs(l1-l2)+.001
 u=delta/distance;a=(l1*l1-l2*l2+distance*distance)/(2*distance)
 h=math.sqrt(max(0,l1*l1-a*a));return root+u*a+sign*np.array([-u[1],u[0]])*h

def foot(t,offset,duty,height,center,ground):
 phase=t/PERIOD-offset;k=math.floor(phase);q=phase-k;half=STRIDE*duty/2
 if q<duty:
  rel=half-STRIDE*q;lift=0.;angle=0.;stance=True
 else:
  u=(q-duty)/(1-duty);m=-STRIDE*(1-duty)
  rel=(2*u**3-3*u**2+1)*(-half)+(u**3-2*u*u+u)*m+(-2*u**3+3*u*u)*half+(u**3-u*u)*m
  lift=height*math.sin(math.pi*u)**2;angle=-12*math.sin(math.pi*u)**2;stance=False
 return np.array([center+rel,ground-lift]),angle,stance,k

def warp_rigid(image,src_origin,src_tip,dst_origin,dst_tip):
 a=np.array(src_tip)-src_origin;b=np.array(dst_tip)-dst_origin
 theta=math.atan2(b[1],b[0])-math.atan2(a[1],a[0]);c,s=math.cos(theta),math.sin(theta)
 rot=np.array([[c,-s],[s,c]],np.float32);translation=dst_origin-rot@src_origin
 matrix=np.column_stack([rot,translation]).astype('float32')
 # Warp premultiplied color, avoiding the old white-background edge halo.
 aa=image[:,:,3].astype('float32')/255;pre=image[:,:,:3].astype('float32')*aa[:,:,None]
 wa=cv2.warpAffine(aa,matrix,(SW,SH),flags=cv2.INTER_LINEAR);wp=cv2.warpAffine(pre,matrix,(SW,SH),flags=cv2.INTER_LINEAR)
 return np.dstack([np.clip(wp/np.maximum(.001,wa[:,:,None]),0,255),np.clip(wa*255,0,255)]).astype('uint8')

def main():
 body,pieces,defs,reg=asset_layers()
 # Measured DogS second walking stride: hind touchdown 39, fore 45,
 # next hind 81, fore 84, at 60fps. Retarget timing, not body proportions.
 with zipfile.ZipFile(R/'canine-reference-data.zip') as z:data=loadmat(BytesIO(z.read('S1_DataSet/Dogs Data/DogS.mat')),simplify_cells=True)['dogdata']['walking']
 hcp=data['hindlimb']['cp'][1];fcp=data['forelimb']['cp'][1]
 fore_offset=float((fcp[0]-hcp[0])/(hcp[2]-hcp[0]));hind_duty=float((hcp[1]-hcp[0])/(hcp[2]-hcp[0]));fore_duty=float((fcp[1]-fcp[0])/(fcp[2]-fcp[0]))
 # Source illustration far legs attach slightly farther right and higher.
 legs=[('far-hind','hind',.5,hind_duty,40,-14,True),('far-fore','fore',fore_offset+.5,fore_duty,38,-14,True),('near-hind','hind',0,hind_duty,0,0,False),('near-fore','fore',fore_offset,fore_duty,0,0,False)]
 locks={};positions=[];max_bone_error=0.;min_support=4
 def character(t,check=True):
  nonlocal max_bone_error,min_support
  canvas=Image.new('RGBA',(SW,SH));bob=10+1.0*(1-math.cos(4*math.pi*t/PERIOD))
  pitch=math.radians(.65)*math.sin(2*math.pi*t/PERIOD+.25)
  rot=np.array([[math.cos(pitch),-math.sin(pitch)],[math.sin(pitch),math.cos(pitch)]])
  pivot=np.array([325.,320.])
  moved_body=warp_rigid(body,pivot,pivot+[1,0],pivot+[0,bob],pivot+[0,bob]+rot@[1.,0.])
  roots={};support=0
  for name,kind,offset,duty,xshift,yshift,far in legs:
   d=defs[kind];root0=np.array(d['root'],float);joint0=np.array(d['joint'],float);wrist0=np.array(d['wrist'],float);contact0=np.array(d['contact'],float)
   root=rot@(root0+[xshift,yshift]-pivot)+pivot+[0,bob];ground=480+yshift;center=root0[0]+xshift+(contact0[0]-wrist0[0])
   target,angle,stance,cycle=foot(t,offset,duty,23 if kind=='fore' else 20,center,ground)
   rad=math.radians(angle);rotation=np.array([[math.cos(rad),-math.sin(rad)],[math.sin(rad),math.cos(rad)]])
   wrist=target-rotation@(contact0-wrist0)
   l1=np.linalg.norm(joint0-root0);l2=np.linalg.norm(wrist0-joint0);joint=ik(root,wrist,l1,l2,1 if kind=='fore' else -1)
   max_bone_error=max(max_bone_error,abs(np.linalg.norm(joint-root)-l1),abs(np.linalg.norm(wrist-joint)-l2))
   if stance:
    support+=1;world=target+[STRIDE*t/PERIOD,0];key=(name,cycle)
    if key in locks:assert np.linalg.norm(world-locks[key])<1e-6
    else:locks[key]=world
   if check:positions.append(dict(t=t,leg=name,stance=stance,paw=target.tolist(),wrist=wrist.tolist(),joint=joint.tolist(),root=root.tolist(),worldPaw=(target+[STRIDE*t/PERIOD,0]).tolist()))
   rendered=[]
   for part,src0,src1,dst0,dst1 in [(0,root0,joint0,root,joint),(1,joint0,wrist0,joint,wrist),(2,wrist0,contact0,wrist,target)]:
    layer=warp_rigid(pieces[kind][part],src0,src1,dst0,dst1)
    if far:layer[:,:,:3]=np.rint(layer[:,:,:3].astype(float)*.88).astype('uint8')
    rendered.append(Image.fromarray(layer))
   # Paw/lower/upper overlap, with the proximal fur covering the joint seam.
   for layer in reversed(rendered):canvas.alpha_composite(layer)
   if name=='far-fore':canvas.alpha_composite(Image.fromarray(moved_body))
  min_support=min(min_support,support);assert support>=2
  return canvas
 if '--proofs' in __import__('sys').argv:
  for n in range(24):
   t=n*PERIOD/24;im=Image.new('RGBA',(SW,SH),(90,100,112,255));im.alpha_composite(character(t));im.convert('RGB').save(R/f'cycle_{n:02d}.jpg',quality=95)
  print('PROOF_OK',max_bone_error,min_support);return
 bg=Image.open(R.parent/'luna-walk-v01/assets/boardwalk.png').convert('RGB').resize((1280,720),Image.Resampling.LANCZOS)
 proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size','1280x720','-framerate','24','-i','pipe:0','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(R/'picture.mp4')],stdin=subprocess.PIPE)
 scale=.72;size=(round(SW*scale),round(SH*scale));ground=645;origin_y=round(ground-480*scale)
 for n in range(FPS*SECS):
  t=n/FPS;actor=character(t).resize(size,Image.Resampling.LANCZOS);left=round(10+STRIDE*t/PERIOD*scale)
  canvas=bg.convert('RGBA');shadow=Image.new('RGBA',canvas.size);draw=ImageDraw.Draw(shadow)
  draw.ellipse((left+105*scale,ground-5,left+480*scale,ground+7),fill=(15,18,27,66));shadow=shadow.filter(ImageFilter.GaussianBlur(5));canvas.alpha_composite(shadow)
  canvas.alpha_composite(actor,(left,origin_y));rgb=np.array(canvas.convert('RGB'));rgb[:,:107]=np.array(bg)[:,:107]
  proc.stdin.write(rgb.tobytes())
  if n in [0,6,12,18,24,30,36,42,48,60,72,84,95]:Image.fromarray(rgb).save(R/f'proof_{n:03d}.jpg',quality=95)
 proc.stdin.close();assert proc.wait()==0
 sr=48000;mix=np.zeros((SECS*sr,2));amb,asr=sf.read(R.parent/'luna-environment-motion-v01/environment-ambience.wav');assert asr==sr;mix+=amb[:len(mix)]*.6;rng=np.random.default_rng(73)
 for _,kind,offset,duty,xs,ys,far in legs:
  for k in range(-1,7):
   at=(k+offset)*PERIOD
   if not 0<=at<SECS:continue
   u=np.arange(round(.065*sr))/sr;sound=(.018*rng.normal(0,1,len(u))+.026*np.sin(2*np.pi*190*u))*np.exp(-u*75)*(1-np.exp(-u*700));lo=round(at*sr);count=min(len(sound),len(mix)-lo);mix[lo:lo+count]+=sound[:count,None]*(.7 if far else 1)
 sf.write(R/'walk-audio.wav',mix,sr,subtype='PCM_24');out=R/'Luna_Walk_Rebuilt_02.mp4'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(R/'picture.mp4'),'-i',str(R/'walk-audio.wav'),'-c:v','copy','-af','loudnorm=I=-27:TP=-6:LRA=6','-c:a','aac','-b:a','160k','-ar','48000','-t',str(SECS),'-movflags','+faststart',str(out)],check=True)
 subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True)
 (R/'joint-traces.json').write_text(json.dumps(positions))
 report=dict(seconds=SECS,frames=SECS*FPS,fps=FPS,method='Single fixed-shape body; independently articulated raster limbs; exact stance locks; no RIFE or image morphing',reference='Catavitello et al. 2015, doi:10.1371/journal.pone.0133936, CC BY, DogS walking second stride contact timing',forePhase=fore_offset,hindDuty=hind_duty,foreDuty=fore_duty,period=PERIOD,stride=STRIDE,bodyPlateRegistration=reg,maxBoneLengthError=max_bone_error,minSupportingFeet=min_support,stanceFootWorldPositionsConstant=True,fullAVDecodePassed=True,sha256=hashlib.sha256(out.read_bytes()).hexdigest())
 (R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)

if __name__=='__main__':main()
