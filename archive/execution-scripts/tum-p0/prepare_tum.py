"""Fetch one official sequence under the assigned byte cap and freeze four frames before inference."""
import hashlib
import json
from pathlib import Path
import ssl
import tarfile
import time
from datetime import datetime, timezone
import urllib.request

import certifi
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[3]
TMP = WORKSPACE / '.workspace/tmp/geometry-audit/tum-data'
URL = 'https://cvg.cit.tum.de/rgbd/dataset/freiburg1/rgbd_dataset_freiburg1_xyz.tgz'
BYTE_CAP = 600000000
DEADLINE = datetime(2026, 9, 21, 19, 55, 27, tzinfo=timezone.utc).timestamp()


def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def pose_from_row(row):
    q = np.array(row[4:8], dtype=float)
    qn = float(np.linalg.norm(q))
    if abs(qn - 1) > 1e-4:
        raise ValueError(f'Non-unit GT quaternion: {qn}')
    x, y, z, w = q / qn
    R = np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                  [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                  [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
    T = np.eye(4); T[:3, :3] = R; T[:3, 3] = row[1:4]
    return T, qn


def main():
    if (ROOT / 'selection.json').exists():
        raise FileExistsError('Selection already frozen; do not overwrite.')
    TMP.mkdir(parents=True, exist_ok=False)
    archive = TMP / 'freiburg1_xyz.tgz'
    record = {'url': URL, 'tls_verified': True, 'ca_bundle': certifi.where(),
              'bytes_received': 0, 'data_byte_cap': BYTE_CAP, 'status': 'started'}
    started = time.perf_counter()
    context = ssl.create_default_context(cafile=certifi.where())
    try:
        with urllib.request.urlopen(URL, context=context, timeout=30) as response:
            record.update(final_url=response.url, headers=dict(response.headers))
            expected = int(response.headers.get('Content-Length', 0))
            if not 0 < expected <= BYTE_CAP:
                raise ValueError(f'Unexpected Content-Length: {expected}')
            with archive.open('wb') as f:
                while True:
                    if time.time() > DEADLINE - 180:
                        raise TimeoutError('Wall-clock budget: reserve time for evidence and cleanup')
                    chunk = response.read(min(1024*1024, BYTE_CAP-record['bytes_received']+1))
                    if not chunk:
                        break
                    record['bytes_received'] += len(chunk)
                    if record['bytes_received'] > BYTE_CAP:
                        raise ValueError('Dataset byte cap reached')
                    f.write(chunk)
                    if record['bytes_received'] % (32*1024*1024) == 0:
                        print('Downloaded bytes', record['bytes_received'], flush=True)
            if record['bytes_received'] != expected:
                raise ValueError('Incomplete download')
        record['download_s'] = time.perf_counter() - started
        record['archive_sha256'] = digest(archive)
        metadata_dir = ROOT / 'reference'
        metadata_dir.mkdir(exist_ok=True)
        with tarfile.open(archive, 'r:gz') as tar:
            members = tar.getmembers()
            # Read only named regular files. Never bulk-extract untrusted paths.
            for basename in ['rgb.txt', 'groundtruth.txt']:
                matching = [m for m in members if m.isfile() and Path(m.name).name == basename]
                if len(matching) != 1:
                    raise ValueError(f'Expected one {basename}')
                data = tar.extractfile(matching[0]).read()
                (metadata_dir / basename).write_bytes(data)
            rgb = [l.split() for l in (metadata_dir/'rgb.txt').read_text().splitlines()
                   if l.strip() and not l.startswith('#')]
            rgb = sorted([(float(t), name) for t, name in rgb])
            gt = np.loadtxt(metadata_dir/'groundtruth.txt')
            gt = gt[np.argsort(gt[:, 0])]
            selection = {'version': 'TUM-P0-SELECTION-1', 'frozen_utc': datetime.now(timezone.utc).isoformat(),
                         'protocol': 'GEO-P0.2', 'protocol_sha256': digest(ROOT/'provenance/PROTOCOL-GEO-P0.2.md'),
                         'archive_sha256': record['archive_sha256'], 'first_rgb_timestamp': rgb[0][0],
                         'reference_convention': 'color optical camera-to-world; tx ty tz metres; quaternion qx qy qz qw; X right Y down Z forward',
                         'reference_source': 'https://cvg.cit.tum.de/data/datasets/rgbd-dataset/file_formats',
                         'interpolation': 'none; nearest timestamp, tie chooses earlier timestamp', 'frames': [],
                         'metadata_hashes': {f.name:digest(f) for f in metadata_dir.iterdir() if f.is_file()}}
            (ROOT/'inputs').mkdir(exist_ok=True)
            chosen = set()
            for i, offset in enumerate([2.0, 2.5, 3.0, 3.5]):
                target = rgb[0][0] + offset
                stamp, name = min(rgb, key=lambda v:(abs(v[0]-target), v[0]))
                if abs(stamp-target) > .05 or name in chosen:
                    raise ValueError('selection-failed: RGB tolerance or duplicate')
                chosen.add(name)
                ref = gt[int(np.argmin(abs(gt[:, 0]-stamp)))]
                if abs(ref[0]-stamp) > .02:
                    raise ValueError('reference-insufficient: GT timestamp tolerance')
                T, qnorm = pose_from_row(ref)
                matching = [m for m in members if m.isfile() and m.name.endswith('/'+name)]
                if len(matching) != 1:
                    raise ValueError(f'Missing/ambiguous archive member: {name}')
                filename = f'{i:02d}-{Path(name).name}'
                image_path = ROOT/'inputs'/filename
                image_path.write_bytes(tar.extractfile(matching[0]).read())
                selection['frames'].append({'index':i, 'target_offset_s':offset, 'target_timestamp':target,
                    'rgb_timestamp':stamp, 'rgb_target_delta_s':stamp-target, 'source_archive_member':matching[0].name,
                    'file':filename, 'sha256':digest(image_path), 'size':Image.open(image_path).size,
                    'gt_timestamp':float(ref[0]), 'gt_rgb_delta_s':float(ref[0]-stamp),
                    'gt_row_timestamp_xyz_xyzw':ref.tolist(), 'gt_quaternion_norm_before_normalizing':qnorm,
                    'gt_camera_to_world':T.tolist()})
            (ROOT/'selection.json').write_text(json.dumps(selection,indent=2))
            (ROOT/'selection.sha256').write_text(digest(ROOT/'selection.json')+'\n')
            print(json.dumps(selection,indent=2),flush=True)
        record['status'] = 'selection-frozen'
    except Exception as exc:
        record.update(status='failed', error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        record['prepare_total_s'] = time.perf_counter() - started
        (ROOT/'logs/download-and-selection.json').write_text(json.dumps(record,indent=2))
        # Only this process created this file and staging directory, with no extracted tree.
        expected_tmp = (WORKSPACE/'.workspace/tmp/geometry-audit/tum-data').resolve()
        if TMP.resolve() != expected_tmp or TMP.is_symlink():
            raise RuntimeError('Unexpected temporary cleanup path')
        if archive.exists():
            archive.unlink()
        TMP.rmdir()


if __name__ == '__main__':
    main()
