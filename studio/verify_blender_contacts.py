"""Blender integration fixture: actual armature + skinned limbs + sole vertices.

No approved Luna mesh is present. Rendered geometry is a diagnostic fixture.
Run: blender --background --python studio/verify_blender_contacts.py -- OUTPUT
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import math
import bpy
from mathutils import Vector
from studio.locomotion import Walk, LEGS, pose
from studio.blender_contacts import validate_mapping, apply_pose


def build_fixture(walk):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.object.armature_add()
    rig = bpy.context.object
    rig.name = 'CONTACT_TEST_ONLY'
    bpy.ops.object.mode_set(mode='EDIT')
    rig.data.edit_bones.remove(rig.data.edit_bones[0])
    rest = pose(0, walk)
    root = rig.data.edit_bones.new('root')
    root.head = rest['root']; root.tail = Vector(root.head)+Vector((.1,0,0))
    mapping = {'root':'root','legs':{}}
    for name, leg in rest['legs'].items():
        mapping['legs'][name] = {}
        parent = root
        for role, start, end in [('upper',leg['hip'],leg['knee']),('lower',leg['knee'],leg['foot']),
                                ('foot',leg['foot'],(leg['foot'][0]+.1,leg['foot'][1],leg['foot'][2]))]:
            bone = rig.data.edit_bones.new(name+'.'+role)
            bone.head, bone.tail = start, end
            bone.parent = parent
            bone.use_connect = role != 'upper'
            mapping['legs'][name][role] = bone.name
            parent = bone
    bpy.ops.object.mode_set(mode='OBJECT')
    meshes = {}; soles = {}
    for name, leg in rest['legs'].items():
        vertices = []; faces = []; weights = []
        roles = mapping['legs'][name]
        # Continuous limb topology across the knee, with blended skin weights.
        hip, knee, foot = map(Vector, [leg['hip'],leg['knee'],leg['foot']])
        centres = [hip, hip.lerp(knee,.5), knee, knee.lerp(foot,.5), foot+Vector((0,0,.055))]
        for ring, centre in enumerate(centres):
            for i in range(12):
                angle = 2*math.pi*i/12
                vertices.append(tuple(centre+Vector((.045*math.cos(angle),.045*math.sin(angle),0))))
                weights.append({roles['upper']:1} if ring<2 else
                               {roles['upper']:.5,roles['lower']:.5} if ring==2 else
                               {roles['lower']:1} if ring==3 else {roles['foot']:1})
        for ring in range(4):
            for i in range(12):
                a=ring*12+i; b=ring*12+(i+1)%12
                faces.append((a,b,b+12,a+12))
        # Sole is an actual evaluated mesh vertex, not a target empty.
        sole = len(vertices)
        vertices.append(tuple(foot)); weights.append({roles['foot']:1})
        for i in range(12): faces.append((48+i,48+(i+1)%12,sole))
        mesh = bpy.data.meshes.new(name+'.skin'); mesh.from_pydata(vertices,[],faces); mesh.update()
        ob = bpy.data.objects.new(name+'.skin', mesh); bpy.context.collection.objects.link(ob)
        for bone in roles.values(): ob.vertex_groups.new(name=bone)
        for index, weight in enumerate(weights):
            for bone, value in weight.items(): ob.vertex_groups[bone].add([index],value,'REPLACE')
        modifier=ob.modifiers.new('Actual skin deformation','ARMATURE'); modifier.object=rig
        mat=bpy.data.materials.new(name); mat.diffuse_color=(.08,.45,.75,1) if 'front' in name else (.95,.42,.13,1)
        ob.data.materials.append(mat)
        meshes[name]=ob; soles[name]=sole
    validate_mapping(rig,mapping,walk)
    return rig,mapping,meshes,soles


def main(output):
    output.mkdir(parents=True,exist_ok=True)
    walk=Walk(); rig,mapping,meshes,soles=build_fixture(walk)
    scene=bpy.context.scene
    scene.render.fps=24
    scene.frame_start=1;scene.frame_end=361
    for bone in rig.pose.bones: bone.rotation_mode='QUATERNION'
    drift=joint_error=sole_error=0.0; minimum_z=math.inf; previous={}
    snapshots={0,9,18,27}
    for frame in range(361):
        expected=pose(frame/24,walk)
        apply_pose(rig,mapping,frame+1,expected)
        for bone in rig.pose.bones:
            bone.keyframe_insert(data_path='location',frame=frame+1)
            bone.keyframe_insert(data_path='rotation_quaternion',frame=frame+1)
            bone.keyframe_insert(data_path='scale',frame=frame+1)
        depsgraph=bpy.context.evaluated_depsgraph_get()
        for name, leg in expected['legs'].items():
            roles=mapping['legs'][name]
            for role, start, end in [('upper',leg['hip'],leg['knee']),('lower',leg['knee'],leg['foot'])]:
                bone=rig.pose.bones[roles[role]]
                joint_error=max(joint_error,(bone.head-Vector(start)).length,(bone.tail-Vector(end)).length)
            evaluated=meshes[name].evaluated_get(depsgraph)
            mesh=evaluated.to_mesh()
            foot=evaluated.matrix_world @ mesh.vertices[soles[name]].co
            minimum_z=min(minimum_z,min((evaluated.matrix_world @ v.co).z for v in mesh.vertices))
            sole_error=max(sole_error,(foot-Vector(leg['foot'])).length)
            before=previous.get(name)
            if before and before[0]==leg['cycle'] and before[1]==leg['state']=='stance':
                drift=max(drift,(foot-before[2]).length)
            previous[name]=(leg['cycle'],leg['state'],foot.copy())
            evaluated.to_mesh_clear()
        if frame in snapshots:
            # Save compact evaluated-geometry snapshots for a diagnostic render.
            for name, ob in meshes.items():
                evaluated=ob.evaluated_get(depsgraph)
                mesh=bpy.data.meshes.new_from_object(evaluated)
                copy=bpy.data.objects.new('POSE_%02d_'%frame+name,mesh)
                bpy.context.collection.objects.link(copy)
                copy.location.y += (frame//9)*1.05
                copy.location.x -= expected['root'][0]
    report={'kind':'skinned-fixture-only','blender':bpy.app.version_string,'framesChecked':361,
            'maxBoneEndpointError':joint_error,'maxEvaluatedSoleError':sole_error,
            'maxEvaluatedStanceDrift':drift,'minimumEvaluatedMeshHeight':minimum_z,
            'approvedCharacterUsed':False}
    (output/'blender-contact-report.json').write_text(json.dumps(report,indent=2))
    print('CONTACT_MEASUREMENTS',json.dumps(report),flush=True)
    assert joint_error<1e-5, report
    assert sole_error<1e-5, report
    assert drift<1e-5, report
    assert minimum_z>-1e-5, report
    for ob in meshes.values(): ob.hide_render=True
    rig.hide_render=True
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005))
    bpy.context.object.name='Diagnostic floor'
    scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=12; scene.cycles.use_denoising=False
    for layer in scene.view_layers:
        layer.cycles.use_denoising=False
    scene.render.resolution_x=900;scene.render.resolution_y=650;scene.render.resolution_percentage=100
    scene.world.color=(.25,.25,.25)
    bpy.ops.object.light_add(type='AREA',location=(1,-2,6));bpy.context.object.data.energy=800;bpy.context.object.data.size=5
    bpy.ops.object.camera_add(location=(3,-5,4.5));camera=bpy.context.object
    camera.rotation_euler=(Vector((0,1.5,.25))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO';camera.data.ortho_scale=5.8;scene.camera=camera
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(output/'contact-fixture.png')
    bpy.ops.render.render(write_still=True)
    for ob in list(bpy.data.objects):
        if ob.name.startswith('POSE_'): ob.hide_render=True;ob.hide_viewport=True
    for ob in meshes.values(): ob.hide_render=False
    scene.frame_set(1)
    camera.location=(3,-4,2.5)
    camera.rotation_euler=(Vector((1.8,0,.25))-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.ortho_scale=5.8
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'contact-fixture.blend'))
    print('LUNA_BLENDER_CONTACT_PASS',json.dumps(report),flush=True)


if __name__=='__main__':
    argv=sys.argv[sys.argv.index('--')+1:]
    main(Path(argv[0]).resolve())
