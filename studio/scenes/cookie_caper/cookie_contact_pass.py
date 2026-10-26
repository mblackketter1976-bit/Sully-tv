"""Small cartoon contact polish; reuse the accepted picture, voices and sound.

The cookie turns toward the tabletop continuously, contacts at 7.55 seconds,
bounces a few pixels and settles. No hard sprite-size swap at impact.
"""
import os
os.environ['ORT_DISABLE_TELEMETRY']='1'
import math,json,subprocess,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
import render_scene as base

OUT=base.ROOT.parent/'luna-cookie-contact-v02'
OUT.mkdir(exist_ok=True)
CONTACT=7.55

def cookie_pose(t):
    start=base.hand_at(164)+[630,111]
    if t<CONTACT:
        u=float(np.clip((t-6.85)/.70,0,1))
        ease=u*u*(3-2*u)
        height=48*(1-.52*ease)
        point=(1-u)*start+u*np.array([670.,503.-height/2])
        point[1]-=60*math.sin(math.pi*u)
        roll=-8*math.sin(math.pi*u)
        lift=max(0.,503.-(point[1]+height/2))
        slide=0.
    else:
        dt=t-CONTACT
        lift=9*math.exp(-10*dt)*abs(math.sin(18*dt))
        height=23.04+2*math.exp(-12*dt)*math.sin(20*dt)
        roll=3*math.exp(-12*dt)*math.sin(22*dt)
        slide=2.2*(1-math.exp(-12*dt))
        point=np.array([670.+slide,503.-height/2-lift])
    return point,height,roll,lift

def render(n):
    t=n/24
    if t<6.85:return base.render(n)
    canvas=base.background.convert('RGBA')
    base.shadow(canvas,426,626,130,13,95)
    base.shadow(canvas,1000,626,150,16,110)
    if t<8.5:canvas.alpha_composite(base.rook_at(n),(630,127))
    canvas.alpha_composite(base.luna_at(n).resize((358,358),Image.Resampling.LANCZOS),(250,273))
    point,height,roll,lift=cookie_pose(t)
    # Contact shadow follows the prop, tightening/darkening near the surface.
    opacity=round(78*max(0,1-lift/160))
    base.shadow(canvas,float(point[0]),505,23+lift*.04,3+lift*.012,opacity)
    prop=base.cookie.resize((48,max(1,round(height))),Image.Resampling.LANCZOS)
    prop=prop.rotate(roll,resample=Image.Resampling.BICUBIC,expand=True)
    canvas.alpha_composite(prop,(round(point[0]-prop.width/2),round(point[1]-prop.height/2)))
    if t>=8.5:canvas=canvas.crop((240,260,780,564)).resize((1280,720),Image.Resampling.LANCZOS)
    return canvas.convert('RGB')

if __name__=='__main__':
    # Verify continuous height/position across the contact; no discrete flip.
    before=cookie_pose(CONTACT-.00001);after=cookie_pose(CONTACT)
    assert np.linalg.norm(before[0]-after[0])<.02
    assert abs(before[1]-after[1])<.02
    for t in np.linspace(CONTACT,10,200):
        p,h,r,l=cookie_pose(float(t))
        assert abs(p[1]+h/2+l-503)<.00001 and l>=0
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24',
        '-video_size','1280x720','-framerate','24','-i','pipe:0','-an','-c:v','libx264',
        '-crf','17','-pix_fmt','yuv420p',str(OUT/'picture.mp4')],stdin=subprocess.PIPE)
    for n in range(240):
        frame=render(n)
        proc.stdin.write(frame.tobytes())
        if n in [164,170,178,181,182,183,184,186,190,194,218]:frame.save(OUT/f'contact_{n:03d}.jpg',quality=92)
    proc.stdin.close();assert proc.wait()==0
    dest=OUT/'Luna_Cookie_Caper_Contact_Polish_02.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(OUT/'picture.mp4'),'-i',str(base.ROOT/'audio/master.wav'),
        '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-t','10','-movflags','+faststart',str(dest)],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(dest),'-f','null','-'],check=True)
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(dest)]))
    v=next(s for s in info['streams'] if s['codec_type']=='video')
    assert v['nb_read_frames']=='240' and v['r_frame_rate']=='24/1' and float(info['format']['duration'])==10
    report=dict(seconds=10,frames=240,fps=24,contactTime=CONTACT,planeY=503,
        contactContinuous=True,groundPenetrationCheckPassed=True,
        audio='Unchanged accepted candidate dialogue/music/foley master; tap remains at 7.55s',
        voiceStatus='Not permanently approved',fullDecodePassed=True,
        sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
        limitation='Simple cartoon prop motion, not a full physics simulation; parent scene detail/beak-sync limitations remain.')
    (OUT/'verification.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report),flush=True)
