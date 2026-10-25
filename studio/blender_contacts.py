"""Apply world-contact poses to an explicitly mapped Blender armature.

Run inside Blender. This adapter does not alter or generate character artwork.
Bone mappings must be approved for the actual rig; never guess by bone name.
"""
import math
import bpy
from mathutils import Matrix, Vector
from studio.locomotion import LEGS


def bone_matrix(start, end):
    direction = Vector(end)-Vector(start)
    if direction.length < 1e-8:
        raise ValueError('Bone direction must have length')
    return Matrix.Translation(Vector(start)) @ direction.to_track_quat('Y', 'Z').to_matrix().to_4x4()


def validate_mapping(rig, mapping, walk):
    if rig.type != 'ARMATURE' or set(mapping) != {'root', 'legs'} or set(mapping['legs']) != set(LEGS):
        raise ValueError('Explicit root and four-leg armature mapping required')
    if rig.matrix_world != Matrix.Identity(4):
        raise ValueError('Apply armature object transforms before using world-contact adapter')
    names = [mapping['root']]
    for names_for_leg in mapping['legs'].values():
        if set(names_for_leg) != {'upper', 'lower', 'foot'}:
            raise ValueError('Upper/lower/foot mapping required for each leg')
        names.extend(names_for_leg.values())
    if len(names) != len(set(names)):
        raise ValueError('Each role must map to a distinct bone')
    for name in names:
        if name not in rig.pose.bones:
            raise ValueError('Mapped bone is missing: '+name)
        if rig.pose.bones[name].constraints:
            raise ValueError('Bake adapter requires unconstrained mapped bones')
    for leg in mapping['legs'].values():
        for role, length in [('upper', walk.upper), ('lower', walk.lower)]:
            if not math.isclose(rig.data.bones[leg[role]].length, length, abs_tol=1e-5):
                raise ValueError('Bone length does not match contact configuration')


def apply_pose(rig, mapping, frame, pose):
    """Set actual bone matrices; keyframe baking is deliberately separate."""
    bpy.context.scene.frame_set(frame)
    root = pose['root']
    rig.pose.bones[mapping['root']].matrix = bone_matrix(root, (root[0]+.1, root[1], root[2]))
    bpy.context.view_layer.update()
    for name, leg in pose['legs'].items():
        roles = mapping['legs'][name]
        for role, start, end in [('upper',leg['hip'],leg['knee']),('lower',leg['knee'],leg['foot']),
                                 ('foot',leg['foot'],(leg['foot'][0]+.1,leg['foot'][1],leg['foot'][2]))]:
            rig.pose.bones[roles[role]].matrix = bone_matrix(start, end)
            bpy.context.view_layer.update()
