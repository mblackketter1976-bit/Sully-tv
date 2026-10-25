import sys
import math
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from studio.locomotion import Walk, pose, benchmark, LEGS

class TestLunaMotion(unittest.TestCase):
    def test_fifteen_second_world_contacts_and_connected_limbs(self):
        result = benchmark()
        self.assertEqual(result['sampleCount'], 361)
        self.assertLessEqual(result['maxStanceDrift'], 1e-12)
        self.assertLess(result['maxSegmentLengthError'], 1e-12)
        self.assertGreaterEqual(result['minimumFootHeight'], 0)
        self.assertAlmostEqual(result['frames'][-1]['root'][0], 3.75)

    def test_each_paw_lifts_and_plants(self):
        frames = benchmark(seconds=2.4, fps=120)['frames']
        for name in LEGS:
            feet = [p['legs'][name] for p in frames]
            self.assertEqual({p['state'] for p in feet}, {'stance', 'swing'})
            self.assertTrue(any(p['foot'][2] > 0.07 for p in feet))
            self.assertTrue(all(p['foot'][2] == 0 for p in feet if p['state'] == 'stance'))

    def test_no_teleport_at_liftoff_or_touchdown(self):
        walk = Walk()
        for name, (_, _, offset, _) in LEGS.items():
            for phase in [walk.stance_fraction, 1.0, 2.0]:
                time = (phase-offset)*walk.period
                left = pose(time-1e-7)['legs'][name]['foot']
                right = pose(time+1e-7)['legs'][name]['foot']
                self.assertLess(math.dist(left, right), 1e-6)

    def test_unsupported_motion_fails_instead_of_stretching(self):
        with self.assertRaises(ValueError): pose(0, Walk(hip_height=2))

    def test_invalid_parameters_rejected(self):
        for parameters in [{'period':0}, {'stance_fraction':1}, {'speed':float('nan')}, {'lift':-1}]:
            with self.assertRaises(ValueError): Walk(**parameters)
        with self.assertRaises(ValueError): pose(float('inf'))

    def test_repeatable_stride_translates_without_changing_shape(self):
        walk = Walk()
        a, b = pose(0.123), pose(0.123+walk.period)
        for name in LEGS:
            for joint in ['hip','knee','foot']:
                pa, pb = a['legs'][name][joint], b['legs'][name][joint]
                self.assertAlmostEqual(pb[0]-pa[0], walk.speed*walk.period)
                self.assertAlmostEqual(pb[1], pa[1])
                self.assertAlmostEqual(pb[2], pa[2])
