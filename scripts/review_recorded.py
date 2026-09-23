"""Recompute the recorded TUM relative poses without images, weights or a GPU."""
import argparse
import itertools
import json
from pathlib import Path

import numpy as np

PROJECT = Path(__file__).resolve().parents[1]


def camera_matrix(row):
    """TUM timestamp xyz xyzw -> optical camera-to-world matrix."""
    values = np.asarray(row, dtype=np.float64)
    if values.shape != (8,) or not np.isfinite(values).all():
        raise ValueError('Expected eight finite TUM row values')
    q = values[4:8]
    norm = np.linalg.norm(q)
    if norm < 1e-12:
        raise ValueError('Zero quaternion')
    x, y, z, w = q / norm
    cross = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    result = np.eye(4)
    result[:3, :3] = np.eye(3) + 2 * w * cross + 2 * cross @ cross
    result[:3, 3] = values[1:4]
    return result


def validate_pose(matrix):
    matrix = np.asarray(matrix, dtype=np.float64)
    if matrix.shape != (4, 4) or not np.isfinite(matrix).all():
        raise ValueError('Expected a finite 4x4 camera pose')
    if not np.allclose(matrix[3], [0, 0, 0, 1], atol=1e-6, rtol=0):
        raise ValueError('Invalid homogeneous row')
    rotation = matrix[:3, :3]
    if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-3, rtol=0) or abs(np.linalg.det(rotation) - 1) >= 1e-3:
        raise ValueError('Invalid rotation matrix')
    return matrix


def compare_poses(references, predictions):
    if len(references) != len(predictions) or len(references) < 2:
        raise ValueError('Matching reference/prediction lists with at least two poses required')
    references = [validate_pose(t) for t in references]
    predictions = [validate_pose(t) for t in predictions]
    pairs = []
    for i, j in itertools.combinations(range(len(references)), 2):
        reference = np.linalg.solve(references[j], references[i])
        predicted = np.linalg.solve(predictions[j], predictions[i])
        baseline = float(np.linalg.norm(reference[:3, 3]))
        predicted_baseline = float(np.linalg.norm(predicted[:3, 3]))
        cosine = (np.trace(predicted[:3, :3] @ reference[:3, :3].T) - 1) / 2
        rotation = float(np.degrees(np.arccos(np.clip(cosine, -1, 1))))
        translation, reason = None, None
        if baseline < 0.05:
            reason = 'reference-baseline-below-0.05m'
        elif predicted_baseline <= 1e-6:
            reason = 'predicted-translation-near-zero-at-1e-6-model-metres'
        else:
            cosine = np.dot(predicted[:3, 3], reference[:3, 3]) / (predicted_baseline * baseline)
            translation = float(np.degrees(np.arccos(np.clip(cosine, -1, 1))))
        pairs.append({'pair_id': f'{i}-{j}', 'reference_baseline_m': baseline,
                      'rotation_deg': rotation, 'translation_direction_deg': translation,
                      'translation_unavailable_reason': reason})
    return pairs


def review(records=PROJECT / 'records/tum'):
    selection = json.loads((records / 'selection.json').read_text(encoding='utf-8'))
    result = json.loads((records / 'result.json').read_text(encoding='utf-8'))
    accepted = json.loads((records / 'pose-comparison.json').read_text(encoding='utf-8'))
    references = [camera_matrix(f['gt_row_timestamp_xyz_xyzw']) for f in selection['frames']]
    for matrix, frame in zip(references, selection['frames']):
        if not np.allclose(matrix, frame['gt_camera_to_world'], atol=1e-12, rtol=0):
            raise ValueError('Quaternion/c2w mismatch')
    predictions = [np.asarray(v['camera_pose'], dtype=np.float64)[0] for v in result['views']]
    pairs = compare_poses(references, predictions)
    if len(pairs) != len(accepted['pairs']):
        raise ValueError('Pair count differs from accepted report')
    for actual, expected in zip(pairs, accepted['pairs']):
        for key in ['pair_id', 'translation_unavailable_reason']:
            if actual[key] != expected[key]:
                raise ValueError(f'Mismatched {key} for {actual["pair_id"]}')
        for key in ['reference_baseline_m', 'rotation_deg', 'translation_direction_deg']:
            a, b = actual[key], expected[key]
            if (a is None) != (b is None) or (a is not None and abs(a - b) > 1e-8):
                raise ValueError(f'Mismatched {key} for {actual["pair_id"]}: {a} vs {b}')
    return {'passed': True, 'method': 'Recorded model cameras; independent xyzw and solve(Tj,Ti) calculation',
            'rotation_denominator': len(pairs), 'translation_denominator': sum(p['translation_direction_deg'] is not None for p in pairs),
            'research_validation_scenes': 0, 'pairs': pairs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional new JSON file; existing files are preserved')
    args = parser.parse_args()
    result = review()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as stream:
            json.dump(result, stream, indent=2)
            stream.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
