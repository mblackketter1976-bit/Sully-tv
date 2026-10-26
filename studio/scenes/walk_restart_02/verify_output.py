"""Check encoded timing and visible planted-paw drift, not just rig targets."""
import subprocess,json,cv2
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
R=Path(__file__).parent;video=R/'Luna_Walk_Rebuilt_02.mp4'
meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(video)]))
v=next(s for s in meta['streams'] if s['codec_type']=='video');assert v['nb_read_frames']=='96' and v['r_frame_rate']=='24/1'
traces=json.loads((R/'joint-traces.json').read_text());track={};results=[];proofs={};samples=[4,8,12,16,20,24,30,36,42,48,60,72,84,95]
proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(video),'-an','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE)
for n in range(96):
 raw=proc.stdout.read(1280*720*3);assert len(raw)==1280*720*3;im=np.frombuffer(raw,np.uint8).reshape(720,1280,3)
 if n in samples:proofs[n]=im.copy()
 for d in traces[n*4:n*4+4]:
  if not d['stance'] or not d['leg'].startswith('near'):continue
  x=round(10+d['worldPaw'][0]*.72);y=round(645+(d['worldPaw'][1]-480)*.72);key=(d['leg'],round(d['worldPaw'][0],3))
  patch=im[y-17:y-2,x-15:x+15]
  if patch.shape!=(15,30,3):continue
  if key not in track:track[key]=patch.copy();continue
  area=im[y-19:y,x-17:x+17];corr=cv2.matchTemplate(area,track[key],cv2.TM_CCOEFF_NORMED);_,score,_,loc=cv2.minMaxLoc(corr)
  results.append(dict(frame=n,leg=d['leg'],pixelShift=[loc[0]-2,loc[1]-2],correlation=score))
assert proc.wait()==0
sheet=Image.new('RGB',(1280,((len(samples)+3)//4)*240),'#111')
for i,n in enumerate(samples):
 im=Image.fromarray(proofs[n]);left=round(10+140*(n/24)/.9*.72)
 crop=im.crop((max(0,left+65),285,min(1280,left+485),660)).resize((320,220));sheet.paste(crop,((i%4)*320,(i//4)*240))
 ImageDraw.Draw(sheet).text(((i%4)*320+4,(i//4)*240+222),str(n),fill='white')
sheet.save(R/'decoded-contact-sheet.jpg')
au=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vn','-f','f32le','-ac','2','-ar','48000','pipe:1']),np.float32)
assert np.isfinite(au).all() and max(abs(au))<.95
report=json.loads((R/'verification.json').read_text())
report.update(decodedFrameCount=96,decodedAudioPeak=float(max(abs(au))),actualPawPatchTracking={'comparisons':len(results),'maxAbsolutePixelShift':max(max(abs(a) for a in x['pixelShift']) for x in results),'minimumCorrelation':min(x['correlation'] for x in results)},decodedFramesInspected=samples,limitations='Short 2D articulated-cutout mechanics proof. Joint seams and stiff body/backpack remain possible; not a finished natural cartoon walk. No realtime visual playback/listening claim. Rig ground locks are exact; encoded/raster pixels can jitter slightly.')
(R/'verification.json').write_text(json.dumps(report,indent=2));(R/'paw-pixel-check.json').write_text(json.dumps(results,indent=2));print(json.dumps(report))
