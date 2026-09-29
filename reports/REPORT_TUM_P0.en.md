# Ordinary four-frame TUM reference comparison: independent CPU review

[English](REPORT_TUM_P0.en.md) | [简体中文（原文）](REPORT_TUM_P0.md) | [Report index](../README.md#evidence-and-provenance)

> English translation of [REPORT_TUM_P0.md](REPORT_TUM_P0.md), version **GEO-REVIEW-TUM-P0-1**, dated 2026-09-22 (Beijing time). The original report remains unchanged. This translation preserves its historical scope, measurements, conclusions, and pending work; it does not record a new experiment.
>
> Repository publication copy: internal links were relocated; original source hashes are in `provenance.json`. Recorded measurements and conclusions are unchanged.

Version: **GEO-REVIEW-TUM-P0-1**; date: 2026-09-22 (Beijing time); role 01. Subject: role 02's `GEO-ENGINEERING-TUM-P0-1 / run-518`; assignment `geo-mapanything-p0-tum4-20260922`.

**Conclusion: the frame selection, coordinate interpretation, six pairwise values, and denominators pass review for an ordinary reference engineering comparison.** One four-image standard-518 run has inspectable raw results: 6 rotation-error pairs and 5 translation-direction-error pairs. This window is not H2 calibration; research-validation scenes remain 0. No model was run, dependencies installed, or viewer launched. The protocol, historical R1 report, role 02's artifacts, and central ledger were not modified, and no new experiment was assigned.

## Evidence and scope

- Original delivery: role 02's main report (original local artifact: `tum-p0/README.md`), [frozen frame selection](../records/tum/selection.json), actual configuration (original local artifact: `tum-p0/run-518/config.json`), [six-pair results](../records/tum/pose-comparison.json), and [reference-convention checks](../records/tum/reference-checks.json).
- Role 01's machine-readable review: [REVIEW_TUM_P0.json](REVIEW_TUM_P0.json). Calculations were performed independently on the CPU with the Python standard library and already-installed NumPy; role 02's `evaluate_poses.py` or `verify_tum.py` were not called as substitutes for independent recalculation.
- All **273 file entries** in the delivery manifest were traversed; every size and SHA256 matched. Source manifest SHA256: `94e01ad9b919c8afcb1a3de10231e496c5b9f0c00cfe8ba129131a174bdfac42`. This checks file consistency within the TUM delivery. It is not fresh verification of external download sources, and the reused external 4.914GB model weights were not rehashed.
- Both the execution and review use GEO-P0.2. The snapshot is byte-identical to role 01's current protocol, SHA256 `3c6a51de641bf4fafeb44ecb525d9850274be0df41cd1d6763d0a521ef7e8760`. Frame-selection SHA256 `336c33ce87f300f07b3ac70e3f17f1f1b7fb832fcfd7d958160047a6f5a84ac3` matches the configuration.

## Frame selection and independent reference

Role 01 searched again for nearest neighbors in the preserved complete `reference/rgb.txt` and `reference/groundtruth.txt`, rather than checking only the rows already selected. The four frames are exactly the nearest neighbors at +2/+2.5/+3/+3.5 seconds after the first RGB timestamp, contain unique images, and are in ascending time order. Input PNG hashes and both raw metadata hashes match the frozen selection.

| Index | RGB timestamp | Signed difference from target time, seconds | GT minus RGB time, seconds |
| --- | --- | ---: | ---: |
| 0 | 1305031104.175424 | +0.000120163 | +0.000375986 |
| 1 | 1305031104.675525 | +0.000221014 | +0.000375032 |
| 2 | 1305031105.175159 | −0.000144958 | +0.000641108 |
| 3 | 1305031105.675166 | −0.000138044 | +0.000734091 |

All meet the RGB difference ≤0.05 seconds and GT pairing difference ≤0.02 seconds. No interpolation was used, and the later two windows were not selected. The saved freeze time, 19:15:05.905455 UTC, precedes the execution configuration's 19:19:59.036451 UTC, supporting the record that this run used frozen inputs. This ordering check relies on local artifact records, not third-party timestamp authentication.

Read-only inspection of the `run_tum.py` input chain: selection chooses images and verifies hashes; the inputs passed to `load_images → model.infer` are four RGB images, with no GT pose or depth injected. `fixed_mapping` uses resolution_set=518, and every raw confidence array has shape `(1,392,518)`: **model images are 518 pixels wide and 392 pixels high; 392 is not a fallback resolution.** PLAN and configuration record that upstream does not support fixed_mapping392, so this run had no such fallback path. The single 518 attempt succeeded.

## Coordinates, calculation, and pairwise results

Reference conventions follow the preserved snapshot of the official format page (original local artifact: `tum-p0/provenance/tum-file-formats.html`): `tx ty tz` is the color camera's optical-center position in the motion-capture world frame, in meters; `qx qy qz qw` is a unit quaternion relative to the world frame. The optical axes right/down/forward align with the raw MapAnything camera convention. Camera-to-world matrices were used; GLB display coordinates were not used for error calculations.

Role 01 normalized the scalar-last quaternions from the original numeric GT rows, reconstructed rotations with the cross-product-matrix formula `R=I+2w[v]×+2[v]×²`, and added the original translations. Results match the c2w matrices in selection within absolute tolerance 1e-12. Predictions were read directly from `camera_poses` in the four `raw-view-*.npz` files and converted to float64. Then `solve(T_j,T_i)` was independently used to obtain `T_ji`, checking each predicted/reference relative matrix saved by role 02. No global trajectory fitting/alignment was introduced into the relative errors.

- Rotation: `acos(clip((trace(R_pred R_refᵀ)−1)/2,−1,1))`, converted to degrees.
- Translation: the **directed** angle between the two relative translation vectors, without taking the absolute value of the dot product. Direction is not evaluated if the reference baseline is <0.05m or predicted translation is near zero.
- Absolute differences between relative matrices and role 02's files are ≤1e-12; recomputed eligible angles differ from the report by <1e-8 degrees. This establishes agreement with saved calculations, not absence of noise in the reference trajectory.

| Image pair | Reference baseline, m | R error, ° | t-direction error, ° |
| --- | ---: | ---: | ---: |
| 0–1 | 0.165027270 | 1.665748298 | 5.636605736 |
| 0–2 | 0.140712686 | 3.021898507 | 7.408182163 |
| 0–3 | 0.071235034 | 0.585604838 | 5.493252134 |
| 1–2 | 0.026964050 | 1.674260209 | null: reference baseline<0.05m |
| 1–3 | 0.235214009 | 1.803999609 | 5.709959501 |
| 2–3 | 0.211527894 | 2.863154376 | 8.439679753 |

**Rotation denominator: 6; translation-direction denominator: 5.** Pair 1–2 was neither recorded as zero nor included in the eligible translation denominator. All six pairs come from the same four-frame window and share cameras; they cannot be counted as six independent scenes. Reference noise has not been independently bounded. This report accepts numeric comparisons only and assigns no pose-correct/error labels. Five values falling within some tolerance cannot establish an H2 threshold: there is only one window, without the three windows and minimum calibration samples required by the protocol.

## Raw outputs and interpretation boundaries

The four raw NPZ files were read with `allow_pickle=False`; camera/intrinsics/conf/depth/points are all finite. Confidence in all four display copies is elementwise identical to the raw data; depth/pts3d inside each display mask is also elementwise identical. Valid pixel counts are 189972, 188734, 189453, and 190089, totaling 758248. These are display-mask point counts, not correct-point counts or coverage of reference-visible regions. The configuration enabled neither confidence filtering nor native G0.

Role 02 reported a single synchronized inference of 11.870 seconds, a model subprocess duration of 42.056 seconds, and approximately 22 minutes 10 seconds of allocated wall-clock time. This review read the records and checked file consistency; it did not remeasure execution cost. Budget review and central registration belong to the main task. Allocator reserved memory must not be treated as WDDM physical residency. This four-image 518×392 run and the two-image 518×336 Motorcycle run must not be directly interpreted as doubled scale at unchanged cost.

No viewer was started or interaction independently repeated. Depth accuracy, ATE, scale accuracy, and confidence calibration were not recomputed or evaluated. Small errors in an ordinary scene do not establish effective disambiguation of repeated structures or general accuracy, still less effective repair. The engineering record's `accuracy_evaluation: not performed` describes the inference stage; the independent trajectory comparisons above did occur afterward. These stages must be distinguished: it would be inaccurate to continue saying that no geometric reference comparison of any kind was ever performed.

## Handoff conclusion

The accepted limited conclusion is **1 ordinary four-frame reference window, 1 standard-518 run, and numeric comparisons of 6 R pairs / 5 t pairs**. Research-validation scenes: 0. H2 high-confidence classification is unavailable; no ATE/P1/P2. The protocol requires no change. This review ends after one completed review; later experiments require separate assignment by the main task.

This result was written to role 01's independent review directory, without modifying the website's current R1 publication draft awaiting authorization. TUM material licensing notes are handled by role 02's provenance records and the specific publication task. No publication was performed here, and the licensing scope of Motorcycle materials was not expanded.
