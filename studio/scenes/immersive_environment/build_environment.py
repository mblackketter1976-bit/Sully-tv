"""Independent foliage/water passes with explicit protected contact regions.

Eight-second ambient-motion proof. Characters deliberately hold their pose;
this is not a new character-performance or lip-sync clip.
"""
import json,math,hashlib,subprocess,shutil
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw
from scipy.signal import butter,sosfilt
import soundfile as sf

ROOT=Path(__file__).parent;ASSETS=ROOT/'assets';ASSETS.mkdir(exist_ok=True)
W,H=1280,720;FPS=24;SECONDS=8
SOURCE=Path('/workspace/scratch/743bef75a537/generated_images/exec-fd04cf7e-6c4c-4788-8b91-61c2d002b1c2.png')
CLEAN=Path('/workspace/scratch/743bef75a537/generated_images/exec-09373be4-cc6e-49fc-8e55-560aaedb44e4.png')

def polygon(points):
    m=np.zeros((H,W),np.uint8);cv2.fillPoly(m,[np.array(points,np.int32)],255);return m


def setup():
    for path,name in [(SOURCE,'source-scene.png'),(CLEAN,'foliage-clean-plate.png')]:
        dest=ASSETS/name
        if not dest.exists():shutil.copy2(path,dest)
    original=np.asarray(Image.open(ASSETS/'source-scene.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS))
    clean=np.asarray(Image.open(ASSETS/'foliage-clean-plate.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS))
    # Fit only a global similarity placement; source artwork is otherwise kept.
    sift=cv2.SIFT_create(nfeatures=1800)
    kp0,d0=sift.detectAndCompute(original,None);kp1,d1=sift.detectAndCompute(clean,None)
    good=[a for a,b in cv2.BFMatcher().knnMatch(d1,d0,k=2) if a.distance<.72*b.distance]
    src=np.float32([kp1[m.queryIdx].pt for m in good]);dst=np.float32([kp0[m.trainIdx].pt for m in good])
    matrix,inliers=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2)
    assert matrix is not None and int(inliers.sum())>100
    clean=cv2.warpAffine(clean,matrix,(W,H),borderMode=cv2.BORDER_REFLECT)
    protect=polygon([(0,0),(132,0),(132,720),(0,720)])
    luna=polygon([(160,710),(160,570),(174,494),(190,453),(219,427),(242,405),
      (253,385),(247,348),(240,312),(249,280),(270,280),(299,304),(319,324),
      (346,305),(371,260),(382,234),(404,237),(427,263),(438,303),(449,326),
      (474,341),(507,350),(534,373),(542,418),(535,446),(560,451),(568,485),
      (547,510),(506,522),(484,534),(484,675),(440,710)])
    rook=polygon([(635,0),(1280,0),(1280,720),(1140,720),(1140,600),(1080,500),
      (840,490),(780,485),(755,460),(680,448),(650,435),(607,422),(570,415),
      (570,362),(598,342),(665,347),(700,325),(680,300),(660,270),(643,230),(630,195)])
    crate=polygon([(448,452),(1260,452),(1280,720),(448,720)])
    protect=np.maximum.reduce([protect,luna,rook,crate])
    protect=cv2.dilate(protect,np.ones((7,7),np.uint8))>0
    # Explicit river panes keep fixed ropes/posts out of the water pass.
    water=np.maximum.reduce([polygon(p) for p in [
      [(140,329),(253,329),(253,379),(220,370),(180,360),(140,348)],
      [(142,398),(180,403),(180,445),(142,445)],
      [(225,412),(253,419),(253,445),(225,445)],
      [(142,480),(181,483),(181,524),(142,524)]
    ]])
    water[protect]=0
    water=cv2.GaussianBlur(water.astype('float32')/255,(0,0),1.2)
    water[protect]=0
    diff=np.max(np.abs(original.astype(float)-clean.astype(float)),axis=2)
    r,g,b=original[:,:,0].astype(float),original[:,:,1].astype(float),original[:,:,2].astype(float)
    tree_roi=polygon([(257,268),(270,210),(292,195),(298,153),(320,142),(338,119),
       (357,129),(364,159),(390,169),(383,205),(399,222),(394,261),(365,289),(319,308),(276,299)])>0
    tree_colors=(r<180)&(g<190)&(b<220)&(g>r*.65)
    tree=(tree_roi&tree_colors&(diff>12)&~protect).astype('uint8')*255
    flower_roi=polygon([(475,244),(601,239),(625,271),(620,344),(472,367)])>0
    flower_colors=((g>r*1.04)&(g>b*1.02))|((r>g*1.22)&(b>g*.92)&(r>90))
    flowers=(flower_roi&flower_colors&(diff>18)&~protect).astype('uint8')*255
    layers=[];base=original.astype('float32').copy()
    for name,mask,anchor,amp in [('tree',tree,308,4.5),('flowers',flowers,367,2.0)]:
        mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
        mask[protect]=0
        # Derive enough alpha to reconstruct the source without invalid RGB,
        # then remove the old sky tint from the foliage's translucent edges.
        delta=original.astype('float32')-clean.astype('float32')
        required=np.where(delta>=0,delta/np.maximum(1,255-clean.astype('float32')),
                          -delta/np.maximum(1,clean.astype('float32')))
        alpha=np.sqrt(np.clip(required.max(axis=2),0,1))*(mask>0)
        alpha[protect]=0
        clear=(alpha>0).astype('float32')
        base=base*(1-clear[:,:,None])+clean*clear[:,:,None]
        color=(original.astype('float32')-(1-alpha[:,:,None])*clean)/np.maximum(alpha[:,:,None],.0001)
        color=np.clip(color,0,255);color[alpha==0]=0
        rgba=np.dstack([color,np.rint(alpha*255)]).astype('uint8');Image.fromarray(rgba,'RGBA').save(ASSETS/f'{name}-layer.png')
        layers.append(dict(name=name,alpha=alpha,premult=color*alpha[:,:,None],clear=clear,anchor=anchor,amplitude=amp))
    allowed=water>0
    for layer in layers:allowed|=cv2.dilate((layer['clear']>0).astype('uint8'),np.ones((17,17),np.uint8))>0
    allowed[protect]=False
    Image.fromarray(np.rint(water*255).astype('uint8')).save(ASSETS/'water-mask.png')
    Image.fromarray((protect*255).astype('uint8')).save(ASSETS/'protected-contacts-and-foreground.png')
    Image.fromarray(np.clip(base,0,255).astype('uint8')).save(ASSETS/'static-backing.png')
    config=dict(size=[W,H],fps=FPS,seconds=SECONDS,cleanPlateSimilarity=matrix.tolist(),
       registrationInliers=int(inliers.sum()),layerPixelCounts={l['name']:int(np.sum(l['alpha']>.1)) for l in layers},
       waterPixels=int(np.sum(water>.1)),layerOrder=['static-backing','water/reflections','tree','flowers','protected foreground/characters/crate'],
       contactPolicy='Restore exact source pixels inside protected actor/prop/contact masks after environment passes.')
    (ROOT/'layer-config.json').write_text(json.dumps(config,indent=2))
    return original,base,layers,water,protect,allowed


def renderer(original,base,layers,water,protect,allowed):
    yy,xx=np.mgrid[:H,:W].astype('float32')
    def frame(t):
        phase=(t%SECONDS)*2*math.pi/SECONDS
        result=base.copy()
        # Natural horizontal river motion carries the existing reflected light.
        dx=2.4*np.sin(yy*.27+phase*2)+.8*np.sin(yy*.61-phase*3)
        dy=.35*np.sin(xx*.045+phase*2)
        flowed=cv2.remap(original,xx+dx.astype('float32'),yy+dy.astype('float32'),cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT).astype('float32')
        gold=(flowed[:,:,0]>flowed[:,:,1]+9)&(flowed[:,:,1]>flowed[:,:,2]+12)
        glint=1+.07*np.sin(yy*.34+phase*3)*gold
        flowed*=glint[:,:,None]
        result=result*(1-water[:,:,None])+flowed*water[:,:,None]
        for layer in layers:
            alpha=layer['alpha'];anchor=layer['anchor'];strength=np.clip((anchor-yy)/180,0,1)**1.5
            sway=layer['amplitude']*np.sin(phase+.22)*strength
            flutter=.45*np.sin(yy*.16+phase*3)*strength
            mx=xx-(sway+flutter).astype('float32');my=yy-(.28*np.sin(phase*2+xx*.025)*strength).astype('float32')
            a=cv2.remap(alpha,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
            premult=cv2.remap(layer['premult'],mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
            a[protect]=0
            premult[protect]=0
            result=result*(1-a[:,:,None])+premult
        result=np.clip(np.rint(result),0,255).astype('uint8')
        result[~allowed]=original[~allowed]
        result[protect]=original[protect]
        return result
    return frame


def main():
    original,base,layers,water,protect,allowed=setup();frame=renderer(original,base,layers,water,protect,allowed)
    assert np.array_equal(frame(0),frame(8)),'Loop endpoint differs'
    for t in [0,1.25,2.5,4,6.5,7.95]:
        im=frame(t)
        assert np.array_equal(im[protect],original[protect])
        assert np.array_equal(im[~allowed],original[~allowed])
    proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}',
      '-framerate','24','-i','pipe:0','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(ROOT/'picture.mp4')],stdin=subprocess.PIPE)
    changes=[]
    for n in range(192):
        im=frame(n/24);proc.stdin.write(im.tobytes())
        changes.append(int(np.sum(np.max(np.abs(im.astype(int)-original.astype(int)),axis=2)>2)))
        if n in [0,48,96,144]:Image.fromarray(im).save(ROOT/f'proof_{n:03d}.jpg',quality=92)
    proc.stdin.close();assert proc.wait()==0
    sr=48000;n=8*sr;rng=np.random.default_rng(27);t=np.arange(n)/sr;mix=np.zeros((n,2))
    for ch in range(2):
        wind=sosfilt(butter(2,[100,650],btype='bandpass',fs=sr,output='sos'),rng.normal(0,1,n))
        river=sosfilt(butter(2,[350,2000],btype='bandpass',fs=sr,output='sos'),rng.normal(0,1,n))
        mix[:,ch]=.009*wind*(.75+.25*np.sin(t*2*math.pi/8))+.007*river*(.75+.25*np.sin(t*2*math.pi/4+ch))
    fade=np.minimum(1,t/.05)*np.minimum(1,(8-t)/.1);mix*=fade[:,None]
    sf.write(ROOT/'environment-ambience.wav',mix,sr,subtype='PCM_24')
    output=ROOT/'Luna_Living_Environment_Test_01.mp4'
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(ROOT/'picture.mp4'),'-i',str(ROOT/'environment-ambience.wav'),
      '-map','0:v:0','-map','1:a:0','-c:v','copy','-af','loudnorm=I=-30:TP=-9:LRA=6','-ar','48000',
      '-c:a','aac','-b:a','160k','-t','8','-movflags','+faststart',str(output)],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-'],check=True)
    report=dict(seconds=8,frames=192,fps=24,sourceDrawings=1,characterAnimation='Held staging pose, deliberately static',
      environmentLayers=['water plus reflected light','root-anchored tree sway','flower/leaf movement'],
      rawProtectedContactsUnchanged=True,rawStaticPixelsUnchanged=True,mathematicalLoopEndpointIdentical=True,
      changedPixelRange=[min(changes),max(changes)],fullDecodePassed=True,sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
      limitation='Environment proof, not a completed character scene. Simple extracted 2D layers; concealed foliage backing is approximate. No realtime playback claim.')
    (ROOT/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)


if __name__=='__main__':main()
