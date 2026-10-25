import bpy,math,json,hashlib,sys,argparse
from pathlib import Path
from mathutils import Vector,Matrix
SOURCE=Path(bpy.data.filepath).resolve()
parser=argparse.ArgumentParser(description='Build a standalone motion study from the reviewed, approved V41 stop-test input.')
parser.add_argument('--output',type=Path,default=SOURCE.parent/'Luna_Next_Movement_Test')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=args.output.resolve();OUT.mkdir(parents=True,exist_ok=True)
EXPECTED='e0101fcdeda9c58533b60acbf21afc720bca14271ab7cf26bee3391d8a6f9d5b'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=EXPECTED:raise ValueError('Requires the unchanged, approved Luna_V41_Stop_Contact_Test.blend input')
if bpy.app.version[:2]!=(5,2):raise ValueError('Use verified Blender 5.2 for this builder')
source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
source_scene=bpy.data.scenes['V41_Stop_Contact_Test'];bpy.context.window.scene=source_scene;source_scene.frame_set(193)
root=next(o for o in source_scene.objects if o.type=='EMPTY' and o.name.startswith('LUNA_ROOT'))
family=[root,*root.children_recursive]
head=next(o for o in family if o.type=='EMPTY' and o.name.startswith('LUNA_HEAD_ACTING'))
scene=bpy.data.scenes.new('Luna_Turn_Weight_Blink_Test');scene.world=source_scene.world.copy()
# Freeze evaluated, visible geometry; no historical pose/action stacks are copied.
newroot=bpy.data.objects.new('Luna movement root',None);scene.collection.objects.link(newroot);newroot.location=root.matrix_world.translation
newhead=bpy.data.objects.new('Luna head acting',None);scene.collection.objects.link(newhead);newhead.parent=newroot;newhead.location=head.matrix_world.translation-newroot.location
bpy.context.view_layer.update()
source_scene.frame_set(193);deps=bpy.context.evaluated_depsgraph_get()
objects={};mesh_records=[]
for ob in family:
 if ob.type not in {'MESH','CURVE'} or ob.hide_render:continue
 skin=ob.name.startswith('Luna skin Leg')
 oldflags=[m.show_viewport for m in ob.modifiers]
 if skin:
  for m in ob.modifiers:m.show_viewport=False
  bpy.context.view_layer.update()
 evaluated=ob.evaluated_get(deps)
 data=bpy.data.meshes.new_from_object(evaluated,preserve_all_data_layers=True,depsgraph=deps)
 data.transform(ob.matrix_world)
 for m,flag in zip(ob.modifiers,oldflags):m.show_viewport=flag
 new=bpy.data.objects.new(ob.name+' movement',data);scene.collection.objects.link(new)
 new.parent=newhead if ob in head.children_recursive else newroot
 new.matrix_parent_inverse=new.parent.matrix_world.inverted();new.matrix_basis=Matrix.Identity(4)
 objects[ob.name]=new
 if skin:
  assert len(data.vertices)==208
  smooth=new.modifiers.new('Existing continuous surface smoothing','SUBSURF');smooth.levels=1;smooth.render_levels=1
 mesh_records.append((ob,new))
bpy.context.window.scene=scene;bpy.context.view_layer.update()
for old,new in mesh_records:
 new.matrix_parent_inverse=new.parent.matrix_world.inverted();new.matrix_basis=Matrix.Identity(4)
bpy.context.view_layer.update()
feet={};skins={};eye_components={-1:[],1:[]}
for old,new in mesh_records:
 if old.name.startswith('Paw'):
  centre=old.matrix_world.translation.copy()
  role=('front' if centre.x>root.location.x else 'hind')+('_left' if centre.y<root.location.y else '_right')
  new.data.transform(Matrix.Translation(-centre));new.matrix_world=Matrix.Translation(centre)
  new.rotation_mode='QUATERNION'
  feet[role]={'ob':new,'initial':centre,'position':centre.copy(),'yaw':0.0}
 if old.name.startswith('Luna skin Leg'):
  centre=sum((old.matrix_world@v.co for v in old.data.shape_keys.key_blocks['Pose 193'].data[:16]),Vector())/16
  role=('front' if centre.x>root.location.x else 'hind')+('_left' if centre.y<root.location.y else '_right')
  new.shape_key_add(name='Basis');skins[role]=new
 if old.name.startswith(('Eye white','Blue iris','Pupil')):
  side=-1 if old.matrix_world.translation.y<root.location.y else 1
  eye_components[side].append((old,new))
assert len(feet)==len(skins)==4
# A physical pair of eyelid caps occludes each eye; eye meshes are not squashed.
headmaterial=next(n.data.materials[0] for o,n in mesh_records if o.name.startswith('Head') and n.data.materials)
lids=[]
for side,components in eye_components.items():
 white=next(o for o,n in components if o.name.startswith('Eye white'))
 pupil=next(o for o,n in components if o.name.startswith('Pupil'))
 axis_x=(pupil.matrix_world.translation-white.matrix_world.translation).normalized()
 up=head.matrix_world.to_3x3()@Vector((0,0,1));axis_z=(up-axis_x*up.dot(axis_x)).normalized();axis_y=axis_z.cross(axis_x).normalized()
 frame=Matrix((axis_x,axis_y,axis_z)).transposed();points=[]
 for old,new in components:
  points.extend(frame.transposed()@v.co for v in new.data.vertices)
 low=Vector(tuple(min(p[i] for p in points) for i in range(3)));high=Vector(tuple(max(p[i] for p in points) for i in range(3)))
 centre=frame@((low+high)/2);radii=(high-low)*.56+Vector((.003,.003,.003))
 pivot=bpy.data.objects.new('Eye lid pivot '+str(side),None);scene.collection.objects.link(pivot);pivot.parent=newhead
 pivot.matrix_world=Matrix.Translation(centre)@frame.to_4x4()
 for upper in [True,False]:
  vertices=[];faces=[];rings=9;around=32
  for ring in range(rings):
   lat=math.pi*.5*ring/(rings-1)*(1 if upper else -1)
   for j in range(around):
    angle=2*math.pi*j/around
    vertices.append((radii.x*math.cos(lat)*math.cos(angle),radii.y*math.cos(lat)*math.sin(angle),radii.z*math.sin(lat)))
  for ring in range(rings-1):
   for j in range(around):
    a=ring*around+j;b=ring*around+(j+1)%around;faces.append((a,b,b+around,a+around))
  mesh=bpy.data.meshes.new('Eyelid cap');mesh.from_pydata(vertices,[],faces);mesh.update();mesh.materials.append(headmaterial)
  lid=bpy.data.objects.new(('Upper' if upper else 'Lower')+' eyelid '+str(side),mesh);scene.collection.objects.link(lid);lid.parent=pivot
  for p in mesh.polygons:p.use_smooth=True
  lids.append((lid,upper))
# Keep body and paws in original scene coordinates. A flat diagnostic floor
# meets their existing soles; material/character redesign is out of scope.
minimum=min((f['ob'].matrix_world@v.co).z for f in feet.values() for v in f['ob'].data.vertices)
floor_data=bpy.data.meshes.new('Floor');floor_data.from_pydata([(-20,-20,minimum),(20,-20,minimum),(20,20,minimum),(-20,20,minimum)],[],[(0,1,2,3)])
floor=bpy.data.objects.new('Contact plane',floor_data);scene.collection.objects.link(floor)
mat=bpy.data.materials.new('Diagnostic floor');mat.diffuse_color=(.32,.34,.36,1);floor.data.materials.append(mat)
initial_root=newroot.location.copy();initial={name:f['initial'].copy() for name,f in feet.items()}
neutral={name:pos.copy() for name,pos in initial.items()}
for kind in ['front','hind']:
 avg=sum(initial[name].x for name in initial if name.startswith(kind))/2
 for name in neutral:
  if name.startswith(kind):neutral[name].x=avg
order=['hind_left','front_left','hind_right','front_right']*3
step_frames=14;start=25;end=start+len(order)*step_frames
plans=[];positions={k:v.copy() for k,v in initial.items()};headings={k:0.0 for k in initial}
def ease(u):
 u=max(0,min(1,u));return u*u*u*(10+u*(-15+6*u))
def body_yaw(frame):return -math.pi/4*ease((frame-start)/(8*step_frames))
for index,name in enumerate(order):
 a=start+index*step_frames;b=a+step_frames;yaw=body_yaw(b+2*step_frames)
 target=initial_root+Matrix.Rotation(yaw,3,'Z')@(neutral[name]-initial_root)
 plans.append({'name':name,'a':a,'b':b,'from':positions[name].copy(),'to':target,'fromYaw':headings[name],'toYaw':yaw})
 positions[name]=target.copy();headings[name]=yaw
records=[];baseline_vertices={name:[v.co.copy() for v in skin.data.vertices] for name,skin in skins.items()}
for frame_no in range(1,241):
 scene.frame_set(frame_no)
 current={name:pos.copy() for name,pos in initial.items()};angles={name:0.0 for name in initial};state={name:'stance' for name in initial};active=None;u=0.0
 for plan in plans:
  name=plan['name']
  if frame_no>=plan['b']:current[name]=plan['to'].copy();angles[name]=plan['toYaw']
  elif frame_no>plan['a']:
   u=(frame_no-plan['a'])/(plan['b']-plan['a']);active=name
   current[name]=plan['from'].lerp(plan['to'],ease(u));current[name].z+=.085*math.sin(math.pi*u)**2
   angles[name]=plan['fromYaw']+(plan['toYaw']-plan['fromYaw'])*ease(u);state[name]='swing'
  elif frame_no==plan['a']:current[name]=plan['from'].copy();angles[name]=plan['fromYaw']
 if active:
  support=sum((pos for name,pos in current.items() if name!=active),Vector())/3
  allmean=sum(current.values(),Vector())/4
  shift=(support-allmean)*.22*math.sin(math.pi*u)**2;shift.z=0
  if shift.length>.035:shift=shift.normalized()*.035
 else:shift=Vector()
 newroot.location=initial_root+shift;newroot.location.z+=.005*math.sin(math.pi*u)**2 if active else 0
 newroot.rotation_euler=(0,0,body_yaw(frame_no))
 newroot.keyframe_insert('location',frame=frame_no);newroot.keyframe_insert('rotation_euler',frame=frame_no)
 newhead.rotation_euler=(0,-.14*ease((frame_no-1)/24),-.12*math.sin(math.pi*max(0,min(1,(frame_no-start)/(8*step_frames)))) )
 newhead.keyframe_insert('rotation_euler',frame=frame_no)
 bpy.context.view_layer.update()
 for name,entry in feet.items():
  ob=entry['ob'];ob.matrix_world=Matrix.Translation(current[name])@Matrix.Rotation(angles[name],4,'Z')
  for channel in ['location','rotation_quaternion','scale']:ob.keyframe_insert(channel,frame=frame_no)
  skin=skins[name];predicted=newroot.matrix_world@initial[name]
  delta=skin.matrix_world.inverted().to_3x3()@(current[name]-predicted)
  key=skin.shape_key_add(name='Motion %03d'%frame_no)
  for index,vertex in enumerate(key.data):
   p=min(1,(index//16)/12/.75);weight=p*p*(3-2*p)
   vertex.co=baseline_vertices[name][index]+delta*weight
  for key_frame,value in [(frame_no-1,0),(frame_no,1),(frame_no+1,0)]:key.value=value;key.keyframe_insert('value',frame=key_frame)
 if frame_no<211 or frame_no>225:closure=0
 elif frame_no<216:closure=ease((frame_no-211)/5)
 elif frame_no<219:closure=1
 else:closure=1-ease((frame_no-219)/6)
 for lid,upper in lids:
  lid.rotation_euler.y=(-1 if upper else 1)*math.pi/2*(1-closure);lid.keyframe_insert('rotation_euler',frame=frame_no)
 records.append({'frame':frame_no,'feet':{k:list(v) for k,v in current.items()},'state':state,'yaw':body_yaw(frame_no)})
# Linear channels prevent automatic handle overshoot between baked samples.
def action_curves(action):
 if hasattr(action,'fcurves'):return list(action.fcurves)
 return [curve for layer in action.layers for strip in layer.strips for bag in getattr(strip,'channelbags',[]) for curve in bag.fcurves]
used_actions=set()
for ob in scene.objects:
 if ob.animation_data and ob.animation_data.action:used_actions.add(ob.animation_data.action)
 if ob.type=='MESH' and ob.data.shape_keys and ob.data.shape_keys.animation_data:used_actions.add(ob.data.shape_keys.animation_data.action)
for action in used_actions:
 for curve in action_curves(action):
  for key in curve.keyframe_points:key.interpolation='LINEAR'
scene.frame_start=1;scene.frame_end=240;scene.render.fps=24
max_target_error=0.0;max_half_stance=0.0;min_sole=1e9
for item in records:
 scene.frame_set(item['frame']);deps=bpy.context.evaluated_depsgraph_get()
 for name,f in feet.items():
  actual=f['ob'].matrix_world.translation;max_target_error=max(max_target_error,(actual-Vector(item['feet'][name])).length)
  evaluated=f['ob'].evaluated_get(deps);mesh=evaluated.to_mesh();min_sole=min(min_sole,min((evaluated.matrix_world@v.co).z for v in mesh.vertices));evaluated.to_mesh_clear()
for index in range(239):
 scene.frame_set(index+1,subframe=.5)
 a,b=records[index],records[index+1]
 for name,f in feet.items():
  if a['state'][name]==b['state'][name]=='stance' and (Vector(a['feet'][name])-Vector(b['feet'][name])).length<1e-6:
   max_half_stance=max(max_half_stance,(f['ob'].matrix_world.translation-Vector(a['feet'][name])).length)
assert max_target_error<1e-5,max_target_error
assert max_half_stance<.001,max_half_stance
assert min_sole>=minimum-1e-5,(min_sole,minimum)
for loc,power,size in [((2,-4,5),850,4),((-3,1,4),650,4)]:
 data=bpy.data.lights.new('Study light','AREA');data.energy=power;data.shape='DISK';data.size=size
 ob=bpy.data.objects.new('Study light',data);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
data=bpy.data.cameras.new('Movement study camera');camera=bpy.data.objects.new('Movement study camera',data);scene.collection.objects.link(camera);camera.location=(3,-4,2.8);camera.rotation_euler=(Vector((0,0,.95))-camera.location).to_track_quat('-Z','Y').to_euler();data.type='ORTHO';data.ortho_scale=3.5;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=32;scene.cycles.use_denoising=True
scene.render.resolution_x=800;scene.render.resolution_y=600;scene.render.resolution_percentage=100;scene.render.filepath='//Luna_Movement_Test_Frames/frame_'
report={'source':'Luna_V41_Stop_Contact_Test.blend','sourceSHA256':source_hash,'blender':bpy.app.version_string,'frames':240,'fps':24,'turnDegrees':-45,'steps':12,'maxFramePawTargetError':max_target_error,'maxHalfFrameStanceDrift':max_half_stance,'minimumPawSoleHeight':min_sole,'floorHeight':minimum,'limits':'Prototype movement study. No calibrated mass/physics, final anatomy, final artwork, dialogue or production pilot. Limb surfaces retain the prior mesh-pose approach.'}
text=bpy.data.texts.new('READ_ME_MOVEMENT_TEST');text.write('LUNA: TURN, WEIGHT SHIFT AND BLINK TEST\n\nPress Space to play 10 seconds. Appearance is the existing prototype. The approved stop file is unchanged.\n\n'+json.dumps(report,indent=2))
(OUT/'movement-verification.json').write_text(json.dumps(report,indent=2))
if '__file__' in globals() and Path(__file__).is_file():
 rebuild=bpy.data.texts.new('REBUILD_TURN_STUDY.py');rebuild.write(Path(__file__).read_text())
for frame,label in [(1,'Ready'),(25,'Turn and weight shift'),(194,'Settle'),(211,'Blink')]:scene.timeline_markers.new(label,frame=frame)
if bpy.context.screen:
 for area in bpy.context.screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.region_3d.view_perspective='CAMERA'
   area.spaces.active.shading.type='SOLID';area.spaces.active.shading.color_type='MATERIAL'
   area.spaces.active.overlay.show_extras=False
# Save only the new study; histories remain intact in their original files.
for old_scene in list(bpy.data.scenes):
 if old_scene!=scene:bpy.data.scenes.remove(old_scene)
bpy.data.orphans_purge(do_recursive=True)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Luna_V41_Turn_Weight_Blink_Test.blend'),compress=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash
print('LUNA_NEXT_MOTION_PASS',json.dumps(report),flush=True)
