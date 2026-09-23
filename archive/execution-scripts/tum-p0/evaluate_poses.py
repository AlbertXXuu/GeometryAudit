"""Check frozen TUM conventions and compare six i<j relative poses; no H2 labels."""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parent


def reference_checks(selection):
    reference = [np.array(f['gt_camera_to_world']) for f in selection['frames']]
    checks = []
    for f, T in zip(selection['frames'], reference):
        q = f['gt_row_timestamp_xyz_xyzw'][4:8]
        independent_R = Rotation.from_quat(q).as_matrix()
        assert np.allclose(T[:3, :3], independent_R, atol=1e-12)
        assert np.allclose(np.linalg.inv(T) @ T, np.eye(4), atol=1e-12)
        assert np.allclose(T[:3, :3].T @ T[:3, :3], np.eye(3), atol=1e-12)
        assert abs(np.linalg.det(T[:3, :3])-1) < 1e-12
        # Camera optical center [0,0,0,1] must map to the published world position.
        assert np.allclose((T @ [0,0,0,1])[:3], f['gt_row_timestamp_xyz_xyzw'][1:4])
        point_cam = np.array([.1, .2, 2., 1.])
        point_back = np.linalg.inv(T) @ (T @ point_cam)
        assert np.allclose(point_cam, point_back, atol=1e-12)
        checks.append({'index':f['index'], 'det_R':float(np.linalg.det(T[:3,:3])),
                       'quaternion_scipy_max_abs_error':float(np.max(abs(T[:3,:3]-independent_R))),
                       'point_round_trip_max_abs_error':float(np.max(abs(point_cam-point_back)))})
    # Contract check: moving camera j by +1 world-X makes camera i origin appear at -1 in j.
    Ti, Tj = np.eye(4), np.eye(4); Tj[0,3] = 1
    assert np.allclose((np.linalg.inv(Tj)@Ti)[:3,3], [-1,0,0])
    # Scalar-last +90-degree Z quaternion maps camera X basis to world Y.
    qz = [0,0,np.sqrt(.5),np.sqrt(.5)]
    assert np.allclose(Rotation.from_quat(qz).apply([1,0,0]), [0,1,0], atol=1e-12)
    pair_checks=[]
    for i,j in itertools.combinations(range(4),2):
        Ti,Tj=reference[i],reference[j]
        relative=np.linalg.inv(Tj)@Ti
        explicit_R=Tj[:3,:3].T@Ti[:3,:3]
        explicit_t=Tj[:3,:3].T@(Ti[:3,3]-Tj[:3,3])
        assert np.allclose(relative[:3,:3],explicit_R,atol=1e-12)
        assert np.allclose(relative[:3,3],explicit_t,atol=1e-12)
        # Transform an actual reference-camera point via world and directly i->j.
        p_i=np.array([.1,.2,2.,1.])
        assert np.allclose(relative@p_i,np.linalg.solve(Tj,Ti@p_i),atol=1e-12)
        pair_checks.append({'pair':f'{i}-{j}','T_ji':relative.tolist(),
                            'reference_baseline_m':float(np.linalg.norm(explicit_t))})
    return reference, {'status':'pass','coordinate_source':'provenance/tum-file-formats.html',
        'convention':'TUM xyz metres and xyzw quaternion = optical camera to world; X-right Y-down Z-forward per official projection equations',
        'relative_transform':'T_ji = inverse(T_j) @ T_i, mapping coordinates in camera i to camera j',
        'checks':checks, 'pairs':pair_checks,
        'limit':'round-trip is an implementation/convention check, not evidence that predicted geometry is correct'}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--reference-only',action='store_true')
    args=parser.parse_args()
    selection_bytes=(ROOT/'selection.json').read_bytes()
    selection_sha=hashlib.sha256(selection_bytes).hexdigest()
    assert selection_sha==(ROOT/'selection.sha256').read_text().strip()
    selection=json.loads(selection_bytes)
    references,checks=reference_checks(selection)
    checks['selection_sha256']=selection_sha
    if args.reference_only:
        (ROOT/'reference-checks.json').write_text(json.dumps(checks,indent=2))
        print('PASS: four GT xyzw/c2w poses, optical projection convention and six directed round-trips')
        return
    predictions=[]
    for i in range(4):
        with np.load(ROOT/f'run-518/raw-view-{i:02d}.npz',allow_pickle=False) as data:
            predictions.append(data['camera_poses'][0].astype(np.float64))
    pairs=[]
    for i,j in itertools.combinations(range(4),2):
        gt=np.linalg.inv(references[j])@references[i]
        estimate=np.linalg.inv(predictions[j])@predictions[i]
        gt_baseline=float(np.linalg.norm(gt[:3,3]))
        estimated_baseline=float(np.linalg.norm(estimate[:3,3]))
        row={'pair_id':f'{i}-{j}','i':i,'j':j,'context_N':4,
             'reference_baseline_m':gt_baseline,'predicted_baseline_model_m':estimated_baseline,
             'rotation_deg':None,'translation_direction_deg':None,'translation_unavailable_reason':None,
             'reference_T_ji':gt.tolist(),'predicted_T_ji':estimate.tolist(),
             'high_confidence_status':'unavailable-not-calibrated'}
        for T in [predictions[i],predictions[j]]:
            assert np.isfinite(T).all()
            assert np.allclose(T[3],[0,0,0,1],atol=1e-6)
            assert np.allclose(T[:3,:3].T@T[:3,:3],np.eye(3),atol=1e-3)
            assert abs(np.linalg.det(T[:3,:3])-1)<1e-3
        cos_R=(np.trace(estimate[:3,:3]@gt[:3,:3].T)-1)/2
        row['rotation_deg']=float(np.degrees(np.arccos(np.clip(cos_R,-1,1))))
        if gt_baseline < .05:
            row['translation_unavailable_reason']='reference-baseline-below-0.05m'
        elif estimated_baseline <= 1e-6:
            row['translation_unavailable_reason']='predicted-translation-near-zero-at-1e-6-model-metres'
        else:
            cos_t=np.dot(estimate[:3,3],gt[:3,3])/(estimated_baseline*gt_baseline)
            row['translation_direction_deg']=float(np.degrees(np.arccos(np.clip(cos_t,-1,1))))
        pairs.append(row)
    report={'version':'TUM-P0-POSE-COMPARISON-1','selection_sha256':selection_sha,
        'protocol':'GEO-P0.2','context_N':4,'pairs':pairs,
        'gt_is_input_to_model':False,'global_alignment':'none; relative comparisons in the destination optical camera coordinates',
        'ate':'not requested/not computed','pose_classification':'not claimed in this P0 report; raw R/t errors and reference eligibility only',
        'reference_noise_limit':'published motion-capture reference plus nearest association; reference noise bounds not independently measured',
        'reference_checks':checks}
    (ROOT/'pose-comparison.json').write_text(json.dumps(report,indent=2))
    fields=['pair_id','context_N','reference_baseline_m','predicted_baseline_model_m','rotation_deg','translation_direction_deg','translation_unavailable_reason','high_confidence_status']
    with (ROOT/'pose-comparison.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(pairs)
    print(json.dumps([{k:p[k] for k in fields} for p in pairs],indent=2))


if __name__=='__main__':
    main()
