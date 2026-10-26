"""Join the two accepted motion studies without changing their source files.
In Blender 5.2 capture the stop file with --capture; then open the turn file
and use --opening with that private cache. Both passes take --turn and --output.
Caches are locally generated intermediates and must never come from untrusted input.
"""
import bpy,sys,argparse,hashlib,json,pickle
from pathlib import Path
from mathutils import Matrix

parser=argparse.ArgumentParser()
parser.add_argument('--turn',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--capture',type=Path)
parser.add_argument('--opening',type=Path)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
source=Path(bpy.data.filepath).resolve();turn=args.turn.resolve();out=args.output.resolve()
if args.opening:
 cache=pickle.loads(args.opening.read_bytes());source=Path(cache['source'])
hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,turn]}
assert hashes[str(source)]=='e0101fcdeda9c58533b60acbf21afc720bca14271ab7cf26bee3391d8a6f9d5b'
assert hashes[str(turn)]=='f5e9a973bbf4feb4939afabf5ea127d65b795502b60482de6353604c2e70860c'
assert bpy.app.version[:2]==(5,2)
if args.capture:
 original=bpy.data.scenes['V41_Stop_Contact_Test'];bpy.context.window.scene=original;original.frame_set(193)
 oldroot=next(o for o in original.objects if o.name.startswith('LUNA_ROOT') and o.type=='EMPTY')
 rest=oldroot.matrix_world.copy();family=[oldroot,*oldroot.children_recursive]
 objects=[o for o in family if o.type in {'MESH','CURVE'} and not o.hide_render]
 for old in objects:
  if old.name.startswith('Luna skin Leg'):
   for mod in old.modifiers:mod.show_viewport=False
 frames=[]
 for frame in range(1,194):
  original.frame_set(frame);deps=bpy.context.evaluated_depsgraph_get();snapshots={}
  for old in objects:
   evaluated=old.evaluated_get(deps);mesh=evaluated.to_mesh()
   snapshots[old.name]=[tuple(evaluated.matrix_world@v.co) for v in mesh.vertices];evaluated.to_mesh_clear()
  frames.append({'delta':[list(row) for row in oldroot.matrix_world@rest.inverted()],'meshes':snapshots})
  if frame%24==0:print('OPENING_CAPTURED',frame,flush=True)
 args.capture.parent.mkdir(parents=True,exist_ok=True)
 args.capture.write_bytes(pickle.dumps({'source':str(source),'hashes':hashes,'frames':frames},protocol=5))
 print('CAPTURE_PASS',len(objects),flush=True);sys.exit(0)
assert args.opening and cache['hashes']==hashes
scene=bpy.data.scenes['Luna_Turn_Weight_Blink_Test'];scene.name='Luna_Walk_Stop_Turn_Look'
root=scene.objects['Luna movement root']
camera=scene.camera;camera_rest=camera.location.copy()
def curves(action):
 if hasattr(action,'fcurves'):return list(action.fcurves)
 return [c for layer in action.layers for strip in layer.strips for bag in getattr(strip,'channelbags',[]) for c in bag.fcurves]
actions=set()
for ob in scene.objects:
 for owner in [ob,ob.data.shape_keys if ob.type=='MESH' else None]:
  if owner and owner.animation_data and owner.animation_data.action:actions.add(owner.animation_data.action)
for action in actions:
 for curve in curves(action):
  for key in curve.keyframe_points:
   key.co.x+=192;key.handle_left.x+=192;key.handle_right.x+=192
for marker in scene.timeline_markers:marker.frame+=192
pairs=[]
for ob in scene.objects:
 if ob.type=='MESH' and ob.name.endswith(' movement'):
  name=ob.name[:-9]
  assert name in cache['frames'][0]['meshes'],ob.name
  if not ob.data.shape_keys:ob.shape_key_add(name='Basis')
  pairs.append((name,ob))
assert len(pairs)==34,len(pairs)
# Geometry caches reproduce the accepted walk including head and paw motion.
# Their local coordinates account for the new root and re-centred paw origins.
max_error=0.0
for frame in range(1,194):
 from mathutils import Vector
 stored=cache['frames'][frame-1];delta=Matrix(stored['delta'])
 snapshots=[(new,[Vector(v) for v in stored['meshes'][name]]) for name,new in pairs]
 for new,coords in snapshots:assert len(coords)==len(new.data.vertices),new.name
 bpy.context.window.scene=scene;scene.frame_set(frame)
 root.matrix_world=delta
 for prop in ['location','rotation_euler','scale']:root.keyframe_insert(prop,frame=frame)
 camera.location=camera_rest+delta.translation;camera.keyframe_insert('location',frame=frame)
 bpy.context.view_layer.update()
 for new,coords in snapshots:
  key=new.shape_key_add(name='Opening %03d'%frame)
  inverse=new.matrix_world.inverted()
  for v,world in zip(key.data,coords):
   v.co=inverse@world
   max_error=max(max_error,(new.matrix_world@v.co-world).length)
  for at,value in [(frame-1,0),(frame,1),(frame+1,0)]:
   key.value=value;key.keyframe_insert('value',frame=at)
 if frame%24==0:print('OPENING_BAKED',frame,flush=True)
for ob in scene.objects:
 if ob.name.startswith(('Upper eyelid','Lower eyelid')):
  for frame,hidden in [(1,True),(192,True),(193,False)]:
   ob.hide_render=hidden;ob.hide_viewport=hidden
   ob.keyframe_insert('hide_render',frame=frame);ob.keyframe_insert('hide_viewport',frame=frame)
for ob in scene.objects:
 for owner in [ob,ob.data.shape_keys if ob.type=='MESH' else None]:
  if owner and owner.animation_data and owner.animation_data.action:
   for curve in curves(owner.animation_data.action):
    for key in curve.keyframe_points:
     key.interpolation='CONSTANT' if curve.data_path in ['hide_render','hide_viewport'] else 'LINEAR'
# A stationary world-space floor grid makes the tracking camera's movement clear.
floor=scene.objects['Contact plane'];mat=floor.data.materials[0].copy();floor.data.materials[0]=mat
mat.use_nodes=True;nodes=mat.node_tree.nodes;links=mat.node_tree.links
bsdf=nodes.get('Principled BSDF');geo=nodes.new('ShaderNodeNewGeometry');separate=nodes.new('ShaderNodeSeparateXYZ')
links.new(geo.outputs['Position'],separate.inputs[0])
lines=[]
for axis in ['X','Y']:
 scale=nodes.new('ShaderNodeMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=2
 links.new(separate.outputs[axis],scale.inputs[0])
 fract=nodes.new('ShaderNodeMath');fract.operation='PINGPONG';fract.inputs[1].default_value=1;links.new(scale.outputs[0],fract.inputs[0])
 line=nodes.new('ShaderNodeMath');line.operation='LESS_THAN';line.inputs[1].default_value=.018;links.new(fract.outputs[0],line.inputs[0]);lines.append(line)
maximum=nodes.new('ShaderNodeMath');maximum.operation='MAXIMUM'
for i,line in enumerate(lines):links.new(line.outputs[0],maximum.inputs[i])
mix=nodes.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.32,.34,.36,1);mix.inputs[2].default_value=(.16,.18,.2,1)
links.new(maximum.outputs[0],mix.inputs[0]);links.new(mix.outputs[0],bsdf.inputs['Base Color'])
scene.frame_start=1;scene.frame_end=432;scene.render.fps=24
for frame,label in [(1,'Approved walk'),(121,'Approved stop'),(193,'Join: approved turn'),(386,'Settle and look'),(403,'Blink')]:scene.timeline_markers.new(label,frame=frame)
report={'frames':432,'fps':24,'durationSeconds':18,'openingMeshCount':len(pairs),'maxBakedWorldVertexError':max_error,'sourceHashes':hashes,'limits':'Movement prototype; existing appearance. Walk and turn are approved clips joined at frame 193. No new physical mass model or final artwork.'}
assert max_error<1e-5,max_error
readme=bpy.data.texts.new('READ_ME_SEQUENCE');readme.write('LUNA WALK → STOP → TURN → LOOK\nSpace to play 18 seconds. Movement review only.\n'+json.dumps(report,indent=2))
rebuild=bpy.data.texts.new('REBUILD_SEQUENCE.py');rebuild.write(Path(__file__).read_text())
for other in list(bpy.data.scenes):
 if other!=scene:bpy.data.scenes.remove(other)
bpy.data.orphans_purge(do_recursive=True)
scene.frame_set(1);scene.render.filepath='//Luna_Sequence_Frames/frame_'
out.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(out),compress=True)
for path,digest in hashes.items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
out.with_suffix('.verification.json').write_text(json.dumps(report,indent=2))
print('LUNA_SEQUENCE_PASS',json.dumps(report),flush=True)
