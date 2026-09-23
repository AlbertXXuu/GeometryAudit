"""Targeted data, provenance, raw/display and export integrity verification."""
import hashlib
import json
from pathlib import Path
import numpy as np
import trimesh

ROOT=Path(__file__).resolve().parent
def digest(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

selection=json.loads((ROOT/'selection.json').read_text())
run=ROOT/'run-518'
config=json.loads((run/'config.json').read_text())
assert digest(ROOT/'selection.json')==config['selection_sha256']==(ROOT/'selection.sha256').read_text().strip()
assert selection['frozen_utc'] < config['started_utc']
assert digest(ROOT/'provenance/PROTOCOL-GEO-P0.2.md')==config['protocol_sha256']
assert len(selection['frames'])==4 and len(set(config['input_order']))==4
assert json.loads((run/'result.json').read_text())['status']=='success'
count=0
for frame in selection['frames']:
    assert digest(ROOT/'inputs'/frame['file'])==frame['sha256']
    assert abs(frame['rgb_target_delta_s'])<=.05 and abs(frame['gt_rgb_delta_s'])<=.02
    i=frame['index']
    with np.load(run/f'raw-view-{i:02d}.npz',allow_pickle=False) as raw, np.load(run/f'view-{i:02d}.npz',allow_pickle=False) as display:
        assert raw['camera_poses'].shape==(1,4,4)
        assert raw['conf'].shape==(1,392,518)
        assert 'mask' not in raw.files
        for key in ['conf','camera_poses','intrinsics','depth_z','pts3d']:
            assert np.isfinite(raw[key]).all()
        assert (raw['depth_z']>0).all()
        assert np.array_equal(raw['conf'],display['conf'])
        assert np.array_equal(raw['camera_poses'],display['camera_poses'])
        mask=display['mask'][0,...,0].astype(bool)
        assert mask.any() and np.array_equal(raw['pts3d'][0][mask],display['pts3d'][0][mask])
        assert (display['pts3d'][0][~mask]==0).all()
        count+=int(mask.sum())
scene=trimesh.load(run/'scene.glb')
assert sum(len(g.vertices) for g in scene.geometry.values())==count
pose=json.loads((ROOT/'pose-comparison.json').read_text())
assert len(pose['pairs'])==6 and pose['selection_sha256']==config['selection_sha256']
assert sum(p['translation_direction_deg'] is not None for p in pose['pairs'])==5
assert all(p['translation_direction_deg'] is None for p in pose['pairs'] if p['reference_baseline_m']<.05)
budget=json.loads((ROOT/'logs/model-budget.json').read_text())
assert budget['status']=='completed' and budget['child_process_wall_s']<300
print(f'PASS: frozen pre-inference selection/protocol; four raw/display archives; {count} GLB points; six R errors, five eligible t errors; model activity upper bound below 300s')
