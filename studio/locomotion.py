"""Renderer-independent quadruped contact benchmark. Metres, seconds, Z up.

Mechanical prototype only: no character mesh, performance, or visual approval.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Walk:
    speed: float = 0.25
    period: float = 1.2
    stance_fraction: float = 0.68
    lift: float = 0.075
    hip_height: float = 0.55
    upper: float = 0.32
    lower: float = 0.33
    bob: float = 0.008

    def __post_init__(self):
        values = (self.speed, self.period, self.stance_fraction, self.lift,
                  self.hip_height, self.upper, self.lower, self.bob)
        if not all(math.isfinite(v) for v in values):
            raise ValueError('Finite walk parameters required')
        if min(self.speed, self.period, self.lift, self.hip_height, self.upper, self.lower) <= 0:
            raise ValueError('Positive walk dimensions required')
        if not 0.5 < self.stance_fraction < 1 or self.bob < 0:
            raise ValueError('Invalid contact timing or bob')


# Four-beat timing is a configurable prototype, not a captured Luna performance.
LEGS = {
    'hind_left': (-0.35, -0.23, 0.0, 1),
    'front_left': (0.35, -0.23, 0.25, -1),
    'hind_right': (-0.35, 0.23, 0.5, 1),
    'front_right': (0.35, 0.23, 0.75, -1),
}


def solve_leg(hip, foot, upper, lower, bend):
    """Exact two-link solution in a sagittal plane; never stretch to hide failure."""
    dx, dz = foot[0] - hip[0], foot[2] - hip[2]
    distance = math.hypot(dx, dz)
    if abs(hip[1] - foot[1]) > 1e-9 or not abs(upper-lower) < distance < upper+lower:
        raise ValueError('Unreachable foot contact')
    ux, uz = dx/distance, dz/distance
    along = (upper*upper - lower*lower + distance*distance) / (2*distance)
    height = math.sqrt(max(0.0, upper*upper - along*along))
    return (hip[0]+along*ux-bend*height*uz, hip[1], hip[2]+along*uz+bend*height*ux)


def pose(time, walk=Walk()):
    if not math.isfinite(time):
        raise ValueError('Finite time required')
    root_x = walk.speed*time
    root_z = walk.hip_height + walk.bob*math.cos(4*math.pi*time/walk.period)
    legs = {}
    for name, (anchor_x, anchor_y, offset, bend) in LEGS.items():
        phase = time/walk.period + offset
        cycle = math.floor(phase)
        fraction = phase-cycle
        touchdown_time = (cycle-offset)*walk.period
        # Stance target is a fixed WORLD point while the hip travels past it.
        contact_x = walk.speed*touchdown_time + anchor_x + walk.speed*walk.period*walk.stance_fraction/2
        if fraction < walk.stance_fraction:
            foot_x, foot_z = contact_x, 0.0
            state = 'stance'
        else:
            swing = (fraction-walk.stance_fraction)/(1-walk.stance_fraction)
            smooth = swing**3*(10+swing*(-15+6*swing))
            foot_x = contact_x + walk.speed*walk.period*smooth
            foot_z = walk.lift*math.sin(math.pi*swing)**2
            state = 'swing'
        hip = (root_x+anchor_x, anchor_y, root_z)
        foot = (foot_x, anchor_y, foot_z)
        knee = solve_leg(hip, foot, walk.upper, walk.lower, bend)
        legs[name] = {'hip': hip, 'knee': knee, 'foot': foot, 'state': state, 'cycle': cycle}
    return {'time': time, 'root': (root_x, 0.0, root_z), 'legs': legs}


def benchmark(seconds=15, fps=24, walk=Walk()):
    """Measure contact drift and segment invariance over sampled world poses."""
    if seconds <= 0 or fps <= 0:
        raise ValueError('Positive duration and frame rate required')
    frames = [pose(frame/fps, walk) for frame in range(round(seconds*fps)+1)]
    max_drift = max_error = 0.0
    minimum_clearance = math.inf
    for i, frame in enumerate(frames):
        for name, leg in frame['legs'].items():
            max_error = max(max_error, abs(math.dist(leg['hip'], leg['knee'])-walk.upper),
                            abs(math.dist(leg['knee'], leg['foot'])-walk.lower))
            minimum_clearance = min(minimum_clearance, leg['foot'][2])
            if i:
                before = frames[i-1]['legs'][name]
                if before['state'] == leg['state'] == 'stance' and before['cycle'] == leg['cycle']:
                    max_drift = max(max_drift, math.dist(before['foot'], leg['foot']))
    return {'schema': 1, 'kind': 'mechanics-only', 'units': 'metres', 'fps': fps,
            'durationSeconds': seconds, 'sampleCount': len(frames),
            'maxStanceDrift': max_drift, 'maxSegmentLengthError': max_error,
            'minimumFootHeight': minimum_clearance, 'frames': frames}
