import bpy,time,sys,argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--probe',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=6;s.cycles.use_denoising=True;s.render.use_persistent_data=True
s.render.resolution_x=512;s.render.resolution_y=384;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
for ob in s.objects:
 for mod in ob.modifiers:
  if mod.type=='SUBSURF':mod.render_levels=1
a.output.mkdir(parents=True,exist_ok=True)
frames=[265,266] if a.probe else list(range(217,361))
for i,frame in enumerate(frames):
 t=time.monotonic();s.frame_set(frame);s.render.filepath=str(a.output/('frame_%04d.png'%i));bpy.ops.render.render(write_still=True)
 print('PREVIEW_FRAME',i,frame,round(time.monotonic()-t,2),flush=True)
