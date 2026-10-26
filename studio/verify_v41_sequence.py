import bpy,sys,pickle,json,argparse
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--opening',type=Path,required=True);p.add_argument('--turn-cache',type=Path,required=True);p.add_argument('--capture-turn',action='store_true');p.add_argument('--report',type=Path,required=True);p.add_argument('--render-dir',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);scene=bpy.context.scene
for ob in scene.objects:
 if ob.name.startswith('Luna skin Leg'):
  for mod in ob.modifiers:mod.show_viewport=False
def snapshot(frame):
 scene.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();result={}
 for ob in scene.objects:
  if ob.type=='MESH' and ob.name.endswith(' movement'):
   ev=ob.evaluated_get(deps);mesh=ev.to_mesh();result[ob.name]=[tuple(ev.matrix_world@v.co) for v in mesh.vertices];ev.to_mesh_clear()
 return result
if a.capture_turn:
 data={f:snapshot(f) for f in [1,24,25,40,80,120,193,200,217,240]}
 a.turn_cache.write_bytes(pickle.dumps(data,protocol=5));print('TURN_REFERENCE_CAPTURED',flush=True);sys.exit(0)
opening=pickle.loads(a.opening.read_bytes());max_open=0;max_turn=0
for f,record in enumerate(opening['frames'],1):
 actual=snapshot(f)
 for name,coords in record['meshes'].items():
  values=actual[name+' movement'];assert len(values)==len(coords)
  max_open=max(max_open,max((Vector(x)-Vector(y)).length for x,y in zip(values,coords)))
for f,expected in pickle.loads(a.turn_cache.read_bytes()).items():
 actual=snapshot(f+192)
 for name,coords in expected.items():max_turn=max(max_turn,max((Vector(x)-Vector(y)).length for x,y in zip(actual[name],coords)))
report={'openingFramesCompared':193,'turnFramesCompared':10,'maxOpeningWorldVertexError':max_open,'maxTurnWorldVertexError':max_turn,'toleranceSceneUnits':1e-5}
assert max_open<1e-5,report
assert max_turn<1e-5,report
a.report.write_text(json.dumps(report,indent=2));print('SEQUENCE_REOPENED_VERIFIED',json.dumps(report),flush=True)
for ob in scene.objects:
 if ob.name.startswith('Luna skin Leg'):
  for mod in ob.modifiers:mod.show_viewport=True
if a.render_dir:
 a.render_dir.mkdir(parents=True,exist_ok=True);scene.render.resolution_percentage=65;scene.cycles.samples=16
 for f in [48,121,193,312,409]:
  scene.frame_set(f);scene.render.image_settings.file_format='PNG';scene.render.filepath=str(a.render_dir/('review_%03d.png'%f));bpy.ops.render.render(write_still=True)
  print('SEQUENCE_RENDERED',f,flush=True)
