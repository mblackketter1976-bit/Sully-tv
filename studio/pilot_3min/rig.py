"""Native local 2D raster puppet and camera, no video-model service."""
from pathlib import Path
import math
import cv2,numpy as np
ROOT=Path(__file__).parent
def ease(u):
 u=float(np.clip(u,0,1));return u*u*u*(10+u*(-15+6*u))
def pulse(t,at,length=.35):
 u=(t-at)/length
 if not 0<u<1:return 0.
 return math.sin(math.pi*u)**2
def keyed(t,points):
 if t<=points[0][0]:return points[0][1]
 for (a,x),(b,y) in zip(points,points[1:]):
  if t<=b:return x+(y-x)*ease((t-a)/(b-a))
 return points[-1][1]
class ActorRig:
 def __init__(self):
  self.bg=cv2.imread(str(ROOT/'assets/background-registered.png')).astype(np.float32)
  raw=cv2.imread(str(ROOT/'assets/actor-registered.png'),cv2.IMREAD_UNCHANGED)
  self.rgb=raw[:,:,:3].astype(np.float32);self.alpha=raw[:,:,3:4].astype(np.float32)/255
  self.h,self.w=raw.shape[:2];self.y,self.x=np.mgrid[:self.h,:self.w].astype(np.float32)
  closed=cv2.resize(cv2.imread(str(ROOT/'assets/blink.png')),(self.w,self.h))
  mask=np.zeros((self.h,self.w),np.uint8);mask[185:390,560:820]=255
  self.eyes=[(617,266),(736,296)]
  for p in self.eyes:cv2.ellipse(mask,p,(45,33),18,0,360,0,-1)
  sift=cv2.SIFT_create();ka,da=sift.detectAndCompute(self.rgb.astype(np.uint8),mask);kb,db=sift.detectAndCompute(closed,mask)
  matches=[m for m,n in cv2.BFMatcher().knnMatch(db,da,k=2) if m.distance<.72*n.distance]
  M,ins=cv2.estimateAffinePartial2D(np.float32([kb[m.queryIdx].pt for m in matches]),np.float32([ka[m.trainIdx].pt for m in matches]),method=cv2.RANSAC,ransacReprojThreshold=2.5)
  assert M is not None and ins.sum()>8
  self.closed=cv2.warpAffine(closed,M,(self.w,self.h)).astype(np.float32)
  self.eye_mask=np.zeros((self.h,self.w),np.uint8);self.gaze=np.zeros((self.h,self.w),np.float32)
  for cx,cy in self.eyes:
   cv2.ellipse(self.eye_mask,(cx,cy),(34,23),18,0,360,255,-1)
   r=((self.x-cx)/24)**2+((self.y-cy)/19)**2;self.gaze=np.maximum(self.gaze,np.clip(1-r,0,1)**2)
  self.eye_mask=cv2.GaussianBlur(self.eye_mask,(0,0),3).astype(np.float32)/255
  head=np.zeros((self.h,self.w),np.uint8)
  cv2.fillPoly(head,[np.array([(551,293),(554,168),(574,60),(608,58),(674,157),(725,168),(855,124),(890,137),(855,230),(819,271),(813,321),(786,354),(753,384),(686,390),(619,371),(577,334)])],255)
  self.head=cv2.GaussianBlur(head,(0,0),12).astype(np.float32)/255
  self.chest=np.exp(-((self.x-666)/115)**4-((self.y-446)/75)**4).astype(np.float32)*np.clip((548-self.y)/55,0,1)
  self.feet=[(489,578,452,0),(633,592,440,.3),(693,570,515,.6),(777,583,440,.9)]
  self.foot_masks=[]
  for fx,fy,hip,phase in self.feet:
   width=34 if fx==693 else 62
   horizontal=np.clip((width-np.abs(self.x-fx))/18,0,1)
   vertical=np.clip((self.y-hip)/(fy-hip-15),0,1);vertical=vertical*vertical*(3-2*vertical)
   self.foot_masks.append((horizontal*vertical).astype(np.float32))
  total=np.maximum(1,sum(self.foot_masks))
  self.foot_masks=[m/total for m in self.foot_masks]
 def root_x(self,t):return 125*(1-ease(t/5))
 def frame(self,t,*,walk=False,tilt=0,gaze=(0,0),blink=0,ear=0,paw=0):
  x,y=self.x,self.y
  rgb=self.rgb
  if abs(gaze[0])+abs(gaze[1])>1e-8:
   rgb=cv2.remap(rgb,x-gaze[0]*self.gaze,y-gaze[1]*self.gaze,cv2.INTER_CUBIC)
  if blink>0:rgb=rgb*(1-self.eye_mask[...,None]*blink)+self.closed*(self.eye_mask[...,None]*blink)
  layer=np.concatenate([rgb*self.alpha,self.alpha],axis=2)
  rad=math.radians(-tilt);c,s=math.cos(rad),math.sin(rad);dx=x-697;dy=y-373
  mx=x+(697+c*dx-s*dy-x)*self.head
  my=y+(373+s*dx+c*dy-y)*self.head
  breath=.5-.5*math.cos(2*math.pi*t/3.4)
  mx+=.5*(x-666)/130*breath*self.chest;my+=1.15*breath*self.chest
  if ear:
   for cx,cy,gain in [(600,130,.45),(839,176,1)]:
    weight=np.exp(-((x-cx)/48)**4-((y-cy)/74)**4).astype(np.float32)
    mx+=ear*gain*.9*weight;my-=abs(ear)*gain*.28*weight
  rootx=self.root_x(t) if walk else 0
  bob=-1.8*math.sin(math.pi*t/1.2)**2*(1-ease((t-5)/1)) if walk else 0
  targets=[]
  for index,((fx,fy,hip,phase),weight) in enumerate(zip(self.feet,self.foot_masks)):
   ox,oy=0.,0.
   if walk:
    period=1.2;swing=.30;step=math.floor((t-phase)/period)*period+phase
    if step<0:world=self.root_x(0)
    else:
     previous=self.root_x(max(0,step-period+swing));landing=self.root_x(step+swing);u=(t-step)/swing
     if 0<u<1:world=previous+(landing-previous)*ease(u);oy=-12*math.sin(math.pi*u)**2
     else:world=landing
    ox=world-rootx;oy-=bob
   if index==1:oy-=paw*8
   mx-=ox*weight;my-=oy*weight;targets.append((fx+rootx+ox,fy+bob+oy))
  deformed=cv2.remap(layer,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT)
  if rootx or bob:deformed=cv2.warpAffine(deformed,np.float32([[1,0,rootx],[0,1,bob]]),(self.w,self.h),flags=cv2.INTER_LINEAR)
  a=np.clip(deformed[:,:,3:4],0,1)
  shadows=np.zeros((self.h,self.w),np.float32)
  for fx,fy in targets:
   shadow=np.exp(-((x-fx)/27)**2-((y-599)/5.5)**2)*.17;shadows=np.maximum(shadows,shadow)
  bg=self.bg*(1-shadows[:,:,None]);out=deformed[:,:,:3]+bg*(1-a)
  return np.clip(out,0,255).astype(np.uint8)

def camera(image,zoom=1,cx=640,cy=360):
 return cv2.warpAffine(image,np.float32([[zoom,0,640-zoom*cx],[0,zoom,360-zoom*cy]]),(1280,720),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
