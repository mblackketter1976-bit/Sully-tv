"""Local 2D expression test built over the accepted acting baseline.
Requires numpy, opencv-python-headless and FFmpeg on PATH.
Inputs: approved still and separately edited closed-eye key pose.
"""
import argparse,hashlib,json,math,subprocess
from pathlib import Path
import cv2
import numpy as np

p=argparse.ArgumentParser();p.add_argument('--still',type=Path,required=True);p.add_argument('--blink',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
assert hashlib.sha256(a.still.read_bytes()).hexdigest()=='9ff00831f4ec4ba05b68a2145623335e3e8bb5d7c26814ac5a55b60dba7cb650','Requires reviewed artwork'
assert hashlib.sha256(a.blink.read_bytes()).hexdigest()=='750e7a794fc7a9bfb7bab098ad76e19a43eb382f77324991297b5c2f0abba768','Requires accepted blink key'
base=cv2.imread(str(a.still));closed=cv2.imread(str(a.blink));assert base is not None and closed is not None
h,w=base.shape[:2];assert (w,h)==(1280,720)
closed=cv2.resize(closed,(w,h),interpolation=cv2.INTER_AREA)
# Register common fur/nose features, excluding the edited eye areas.
feature_mask=np.zeros((h,w),np.uint8);feature_mask[190:390,560:810]=255
eyes=[((617,266),(34,23),18),((736,296),(34,23),18)]
for centre,radius,angle in eyes:cv2.ellipse(feature_mask,centre,(radius[0]+10,radius[1]+10),angle,0,360,0,-1)
sift=cv2.SIFT_create();ka,da=sift.detectAndCompute(base,feature_mask);kb,db=sift.detectAndCompute(closed,feature_mask)
matches=cv2.BFMatcher().knnMatch(db,da,k=2);good=[m for m,n in matches if m.distance<.72*n.distance]
assert len(good)>=6,len(good)
src=np.float32([kb[m.queryIdx].pt for m in good]);dst=np.float32([ka[m.trainIdx].pt for m in good])
matrix,inliers=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2)
assert matrix is not None and int(inliers.sum())>=6
closed=cv2.warpAffine(closed,matrix,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
eye_mask=np.zeros((h,w),np.uint8)
for centre,radius,angle in eyes:cv2.ellipse(eye_mask,centre,radius,angle,0,360,255,-1)
eye_mask=cv2.GaussianBlur(eye_mask,(0,0),3).astype(np.float32)/255
# Mesh-like deformation weights. The original raster is sampled directly.
head=np.zeros((h,w),np.uint8)
outline=np.array([(550,293),(557,227),(552,174),(560,101),(575,63),(603,61),(632,85),(670,155),(725,168),(790,139),(854,126),(884,138),(875,185),(852,226),(822,266),(813,314),(790,352),(755,380),(691,388),(624,368),(577,333)],np.int32)
cv2.fillPoly(head,[outline],255)
head=cv2.GaussianBlur(head,(0,0),13).astype(np.float32)/255
head[head<.002]=0
chest=np.zeros((h,w),np.uint8);cv2.ellipse(chest,(666,448),(139,91),-7,0,360,255,-1)
chest=cv2.GaussianBlur(chest,(0,0),18).astype(np.float32)/255
yy,xx=np.mgrid[:h,:w].astype(np.float32)
# Compact interior eye weights leave the surrounding fur/lids untouched.
gaze_weight=np.zeros((h,w),np.float32)
for cx,cy,rx,ry in [(619,265,24,19),(736,296,24,19)]:
 radius=((xx-cx)/rx)**2+((yy-cy)/ry)**2
 gaze_weight=np.maximum(gaze_weight,np.clip(1-radius,0,1)**2)
ear_weights=[]
for polygon,pivot,gain in [
 ([(555,174),(561,103),(575,62),(603,60),(635,89),(665,157),(646,192),(599,215)],(622,207),.42),
 ([(772,182),(809,147),(855,124),(884,135),(875,183),(855,218),(814,244),(785,222)],(804,235),1.0)]:
 mask=np.zeros((h,w),np.uint8);cv2.fillPoly(mask,[np.array(polygon,np.int32)],255)
 mask=cv2.GaussianBlur(mask,(0,0),5).astype(np.float32)/255;mask[mask<.002]=0
 ear_weights.append((mask,pivot,gain))
# Exact pins: boots, floor, paws, storefront lettering and bridge.
chest*=np.clip((550-yy)/45,0,1);chest[chest<.002]=0
allowed=np.zeros((h,w),bool);allowed[28:552,425:925]=True
head*=allowed;chest*=allowed
for cx,cy,rx,ry in [(490,579,42,27),(635,592,49,35),(777,583,45,28),(695,570,35,28)]:
 pin=((xx-cx)/rx)**2+((yy-cy)/ry)**2<1.6
 head[pin]=0;chest[pin]=0
def ease(u):
 u=max(0,min(1,u));return u*u*u*(10+u*(-15+6*u))
beats=[(0,0),(.7,0),(2.2,-2.5),(3.1,-2.5),(4.6,2.3),(5.6,2.3),(7.1,0),(8,0)]
def tilt(t):
 for (t0,v0),(t1,v1) in zip(beats,beats[1:]):
  if t<=t1:return v0+(v1-v0)*ease((t-t0)/(t1-t0))
 return 0
def blink(t):
 closure=0
 for at in [1.65,6.35]:
  u=t-at
  if 0<=u<.12:value=ease(u/.12)
  elif .12<=u<.20:value=1
  elif .20<=u<.37:value=1-ease((u-.20)/.17)
  else:value=0
  closure=max(closure,value)
 return closure
def glance(t):
 if t<2.05:return (0.,0.)
 if t<2.5:amount=ease((t-2.05)/.45)
 elif t<3.55:amount=1.
 elif t<4.1:amount=1-ease((t-3.55)/.55)
 else:amount=0.
 return (-2.6*amount,3.2*amount)
def ear_reaction(t):
 # Small, asymmetric perk-and-release, never a detached rotating sticker.
 if not 3.45<t<4.25:return 0.
 u=(t-3.45)/.8
 return 3.1*math.sin(math.pi*u)**2*math.cos(math.pi*u*.8)
fps=24;frames=192
proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','bgr24','-video_size',f'{w}x{h}','-framerate',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output)],stdin=subprocess.PIPE)
base_float=base.astype(np.float32);closed_float=closed.astype(np.float32)
outside=~allowed;max_background_error=0;max_pin_error=0;checks=[]
pins=(yy>=553)|((xx<300)&(yy>390))
for i in range(frames):
 t=i/fps;angle=math.radians(tilt(t));c=math.cos(-angle);s=math.sin(-angle)
 dx=xx-697;dy=yy-373
 mapped_x=697+c*dx-s*dy;mapped_y=373+s*dx+c*dy
 breath=.5-.5*math.cos(2*math.pi*t/3.3)
 map_x=xx+(mapped_x-xx)*head+.65*(xx-666)/139*breath*chest
 map_y=yy+(mapped_y-yy)*head+1.35*breath*chest
 ear_angle=ear_reaction(t)
 for weight,(px,py),gain in (ear_weights if abs(ear_angle)>1e-10 else []):
  local_weight=cv2.remap(weight,map_x,map_y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
  theta=math.radians(-ear_angle*gain);ec=math.cos(theta);es=math.sin(theta)
  ex=map_x-px;ey=map_y-py
  ear_x=px+ec*ex-es*ey;ear_y=py+es*ex+ec*ey
  map_x=map_x+(ear_x-map_x)*local_weight;map_y=map_y+(ear_y-map_y)*local_weight
 closure=blink(t);alpha=eye_mask*closure
 gx,gy=glance(t)
 looking=cv2.remap(base,xx-gx*gaze_weight,yy-gy*gaze_weight,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT).astype(np.float32) if abs(gx)+abs(gy)>1e-10 else base_float
 pose=looking*(1-alpha[...,None])+closed_float*alpha[...,None]
 pose=np.clip(np.rint(pose),0,255).astype(np.uint8)
 frame=cv2.remap(pose,map_x,map_y,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
 # Enforce stationary pixels outside the performance area, including feet.
 frame[outside|pins]=base[outside|pins]
 max_background_error=max(max_background_error,int(np.max(np.abs(frame[outside].astype(np.int16)-base[outside].astype(np.int16)))))
 max_pin_error=max(max_pin_error,int(np.max(np.abs(frame[pins].astype(np.int16)-base[pins].astype(np.int16)))))
 proc.stdin.write(frame.tobytes())
 if i in [0,42,45,60,70,83,89,96,111,156,160,191]:
  cv2.imwrite(str(a.output.parent/f'review_{i:03d}.png'),frame);checks.append({'frame':i,'tiltDegrees':tilt(t),'blinkClosure':closure,'gazePixels':[gx,gy],'earDegrees':ear_angle})
 if i%48==0:print('2D_FRAME',i,flush=True)
proc.stdin.close();assert proc.wait()==0
report={'method':'Accepted local 2D acting plus a small glance and asymmetric ear reaction. Uses the original artwork and accepted blink key; no source-video motion, Runway service or new image-generation call.','sourceStillSHA256':hashlib.sha256(a.still.read_bytes()).hexdigest(),'closedEyeSHA256':hashlib.sha256(a.blink.read_bytes()).hexdigest(),'fps':fps,'frames':frames,'seconds':frames/fps,'backgroundMaxRawPixelDifference':max_background_error,'pinnedPawsMaxRawPixelDifference':max_pin_error,'eyeAlignmentInliers':int(inliers.sum()),'poseChecks':checks,'limits':'Limited 2D acting/deformation study. No walking, full head turn, new dialogue or complete reusable rig. Nearby detail inside feathered movement boundaries may deform; inspect before expanding.'}
a.output.with_suffix('.verification.json').write_text(json.dumps(report,indent=2));assert max_background_error==max_pin_error==0
print('LUNA_2D_PASS',json.dumps(report),flush=True)
