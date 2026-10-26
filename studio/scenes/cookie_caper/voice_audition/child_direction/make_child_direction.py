"""Voice B warmth, younger resonance/pitch direction; not an approved voice lock."""
import json,hashlib,subprocess
from pathlib import Path
import numpy as np
import parselmouth
from parselmouth.praat import call
import soundfile as sf

root=Path(__file__).parent
source=root.parent/'luna-youth-voice-test/Luna_Younger_Voice_B.wav'
sound=parselmouth.Sound(str(source))
pitch=sound.to_pitch(pitch_floor=100,pitch_ceiling=600)
voiced=pitch.selected_array['frequency'];voiced=voiced[voiced>0]
baseline=float(np.median(voiced))
settings=dict(formantRatio=1.18,targetMedianPitchHz=310.,pitchRangeFactor=1.08,durationFactor=1.0)
result=call(sound,'Change gender',100.,600.,settings['formantRatio'],settings['targetMedianPitchHz'],settings['pitchRangeFactor'],settings['durationFactor'])
wave=result.values[0]
assert np.isfinite(wave).all()
gain=min(.68/max(abs(wave)),.13/max(.001,float(np.sqrt(np.mean(wave*wave)))))
wave=wave*gain
dest=root/'Luna_Young_Voice_B.wav'
sf.write(dest,wave,round(result.sampling_frequency),subtype='PCM_24')
subprocess.run(['ffmpeg','-v','error','-y','-i',str(dest),'-ar','48000','-c:a','libmp3lame','-b:a','192k',str(root/'Luna_Young_Voice_B.mp3')],check=True)
sr=round(result.sampling_frequency);reel=np.zeros(round(3.5*sr));at=round(.2*sr);reel[at:at+len(wave)]=wave
sf.write(root/'preview-audio.wav',reel,sr,subtype='PCM_24')
report=dict(status='Younger, approximately five-year-old creative target; owner listening review required',
 interpretation='Boyz II interpreted as Voice B from the preceding A/B comparison',
 sourcePreset='af_nova',sourceSpeed=1.0,sourceLanguage='en-us',sourceModel='Kokoro v1.0 ONNX',
 sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),sourceMedianPitchHz=baseline,
 processing='Praat pitch-synchronous resynthesis with separately set formants, pitch and range; no added reverb/echo',
 praatParselmouthVersion=parselmouth.__version__,settings=settings,gain=gain,
 sampleRate=sr,seconds=len(wave)/sr,peak=float(np.max(np.abs(wave))),
 wavSha256=hashlib.sha256(dest.read_bytes()).hexdigest(),approved=False)
(root/'voice-settings.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
