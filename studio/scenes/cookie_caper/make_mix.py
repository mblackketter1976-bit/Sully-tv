"""Original synthesized music/foley plus candidate dialogue; ten-second stereo mix."""
import json,math,subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import butter,sosfilt,resample_poly
ROOT=Path(__file__).parent;SR=48000;N=10*SR;rng=np.random.default_rng(1976)
voice=np.zeros((N,2));score=np.zeros((N,2));foley=np.zeros((N,2));ambience=np.zeros((N,2));duck=np.ones(N)
def add(track,wave,start,level=1,pan=0):
 at=round(start*SR);wave=np.asarray(wave);end=min(N,at+len(wave));wave=wave[:end-at]
 gains=np.array([math.sqrt((1-pan)/2),math.sqrt((1+pan)/2)])
 track[at:end]+=wave[:,None]*gains*level

records=json.loads((ROOT/'audio/voice-candidates.json').read_text())
dialogue=[]
for line in records['lines']:
 x,sr=sf.read(ROOT/'audio'/line['file']);x=resample_poly(x,SR,sr) if sr!=SR else x
 peak=float(np.max(np.abs(x)));gain=.60/max(peak,.001)
 add(voice,x,line['start'],gain,.18 if line['character']=='The Rook' else -.12)
 lo=max(0,round((line['start']-.12)*SR));hi=min(N,round((line['start']+line['seconds']+.12)*SR));duck[lo:hi]=.35
 dialogue.append(dict(id=line['id'],start=line['start'],end=line['start']+len(x)/SR,gain=gain))

def pluck(freq,duration=.65):
 t=np.arange(round(duration*SR))/SR
 wave=sum((1/k**1.7)*np.sin(2*np.pi*freq*k*t)*np.exp(-t*(3+k*1.3)) for k in range(1,6))
 wave*=1-np.exp(-t*900)
 return wave

# Original G-major musical punctuation; intentionally sparse under dialogue.
notes=[(0,196,.055),(0.18,293.665,.035),(0.38,391.995,.025),
       (2.25,329.628,.025),(5.48,493.883,.03),(5.65,369.994,.02),
       (8.48,196,.06),(8.60,246.942,.045),(8.73,293.665,.04),
       (8.88,391.995,.045),(9.18,587.33,.025),(9.44,783.991,.025)]
for start,freq,level in notes:add(score,pluck(freq,1.0),start,level,-.15)

def rustle(start,duration,level,pan):
 n=round(duration*SR);noise=rng.normal(0,1,n)
 wave=sosfilt(butter(2,[600,4500],btype='bandpass',fs=SR,output='sos'),noise)
 wave*=np.sin(np.linspace(0,np.pi,n))**2
 add(foley,wave,start,level,pan)
rustle(.18,.42,.024,.3);rustle(1.18,.22,.018,.25);rustle(6.35,.32,.018,.25);rustle(6.83,.24,.032,.1)
for start,freq in [(1.22,783.99),(1.29,987.77),(1.36,1174.66)]:
 t=np.arange(int(.42*SR))/SR;bell=np.sin(2*np.pi*freq*t)*np.exp(-t*14)*(1-np.exp(-t*1000));add(foley,bell,start,.055,.1)
t=np.arange(int(.16*SR))/SR
tap=(np.sin(2*np.pi*380*t)*np.exp(-t*52)+.3*rng.normal(0,1,len(t))*np.exp(-t*90))*(1-np.exp(-t*2000))
add(foley,tap,7.55,.14,-.05)
# Quiet riverfront air and soft distant water texture, never an intrusive hiss.
for ch in range(2):
 noise=rng.normal(0,1,N);air=sosfilt(butter(2,[80,600],btype='bandpass',fs=SR,output='sos'),noise)
 ambience[:,ch]=air*.003
duck=np.convolve(duck,np.ones(2401)/2401,mode='same');duck[:1200]=np.linspace(.35,duck[1200],1200)
mix=voice+score*duck[:,None]+foley+ambience
fade=np.minimum(1,np.arange(N)/(.03*SR))*np.minimum(1,(N-1-np.arange(N))/(.08*SR));mix*=fade[:,None]
assert np.isfinite(mix).all() and np.max(np.abs(mix))<.98
sf.write(ROOT/'audio/mix-premaster.wav',mix,SR,subtype='PCM_24')
for name,data in [('dialogue',voice),('original-score',score),('original-foley',foley),('riverfront-air',ambience)]:sf.write(ROOT/'audio'/(name+'.wav'),data,SR,subtype='PCM_24')
# Two-pass loudness mastering, retaining measured values for review.
result=subprocess.run(['ffmpeg','-hide_banner','-i',str(ROOT/'audio/mix-premaster.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
text=result.stderr;lo=text.rfind('{');hi=text.rfind('}')+1;measurement=json.loads(text[lo:hi])
filter_=('loudnorm=I=-16:TP=-1.5:LRA=7:measured_I='+measurement['input_i']+':measured_TP='+measurement['input_tp']+':measured_LRA='+measurement['input_lra']+':measured_thresh='+measurement['input_thresh']+':offset='+measurement['target_offset']+':linear=true:print_format=json')
master=subprocess.run(['ffmpeg','-v','info','-y','-i',str(ROOT/'audio/mix-premaster.wav'),'-af',filter_,'-ar','48000','-c:a','pcm_s24le',str(ROOT/'audio/master.wav')],capture_output=True,text=True,check=True)
lo=master.stderr.rfind('{');hi=master.stderr.rfind('}')+1;mastered=json.loads(master.stderr[lo:hi])
data,sr=sf.read(ROOT/'audio/master.wav');assert len(data)==N and sr==SR and np.max(np.abs(data))<.95
report=dict(duration=10,sampleRate=SR,channels=2,dialogue=dialogue,music='Original procedural G-major plucked cue',foley='Original synthesized feather rustles, magic glints and wooden cookie tap',inputMeasurement=measurement,masterMeasurement=mastered,masterSamplePeak=float(np.max(np.abs(data))),noAddedVoiceReverb=True,noNarrator=True)
(ROOT/'audio/mix-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(dict(masterPeak=report['masterSamplePeak'],loudness=mastered['output_i'],truePeak=mastered['output_tp'])))
