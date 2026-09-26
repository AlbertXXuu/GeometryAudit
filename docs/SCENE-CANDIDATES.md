# Physical-scene candidate register

Version: `GEO-SCENES-0.1-draft` · checked 2026-09-26 · **closed preparation record; no scene admitted**.

The [2026-09-26 prior-art decision](PRIOR-ART-DECISION-2026-09-26.md) retires the associated research candidate. Entries and admission instructions below document the unexecuted draft; they are no longer an active acquisition or experiment queue.

This register supports [GEO-POSE-0.1-draft](PROTOCOL-NEXT.md). It lists eight candidate dataset entries with official source evidence. **Eight names do not establish eight independent physical scenes.** No new scene is admitted yet: exact image selection, inter-scene overlap and pair-specific reference uncertainty remain unresolved. The 6–10 independent-scene target therefore remains unfulfilled. The existing TUM window is development/engineering evidence, not new research validation.

## Candidate entries

| ID | Official dataset entry | Verified source facts | Reference route and next admission evidence |
| --- | --- | --- | --- |
| C01 | ETH3D `courtyard` | High-resolution training scene; 38 images, outdoors | Published camera calibration plus laser-based geometry. Check site overlap with facade/electro, exact cameras and rotation uncertainty. |
| C02 | ETH3D `delivery_area` | Training scene; 44 images, indoors | Same reference route; establish a distinct physical indoor space and camera-to-scan registration quality. |
| C03 | ETH3D `electro` | Training scene; 45 images, outdoors | Same reference route; location overlap with other campus exterior captures is unknown. |
| C04 | ETH3D `facade` | Training scene; 76 images, outdoors | Same reference route; do not count a different view of the courtyard building as an independent place. |
| C05 | ETH3D `office` | Training scene; 26 images, indoors | Same reference route; identify actual room and static arrangement, with no cross-split duplicates. |
| C06 | ETH3D `playground` | Training scene; 38 images, outdoors | Same reference route; verify physical location and overlap before final group assignment. |
| C07 | ETH3D `terrains` | Training scene; 42 images, indoors | Same reference route; do not infer an outdoor landscape from its name or count tabletop variants separately. |
| C08 | TUM `freiburg1_xyz` physical environment | Existing four-image window and independent motion-capture reference are already recorded | Retained inputs/poses and CPU calculation are available. Bound camera calibration/timing uncertainty before assigning new hard labels; all other sequences in the same environment stay in one group. |

C01–C07 names, image counts and indoor/outdoor classification come from the [official ETH3D dataset catalogue](https://eth3d.ethz.ch/datasets), retrieved through its indexed page on 2026-09-26. The catalogue's direct fetch timed out during this check; no archive was downloaded or verified. The entries are not claimed to exhibit model errors, repeated texture or sufficient four-view overlap. Their intended ordinary-control role is a selection proposal.

For temporary leakage protection, C01/C03/C04 share the unresolved group `eth3d-exterior-overlap-pending`; C02/C05/C07 share `eth3d-interior-overlap-pending`; C06 has `eth3d-playground-pending`. These are conservative grouping instructions, not assertions that the grouped scenes are the same place or that different groups are independent. Any remaining uncertain group relationship prevents a confirmatory split. C08 is `tum-fr1-environment-pending`, with the complete physical extent still to be documented. Never count these provisional group strings as established independent scenes.

## What the references support

[ETH3D's overview](https://eth3d.ethz.ch/overview) confirms high-resolution indoor/outdoor scenes and laser-scanned geometry. [Its published pipeline](https://github.com/ETH3D/dataset-pipeline) describes initial SfM alignment, laser-scan refinement and image-pose/intrinsic refinement against scans. [The format documentation](https://eth3d.ethz.ch/documentation) describes the camera model files. Thus a scan is independent geometric measurement, while the released camera pose also depends on image registration. No inspected source supplied a per-selected-pair camera-rotation uncertainty bound. A scanner distance specification cannot fill that missing field.

For C08, the [TUM dataset](https://cvg.cit.tum.de/data/datasets/rgbd-dataset) and [official format](https://cvg.cit.tum.de/data/datasets/rgbd-dataset/file_formats) establish motion-capture camera poses; the [accepted local review](../reports/REPORT_TUM_P0.md) establishes association and numerical conventions for the saved window. It explicitly leaves reference noise unbounded. The saved 0.05 m translation-baseline rule identifies one ineligible pair; it does not by itself bound translation-direction uncertainty.

The [ETH3D data terms](https://eth3d.ethz.ch/) state CC BY-NC-SA 4.0. This register copies no images, scans or dataset archives. A future input acquisition must retain the actual source/terms snapshot and attribution; publishing derived media is a separate concrete scope. Model/code licensing does not replace dataset terms.

## Admission record required for each physical scene

Before considering any inference, fill these fields in a new manifest:

1. official release/archive URL, checked size and hash; exact selected image names/hashes/order;
2. physical place, static arrangement and overlap evidence; final group ID and reviewer disposition;
3. available reference files, units, camera conventions, timestamp rules and successful round-trip checks;
4. independent reference-generation chain, pair-specific uncertainty method/evidence and eligible endpoints;
5. four-image selection rule based on reference geometry/visibility, with every excluded image/pair reason;
6. allowed public use and attribution; known or unknown pretrained-model exposure;
7. source preparation bytes, local storage, missing dependencies, stage cost and stop decision.

The low-cost next action is metadata/reference inspection for one promising ETH3D candidate, then one other demonstrably different place. Inspect published reference quality and available archives before data transfer; a scene package larger than the proposed allowance is a scope decision, not an instruction to exceed it. Failure to establish reference uncertainty can produce a valid narrower reference-discrepancy study, but cannot be silently converted into correct/error labels.

This first-stage source review did not inspect candidate images, download large data, train/fine-tune models or perform new model inference. Potential aliasing scenes from the older protocol remain available as a different research population; public pair-identity labels alone do not supply precise pose-error ground truth.
