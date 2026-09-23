"""Check provenance bytes and real output integrity; does not assert geometric accuracy."""
import argparse
import hashlib
import json
import os
from pathlib import Path

ARTIFACTS = Path(os.environ.get("GEOMETRY_AUDIT_ARTIFACTS", str(Path(__file__).resolve().parents[2] / ".local"))).resolve()
ROOT = ARTIFACTS / "round1"


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputs-only', action='store_true')
    parser.add_argument('--run', default='run-02')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'inputs-manifest.json').read_text())
    for item in manifest['files']:
        assert sha256(ROOT / 'inputs' / item['file']) == item['sha256'], item['file']
    metadata = json.loads((ROOT / 'model-metadata.json').read_text())
    weight_info = next(s for s in metadata['siblings'] if s['rfilename'] == 'model.safetensors')
    assert (ROOT / 'weights/model.safetensors').stat().st_size == weight_info['size']
    assert sha256(ROOT / 'weights/model.safetensors') == weight_info['lfs']['sha256']
    if args.inputs_only:
        print('PASS: exact input and upstream model LFS hashes')
        return
    import numpy as np
    import trimesh
    run = ROOT / args.run
    result = json.loads((run / 'result.json').read_text())
    assert result['status'] == 'success'
    files = sorted(run.glob('view-*.npz'))
    assert len(files) == len(manifest['files']) == 2
    point_count = 0
    for file in files:
        with np.load(file, allow_pickle=False) as a:
            assert a['camera_poses'].shape == (1, 4, 4)
            assert np.allclose(a['camera_poses'][0, 3], [0, 0, 0, 1])
            assert a['intrinsics'].shape == (1, 3, 3)
            assert np.isfinite(a['camera_poses']).all() and np.isfinite(a['intrinsics']).all()
            assert np.isfinite(a['conf']).all()
            mask = a['mask'][0, ..., 0].astype(bool)
            assert mask.any()
            assert np.isfinite(a['pts3d'][0][mask]).all()
            assert (a['depth_z'][0, ..., 0][mask] > 0).all()
            assert a['conf'].shape[1:] == mask.shape
            point_count += int(mask.sum())
            with np.load(file.with_name('raw-' + file.name), allow_pickle=False) as raw:
                assert 'mask' not in raw.files
                assert np.array_equal(a['conf'], raw['conf'])
                assert np.allclose(a['pts3d'][0][mask], raw['pts3d'][0][mask])
    scene = trimesh.load(run / 'scene.glb')
    exported_points = sum(len(g.vertices) for g in scene.geometry.values())
    assert exported_points == point_count, (exported_points, point_count)
    assert (run / 'scene.rrd').stat().st_size > 0
    print(f'PASS: 2 view archives, finite cameras/confidence/valid geometry, {point_count} GLB points; accuracy not evaluated')


if __name__ == '__main__':
    main()
