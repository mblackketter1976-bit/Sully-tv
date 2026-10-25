import bpy,json,hashlib,math,sys,argparse
from pathlib import Path
from mathutils import Vector
# Explicitly scoped to the reviewed V41 input; never apply this patch blindly.
SOURCE=Path(bpy.data.filepath).resolve()
parser=argparse.ArgumentParser()
parser.add_argument('--output',type=Path,default=SOURCE.parent/'V41_Contact_Test_Output')
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
OUT=args.output.resolve();OUT.mkdir(parents=True,exist_ok=True)
EXPECTED_SHA256='e6680e9c517af50315372c555bef563c83029acbe2a9589402d7f450ec10ed04'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=EXPECTED_SHA256:
 raise ValueError('This reviewed patch requires the unchanged original Luna_3D_Studio_V41.blend')
if bpy.app.version[:2]!=(5,2):
 raise ValueError('Use the verified Blender 5.2 runtime for this patch')
original_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
original=bpy.context.scene;original.name='V41_Original_Story'
original.frame_set(121)
paw_names=['Paw','Paw.001','Paw.002','Paw.003']
skin_names=['Luna skin Leg','Luna skin Leg.001','Luna skin Leg.002','Luna skin Leg.003']
original_feet={name:original.objects[name] for name in paw_names}
original_skins={name:original.objects[name] for name in skin_names}
# Record a baseline stop and opening pose before cloning any data.
def centres(scene,frame):
 scene.frame_set(frame)
 return {name:list(original_feet[name].matrix_world.translation) for name in paw_names}
baseline_stop=centres(original,193)
baseline_opening={f:centres(original,f) for f in [1,49,97,120]}
for ob in original.objects:ob['_v41_source_name']=ob.name
bpy.ops.scene.new(type='FULL_COPY')
trial=bpy.context.scene;trial.name='V41_Stop_Contact_Test'
objects={ob['_v41_source_name']:ob for ob in trial.objects}
for scene in [original,trial]:
 for ob in scene.objects:
  if '_v41_source_name' in ob:del ob['_v41_source_name']
feet={name:objects[name] for name in paw_names}
skins={name:objects[name] for name in skin_names}
for name,foot in feet.items():
 if foot.animation_data and foot.animation_data.action:foot.animation_data.action=foot.animation_data.action.copy()
for name,skin in skins.items():
 if len(skin.data.vertices)!=208 or len(skin.data.polygons)!=194:raise ValueError('Unexpected reviewed limb topology: '+name)
 if skin.data==original_skins[name].data:skin.data=skin.data.copy()
 keys=skin.data.shape_keys
 if keys==original_skins[name].data.shape_keys:raise ValueError('Shared shape data; refusing original mutation')
 if keys.animation_data and keys.animation_data.action:keys.animation_data.action=keys.animation_data.action.copy()
trial.frame_set(121)
held={name:foot.matrix_world.translation.copy() for name,foot in feet.items()}
old_frames={}
for frame in range(121,194):
 trial.frame_set(frame)
 old_frames[frame]={name:foot.matrix_world.translation.copy() for name,foot in feet.items()}
for frame in range(121,194):
 trial.frame_set(frame)
 for paw_name,skin_name in zip(paw_names,skin_names):
  foot,skin=feet[paw_name],skins[skin_name]
  key=skin.data.shape_keys.key_blocks.get('Pose %03d'%frame)
  if key is None or abs(key.value-1)>1e-5:raise ValueError('Expected single reviewed opening pose key at '+str(frame))
  delta=held[paw_name]-old_frames[frame][paw_name]
  local_delta=skin.matrix_world.inverted().to_3x3()@delta
  for index,vertex in enumerate(key.data):
   u=(index//16)/12
   weight=u*u*(3-2*u)
   vertex.co+=local_delta*weight
  matrix=foot.matrix_world.copy();matrix.translation=held[paw_name];foot.matrix_world=matrix
  foot.keyframe_insert(data_path='location',frame=frame)
# Verify actual world foot transforms at integer and half-frame samples.
max_drift=0.0
for step in range(145):
 frame=121+step*.5
 trial.frame_set(int(frame),subframe=frame%1)
 for name,foot in feet.items():max_drift=max(max_drift,(foot.matrix_world.translation-held[name]).length)
assert max_drift<1e-5,max_drift
# Verify original story data and original opening foot positions were preserved.
assert centres(original,193)==baseline_stop,'Original story foot actions changed'
for frame,baseline in baseline_opening.items():assert centres(original,frame)==baseline
for frame,baseline in baseline_opening.items():
 trial.frame_set(frame)
 for name,foot in feet.items():assert (foot.matrix_world.translation-Vector(baseline[name])).length<1e-6
# Evaluate the last ring before subdivision, including active relative shape keys.
def tip_world(skin):
 keys=skin.data.shape_keys;basis=keys.key_blocks[0]
 active=[key for key in keys.key_blocks[1:] if abs(key.value)>1e-8]
 points=[]
 for index in range(192,208):
  point=basis.data[index].co.copy()
  for key in active:point+=(key.data[index].co-basis.data[index].co)*key.value
  points.append(skin.matrix_world@point)
 return sum(points,Vector())/16
trial.frame_set(121)
expected_offsets={p:tip_world(skins[s])-feet[p].matrix_world.translation for p,s in zip(paw_names,skin_names)}
max_tip_error=0.0
for step in range(145):
 frame=121+step*.5;trial.frame_set(int(frame),subframe=frame%1)
 for p,s in zip(paw_names,skin_names):
  offset=tip_world(skins[s])-feet[p].matrix_world.translation
  max_tip_error=max(max_tip_error,(offset-expected_offsets[p]).length)
assert max_tip_error<1e-4,max_tip_error
trial.frame_start=1;trial.frame_end=193;trial.render.filepath='//V41_Contact_Test_Frames/frame_';trial.frame_set(111)
report={'source':'Luna_3D_Studio_V41.blend','sourceSHA256':original_hash,'blender':bpy.app.version_string,
 'change':'Opening stop only, frames 121–193; existing mesh poses and paw animation adapted in a separate scene.',
 'originalStoryScene':original.name,'trialScene':trial.name,'maxPawWorldDriftDuringStop':max_drift,
 'maxLimbTipOffsetError':max_tip_error,'originalStoryVerifiedUnchanged':True,'openingBeforeStopVerifiedUnchanged':True,
 'originalStopPawTravel':{name:(Vector(baseline_stop[name])-held[name]).length for name in paw_names},
 'limits':'Mechanical correction on the V41 blocking character. Not an approved likeness or final animation; body weight transfer and later scenes are not corrected.'}
(OUT/'stop-contact-verification.json').write_text(json.dumps(report,indent=2))
text=bpy.data.texts.new('READ_ME_V41_CONTACT_TEST')
text.write('V41 STOP CONTACT TEST\n\nThis file contains both the original story and a separate test scene.\nSelect V41_Stop_Contact_Test and play frames 1–193 to inspect the opening stop.\nThe original uploaded file was never overwritten.\n\n'+json.dumps(report,indent=2))
if '__file__' in globals() and Path(__file__).is_file():
 rebuild=bpy.data.texts.new('REBUILD_V41_STOP_TEST.py');rebuild.write(Path(__file__).read_text())
bpy.context.window.scene=trial
trial.frame_set(111)
path=OUT/'Luna_V41_Stop_Contact_Test.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(path),compress=True)
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==original_hash
print('V41_STOP_CONTACT_PASS',json.dumps(report),flush=True)
