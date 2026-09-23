import importlib.util
from pathlib import Path
import unittest

import numpy as np

SOURCE = Path(__file__).resolve().parents[1] / 'scripts/review_recorded.py'
SPEC = importlib.util.spec_from_file_location('review_recorded', SOURCE)
reviewer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reviewer)


def translated(x):
    pose = np.eye(4)
    pose[0, 3] = x
    return pose


class PoseContract(unittest.TestCase):
    def test_recorded_results_and_null_denominator(self):
        result = reviewer.review()
        self.assertEqual(result['rotation_denominator'], 6)
        self.assertEqual(result['translation_denominator'], 5)
        pair = next(p for p in result['pairs'] if p['pair_id'] == '1-2')
        self.assertIsNone(pair['translation_direction_deg'])

    def test_reversed_translation_is_180_not_zero(self):
        pair = reviewer.compare_poses([translated(0), translated(1)], [translated(0), translated(-1)])[0]
        self.assertAlmostEqual(pair['translation_direction_deg'], 180)

    def test_short_reference_baseline_is_unavailable(self):
        pair = reviewer.compare_poses([translated(0), translated(.049)], [translated(0), translated(1)])[0]
        self.assertIsNone(pair['translation_direction_deg'])

    def test_threshold_is_inclusive(self):
        pair = reviewer.compare_poses([translated(0), translated(.05)], [translated(0), translated(1)])[0]
        self.assertAlmostEqual(pair['translation_direction_deg'], 0)

    def test_zero_predicted_translation_is_unavailable(self):
        pair = reviewer.compare_poses([translated(0), translated(1)], [translated(0), translated(0)])[0]
        self.assertEqual(pair['translation_unavailable_reason'], 'predicted-translation-near-zero-at-1e-6-model-metres')

    def test_xyzw_quarter_turn(self):
        pose = reviewer.camera_matrix([0, 1, 2, 3, 0, 0, np.sqrt(.5), np.sqrt(.5)])
        np.testing.assert_allclose(pose[:3, :3] @ [1, 0, 0], [0, 1, 0], atol=1e-12)
        np.testing.assert_allclose(pose[:3, 3], [1, 2, 3])

    def test_zero_quaternion_rejected(self):
        with self.assertRaises(ValueError):
            reviewer.camera_matrix([0] * 8)

    def test_reflection_rejected(self):
        pose = np.eye(4)
        pose[0, 0] = -1
        with self.assertRaises(ValueError):
            reviewer.compare_poses([np.eye(4), pose], [np.eye(4), np.eye(4)])


if __name__ == '__main__':
    unittest.main()
