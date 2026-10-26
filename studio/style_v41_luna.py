"""A separate native-mesh appearance pass over the accepted motion sequence."""
import bpy,math,json,hashlib,sys,argparse
import numpy as np
from pathlib import Path
from mathutils import Vector
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--render-dir',type=Path,required=True)
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);source=Path(bpy.data.filepath);digest=hashlib.sha256(source.read_bytes()).hexdigest();scene=bpy.context.scene
scene.frame_set(193)
def material(name,color,rough=.5):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough
 return m,bs
coat,bs=material('Luna • silver merle velvet',(.48,.50,.56),.62)
bs.inputs['Sheen Weight'].default_value=.18
nodes=coat.node_tree.nodes;links=coat.node_tree.links
attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='luna_rest'
noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5.3;noise.inputs['Detail'].default_value=2.2;noise.inputs['Roughness'].default_value=.66
links.new(attr.outputs['Vector'],noise.inputs['Vector'])
ramp=nodes.new('ShaderNodeValToRGB');r=ramp.color_ramp;r.elements.remove(r.elements[1]);r.elements[0].position=.30;r.elements[0].color=(.035,.045,.065,1)
for pos,c in [(.41,(.055,.068,.09,1)),(.46,(.24,.28,.35,1)),(.51,(.50,.53,.59,1)),(.63,(.70,.70,.71,1)),(.78,(.81,.79,.76,1))]:r.elements.new(pos).color=c
links.new(noise.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],bs.inputs['Base Color'])
cream,_=material('Luna • warm ivory',(.82,.77,.68),.6)
pink,_=material('Luna • soft ear blush',(.53,.25,.29),.64)
nose,nosebs=material('Luna • charcoal nose',(.025,.032,.045),.28);nosebs.inputs['Coat Weight'].default_value=.22
eye,eyebs=material('Luna • porcelain eye',(.86,.88,.86),.22);eyebs.inputs['Coat Weight'].default_value=.4
iris,irisbs=material('Luna • blue eyes',(.035,.30,.67),.22);irisbs.inputs['Coat Weight'].default_value=.5
pupil,pupilbs=material('Luna • deep pupil',(.004,.009,.018),.14);pupilbs.inputs['Coat Weight'].default_value=.6
collar,_=material('Luna • teal collar',(.025,.29,.31),.38)
tag,tagbs=material('Luna • champagne tag',(.72,.43,.14),.28);tagbs.inputs['Metallic'].default_value=.65
tongue,_=material('Luna • rose tongue',(.65,.22,.28),.52)
ear_changes=[]
outer_bounds=[]
for ear in scene.objects:
 if ear.type=='MESH' and ear.name.startswith('Upright ear'):
  v=np.array([tuple(x.co) for x in ear.data.shape_keys.key_blocks[0].data]);outer_bounds.append((v.mean(axis=0),v.min(axis=0),v.max(axis=0)))
for ob in scene.objects:
 if ob.type!='MESH' or not ob.name.endswith(' movement'):continue
 name=ob.name[:-9]
 attr=ob.data.attributes.get('luna_rest') or ob.data.attributes.new('luna_rest','FLOAT_VECTOR','POINT')
 for v,item in zip(ob.data.vertices,attr.data):item.vector=v.co
 chosen=coat
 if name.startswith(('Chest bib','Short muzzle','Muzzle jowl')):chosen=cream
 elif name.startswith('Inner ear'):chosen=pink
 elif name.startswith(('Nose','Mouth smile')):chosen=nose
 elif name.startswith('Eye white'):chosen=eye
 elif name.startswith('Blue iris'):chosen=iris
 elif name.startswith('Pupil'):chosen=pupil
 elif name.startswith(('Collar','V41 Luna harness')):chosen=collar
 elif name.startswith('Luna tag'):chosen=tag
 elif name.startswith('Tongue'):chosen=tongue
 elif name.startswith('Expressive brow'):chosen=coat
 ob.data.materials.clear();ob.data.materials.append(chosen)
 for poly in ob.data.polygons:poly.use_smooth=True
 # Bat-ear silhouette: taller with a gently tapered crown. Transfer each cached
 # pose's affine motion onto the new rest shape instead of stretching its path.
 if name.startswith(('Upright ear','Inner ear')):
  keys=ob.data.shape_keys.key_blocks if ob.data.shape_keys else []
  base=np.array([tuple(v.co) for v in (keys[0].data if keys else ob.data.vertices)])
  centre,lo,hi=min(outer_bounds,key=lambda item:abs(item[0][1]-base.mean(axis=0)[1]))
  inner=name.startswith('Inner');height=(hi[2]-lo[2])*1.22;bottom=lo[2]-.06
  if inner:bottom+=height*.12;height*=.76
  new=[];faces=[];rings=15;around=32
  for ring in range(rings):
   u=ring/(rings-1);profile=math.sin(math.pi*u)**.6
   half_width=(hi[1]-lo[1])*.35*(.70 if inner else 1)*profile*(1-.28*u)
   depth=(.012 if inner else (hi[0]-lo[0])*.48)*math.sin(math.pi*u)**.5
   for j in range(around):
    theta=2*math.pi*j/around
    new.append((centre[0]+((hi[0]-lo[0])*.6+.02 if inner else 0)+depth*math.sin(theta)-.025*u,centre[1]+half_width*math.cos(theta),bottom+height*u))
  for ring in range(rings-1):
   for j in range(around):
    x=ring*around+j;y=ring*around+(j+1)%around;faces.append((x,y,y+around,x+around))
  new=np.array(new)
  design=np.column_stack([base,np.ones(len(base))])
  poses=[]
  for key in keys:
   target=np.array([tuple(v.co) for v in key.data]);affine=np.linalg.lstsq(design,target,rcond=None)[0]
   poses.append((key.name,np.column_stack([new,np.ones(len(new))])@affine))
  action=ob.data.shape_keys.animation_data.action if ob.data.shape_keys and ob.data.shape_keys.animation_data else None
  slot=ob.data.shape_keys.animation_data.action_slot if action else None
  data=bpy.data.meshes.new(name+' sculpted bat ear');data.from_pydata(new.tolist(),[],faces);data.materials.append(chosen);ob.data=data
  for keyname,coords in poses:
   key=ob.shape_key_add(name=keyname)
   for vertex,co in zip(key.data,coords):vertex.co=co
  if action:
   data.shape_keys.animation_data_create();data.shape_keys.animation_data.action=action;data.shape_keys.animation_data.action_slot=slot
  attr=data.attributes.new('luna_rest','FLOAT_VECTOR','POINT')
  for vertex,item in zip(data.vertices,attr.data):item.vector=vertex.co
  for poly in data.polygons:poly.use_smooth=True
  ear_changes.append(name)
 # Smooth silhouette without a high-density viewport burden.
 if not ob.modifiers and not name.startswith(('Paw','Blue iris','Pupil','V41 Luna harness')):
  mod=ob.modifiers.new('Presentation surface','SUBSURF');mod.levels=1;mod.render_levels=2
for ob in scene.objects:
 if ob.name.startswith(('Upper eyelid','Lower eyelid')):
  ob.data.materials.clear();ob.data.materials.append(coat)
  attr=ob.data.attributes.get('luna_rest') or ob.data.attributes.new('luna_rest','FLOAT_VECTOR','POINT')
  for v,item in zip(ob.data.vertices,attr.data):item.vector=ob.matrix_world@v.co
floor=scene.objects['Contact plane'];floor.data.materials.clear();floormat,_=material('Studio • warm sand',(.48,.39,.32),.8);floor.data.materials.append(floormat)
scene.world=scene.world.copy();scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.27,.36,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
lights=[ob for ob in scene.objects if ob.type=='LIGHT']
for ob,location,energy,color,size in zip(lights,[(2,-4,5),(-3,2,4)],[650,900],[(1,.85,.70),(.72,.84,1)],[4,3]):
 ob.location=location;ob.data.energy=energy;ob.data.color=color;ob.data.size=size;ob.rotation_euler=(Vector((0,0,1))-ob.location).to_track_quat('-Z','Y').to_euler()
ld=bpy.data.lights.new('Studio • soft face fill','AREA');ld.energy=140;ld.size=3
fill=bpy.data.objects.new('Studio • soft face fill',ld);scene.collection.objects.link(fill);fill.location=(4,-1,3);fill.rotation_euler=(Vector((0,0,1.2))-fill.location).to_track_quat('-Z','Y').to_euler()
scene.camera.data.ortho_scale=3.65
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.name='Luna_Visual_Movement_Study';scene.render.fps=24
if bpy.context.screen:
 for area in bpy.context.screen.areas:
  if area.type=='VIEW_3D':
   area.spaces.active.shading.type='MATERIAL';area.spaces.active.shading.use_scene_lights=True;area.spaces.active.shading.use_scene_world=True
note=bpy.data.texts.new('READ_ME_VISUAL_PASS');note.write('LUNA VISUAL + MOVEMENT STUDY\n18 seconds; Space to play. A separate appearance proposal. Blue eyes, rest-coordinate silver merle, bat-ear silhouette, warm studio. Earlier movement and source files remain preserved.\n')
sourcecode=bpy.data.texts.new('REBUILD_VISUAL.py');sourcecode.write(Path(__file__).read_text())
a.output.parent.mkdir(parents=True,exist_ok=True);a.render_dir.mkdir(parents=True,exist_ok=True)
scene.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(a.output),compress=True)
assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
for frame in [193,312,409]:
 scene.frame_set(frame);scene.render.image_settings.file_format='PNG';scene.render.filepath=str(a.render_dir/('look_%03d.png'%frame));bpy.ops.render.render(write_still=True);print('LOOK_RENDERED',frame,flush=True)
print('VISUAL_PASS_SAVED',json.dumps({'sourceHash':digest,'earMeshes':ear_changes,'frames':432}),flush=True)
