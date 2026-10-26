import bpy,sys,argparse,json,pickle
from pathlib import Path
from mathutils import Matrix,Vector
p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True);p.add_argument('--capture',action='store_true');p.add_argument('--report',type=Path,required=True);p.add_argument('--finalize',type=Path)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=bpy.context.scene
feet=sorted([ob for ob in s.objects if ob.name.startswith('Paw') and ob.name.endswith(' movement')],key=lambda ob:ob.name)
assert len(feet)==4
if a.finalize:
 for ob in feet:
  for mod in list(ob.modifiers):
   if mod.name=='Presentation surface':ob.modifiers.remove(mod)
 code=bpy.data.texts.get('REBUILD_VISUAL.py');code.clear();code.write(Path(__file__).with_name('style_v41_luna.py').read_text())
 s.frame_set(1);s.render.filepath='//Luna_Studio_Frames/frame_'
 bpy.ops.wm.save_as_mainfile(filepath=str(a.finalize),compress=True)
def records():
 result=[]
 for frame in range(1,433):
  s.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();r={'frame':frame,'feet':{},'root':[list(row) for row in s.objects['Luna movement root'].matrix_world]}
  for ob in feet:
   ev=ob.evaluated_get(deps);mesh=ev.to_mesh();r['feet'][ob.name]=[tuple(ev.matrix_world@v.co) for v in mesh.vertices];ev.to_mesh_clear()
  result.append(r)
 return result
actual=records()
if a.capture:a.reference.write_bytes(pickle.dumps(actual,protocol=5));print('FOOT_REFERENCE_CAPTURED',flush=True);sys.exit(0)
expected=pickle.loads(a.reference.read_bytes());error=0;root_error=0
for x,y in zip(actual,expected):
 for name,points in x['feet'].items():
  assert len(points)==len(y['feet'][name]),name
  error=max(error,max((Vector(p)-Vector(q)).length for p,q in zip(points,y['feet'][name])))
 root_error=max(root_error,max(abs(p-q) for a,b in zip(x['root'],y['root']) for p,q in zip(a,b)))
assert error<1e-6,(error,root_error)
assert root_error<1e-6
report={'frames':432,'evaluatedPawVerticesCompared':432*sum(len(v) for v in actual[0]['feet'].values()),'maxPawWorldVertexDifference':error,'maxRootMatrixDifference':root_error,'limits':'Appearance changes intentionally alter ear geometry and materials. Contact/movement comparison preserves the previously approved feet and root across all 18 seconds.'}
a.report.write_text(json.dumps(report,indent=2));print('VISUAL_MOTION_VERIFIED',json.dumps(report),flush=True)
