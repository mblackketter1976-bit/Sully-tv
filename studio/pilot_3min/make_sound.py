"""Original procedural score/foley and locally synthesized narrator mix."""
import json,math,textwrap
from pathlib import Path
import numpy as np
import soundfile as sf
ROOT=Path(__file__).parent;SR=24000;DURATION=180;N=SR*DURATION
rng=np.random.default_rng(20261026);mix=np.zeros((N,2),np.float32);narr=np.zeros(N,np.float32)
timing=json.loads((ROOT/'audio/narration-timing.json').read_text());story=json.loads((ROOT/'story.json').read_text())
def add(signal,at,level=1,pan=0):
 i=round(at*SR);n=min(len(signal),N-i)
 if n<=0:return
 gains=np.sqrt(np.array([(1-pan)/2,(1+pan)/2],np.float32));mix[i:i+n]+=signal[:n,None]*level*gains
def tone(freq,seconds,kind='bell'):
 t=np.arange(round(seconds*SR),dtype=np.float32)/SR
 if kind=='bell':return (.65*np.sin(2*np.pi*freq*t)*np.exp(-t*2)+.22*np.sin(2*np.pi*freq*2.01*t)*np.exp(-t*4)+.10*np.sin(2*np.pi*freq*3.97*t)*np.exp(-t*7)).astype(np.float32)
 return (np.sin(2*np.pi*freq*t)*np.exp(-t*5)*(1-np.exp(-t*70))).astype(np.float32)
# Quiet river/air bed; smoothly filtered original noise, no sampled recordings.
noise=rng.normal(0,1,N).astype(np.float32)
air=np.convolve(noise,np.ones(65,dtype=np.float32)/65,mode='same');air/=max(1,np.max(np.abs(air)))
add(air,0,.023,-.35);add(np.roll(air,13000),0,.020,.4)
# Original celesta motif with three changing registers/sections.
notes=[392,493.883,587.33,659.255,587.33,493.883,440,392]
for beat,at in enumerate(np.arange(2,178,2.35)):
 freq=notes[beat%len(notes)]
 if 65<at<155:freq*=.5
 level=.031 if at<65 else .022
 add(tone(freq,2.8),float(at),level,.35*math.sin(beat))
 if beat%4==0:
  for f in [196,246.942,293.665]:add(tone(f,4,'pluck'),float(at),.012,-.2)
# Footstep clacks, metal taps, distant bell and latch are synthesized here.
events=[]
def click(at,metal=False,pan=0,level=.09):
 dur=.12 if not metal else .42;t=np.arange(round(dur*SR))/SR
 signal=rng.normal(0,1,len(t))*np.exp(-t*(65 if not metal else 32))*.35
 signal+=np.sin(2*np.pi*(1450 if metal else 145)*t)*np.exp(-t*(14 if metal else 48))*.5
 add(signal.astype(np.float32),at,level,pan);events.append({'type':'metal tap' if metal else 'paw/wood contact','time':at})
for at in [20,20.3,20.6,20.9,21.2,21.5,21.8,22.1,22.4,22.7,23,23.3,48.6,126.6]:click(at,False,.2,.08)
for start in [65.7,68.0]:
 for delta in [0,.24,.48]:click(start+delta,True,.2,.11)
for at in [112.4,168.0]:
 click(at,True,.1,.12);add(tone(1174.66,1.8),at,.045,.2)
add(tone(523.25,5),4,.045,-.7);add(tone(698.456,4),174.4,.06,.35)
click(173.8,True,.4,.12)
# Speech is mixed above a ducked score, without modifying character voices.
for item in timing:
 x,sr=sf.read(ROOT/'audio'/item['file']);assert sr==SR
 i=round(item['start']*SR);n=len(x);narr[i:i+n]+=x.astype(np.float32)*1.7
duck=np.ones(N,np.float32)
for item in timing:
 a=max(0,round((item['start']-.15)*SR));b=min(N,round((item['start']+item['seconds']+.3)*SR));duck[a:b]=.52
mix*=duck[:,None];mix+=narr[:,None]*.7071
fade=np.minimum(np.minimum(np.arange(N)/SR/1.2,(N-np.arange(N))/SR/1.4),1).astype(np.float32);mix*=np.maximum(fade,0)[:,None]
peak=float(np.max(np.abs(mix)));mix*=min(1,.89/max(peak,1e-9));sf.write(ROOT/'audio/mix.wav',mix,SR,subtype='PCM_16')
report={'seconds':DURATION,'sampleRate':SR,'channels':2,'peakBeforeGain':peak,'peakAfterGain':float(np.max(np.abs(mix))),'narrationSegments':len(timing),'soundEvents':events,'source':'Original procedural score/foley plus locally synthesized narrator. No source-clip audio or motion.'}
(ROOT/'audio/sound-verification.json').write_text(json.dumps(report,indent=2))
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
subs=[]
for item in timing:
 words=item['text'].split();groups=[words[i:i+12] for i in range(0,len(words),12)];done=0
 for group in groups:
  start=item['start']+item['seconds']*done/len(words);done+=len(group);stop=item['start']+item['seconds']*done/len(words)
  subs.append((start,stop,textwrap.fill(' '.join(group),width=48)))
(ROOT/'captions.srt').write_text(''.join(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{s}\n\n' for i,(a,b,s) in enumerate(subs)))
print('SOUND_READY',json.dumps(report),flush=True)
