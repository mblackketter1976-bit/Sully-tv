"""Stream authored PNG cels through an exposure sheet into a local video.
No image generation, morphing, or automatic in-betweening is performed here.
Drawing/timing decisions remain explicit and reviewable.
"""
import argparse,bisect,collections,hashlib,json,subprocess
from pathlib import Path
from PIL import Image

class CelScene:
 def __init__(self,path):
  self.path=Path(path).resolve();self.root=self.path.parent
  self.spec=json.loads(self.path.read_text());s=self.spec
  assert s.get('schema')==1,'Unsupported sheet schema'
  self.width,self.height=map(int,s['size']);self.fps=int(s['fps']);self.frames=int(s['frames'])
  assert 1<=self.width<=8192 and 1<=self.height<=8192
  assert 1<=self.fps<=120 and self.frames>0
  self.cels={};self.cache=collections.OrderedDict();self.layers=[]
  for name,value in s['cels'].items():
   p=(self.root/value).resolve();assert p.is_relative_to(self.root),'Cel paths must stay within the project'
   assert p.is_file(),f'Missing cel: {name}'
   with Image.open(p) as im:im.verify()
   self.cels[name]=p
  for layer in s['layers']:
   exposures=sorted(layer['exposures'],key=lambda e:e['start']);end=0
   for e in exposures:
    assert isinstance(e['start'],int) and isinstance(e['stop'],int)
    assert 0<=e['start']<e['stop']<=self.frames,'Exposure outside timeline'
    assert e['start']>=end,'Overlapping exposures on one layer'
    assert e['cel'] in self.cels,f'Unknown cel {e["cel"]}'
    position=e.get('position',layer.get('position',[0,0]));assert len(position)==2 and all(isinstance(x,int) for x in position)
    end=e['stop']
   self.layers.append((layer,exposures,[e['start'] for e in exposures]))
  assert self.layers,'No drawing layers'
 def image(self,name):
  if name not in self.cache:
   with Image.open(self.cels[name]) as im:self.cache[name]=im.convert('RGBA')
   if len(self.cache)>16:self.cache.popitem(last=False)
  self.cache.move_to_end(name);return self.cache[name]
 def stack(self,frame):
  assert 0<=frame<self.frames
  result=[]
  for layer,exposures,starts in self.layers:
   i=bisect.bisect_right(starts,frame)-1
   if i>=0:
    e=exposures[i]
    if frame<e['stop']:result.append((e['cel'],tuple(e.get('position',layer.get('position',[0,0])))))
  return result
 def frame(self,number):
  out=Image.new('RGBA',(self.width,self.height),tuple(self.spec.get('background',[0,0,0,255])))
  for name,position in self.stack(number):out.alpha_composite(self.image(name),position)
  return out
 def report(self):
  used={e['cel'] for _,es,_ in self.layers for e in es}
  return {'schema':1,'size':[self.width,self.height],'fps':self.fps,'frames':self.frames,'seconds':self.frames/self.fps,
   'uniqueCelsUsed':len(used),'exposures':sum(len(es) for _,es,_ in self.layers),
   'sourceHashes':{n:hashlib.sha256(self.cels[n].read_bytes()).hexdigest() for n in sorted(used)},
   'method':'Authored PNG cels on explicit exposure sheets; no automatic image warping or in-between generation.'}

def render(scene,output,frames_dir=None):
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 assert scene.width%2==scene.height%2==0,'H.264 output dimensions must be even'
 if frames_dir:frames_dir=Path(frames_dir);frames_dir.mkdir(parents=True,exist_ok=True)
 command=['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{scene.width}x{scene.height}','-framerate',str(scene.fps),'-i','pipe:0']
 if scene.spec.get('audio'):
  audio=(scene.root/scene.spec['audio']).resolve();assert audio.is_relative_to(scene.root) and audio.is_file()
  command+=['-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','160k']
 else:command+=['-an']
 command+=['-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-t',str(scene.frames/scene.fps),'-movflags','+faststart',str(output)]
 process=subprocess.Popen(command,stdin=subprocess.PIPE);last_stack=None;pixels=None
 try:
  for number in range(scene.frames):
   stack=scene.stack(number)
   if stack!=last_stack:
    frame=scene.frame(number);pixels=frame.convert('RGB').tobytes();last_stack=stack
   process.stdin.write(pixels)
   if frames_dir:
    if stack!=scene.stack(max(0,number-1)) or number==0:frame=scene.frame(number)
    frame.save(frames_dir/f'frame_{number:06d}.png')
 finally:process.stdin.close()
 assert process.wait()==0,'FFmpeg render failed'
 report=scene.report();report['output']=output.name
 output.with_suffix('.verification.json').write_text(json.dumps(report,indent=2));return report

def onion(scene,frame,output):
 # Previous/red and next/blue pixel differences over the current frame.
 out=scene.frame(frame)
 for at,color in [(frame-1,(235,70,75)),(frame+1,(60,135,240))]:
  if not 0<=at<scene.frames:continue
  from PIL import ImageChops
  neighbor=scene.frame(at);delta=ImageChops.difference(neighbor,scene.frame(frame)).convert('L')
  delta=delta.point(lambda p:min(125,p*3))
  tint=Image.new('RGBA',out.size,(*color,0));tint.putalpha(delta);out=Image.alpha_composite(out,tint)
 out.save(output)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('sheet',type=Path)
 sub=p.add_subparsers(dest='command',required=True);sub.add_parser('validate')
 r=sub.add_parser('render');r.add_argument('--output',type=Path,required=True);r.add_argument('--frames-dir',type=Path)
 o=sub.add_parser('onion');o.add_argument('--frame',type=int,required=True);o.add_argument('--output',type=Path,required=True)
 a=p.parse_args();scene=CelScene(a.sheet)
 if a.command=='render':result=render(scene,a.output,a.frames_dir)
 elif a.command=='onion':onion(scene,a.frame,a.output);result={'onionProof':str(a.output)}
 else:result=scene.report()
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
