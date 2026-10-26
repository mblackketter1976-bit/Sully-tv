import bpy,sys
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]);s=bpy.context.scene;s.frame_set(193)
s.render.resolution_x=960;s.render.resolution_y=720;s.render.resolution_percentage=100;s.cycles.samples=48;s.render.image_settings.file_format='PNG';s.render.filepath=str(out)
bpy.ops.render.render(write_still=True)
