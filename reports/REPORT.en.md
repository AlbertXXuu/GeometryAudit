# First-round GEO engineering artifact review

[English](REPORT.en.md) | [简体中文（原文）](REPORT.md) | [Report index](../README.md#evidence-and-provenance)

> English translation of [REPORT.md](REPORT.md), version **GEO-REVIEW-R1**, dated 2026-09-22 (Beijing time). The original report remains unchanged. This translation preserves its historical scope, measurements, conclusions, and pending work; it does not record a new experiment.
>
> Repository publication copy: internal links were relocated; original source hashes are in `provenance.json`. Recorded measurements and conclusions are unchanged.

Version: **GEO-REVIEW-R1**; date: 2026-09-22 (Beijing time); reviewer: role 01. Subject: role 02's `GEO-ENGINEERING-R1 / run-02`. Status: **P0 engineering evidence review passed; the number of research-validation scenes remains 0**.

## Conclusion and scope

The saved configuration, execution logs, raw tensors, and exported artifacts agree. They support successful real two-image inference on an RTX 4060 Laptop and the preservation of inspectable results. No conflicting evidence was found that would block the current engineering conclusion. Here, “passed” means a consistency review of saved artifacts and their interpretation. The model was not run a second time, the environment was not rebuilt, and geometric ground truth was not independently measured.

This review followed the lab-report skill's requirements for evidence and result reporting. Engineering execution used **GEO-P0.1**; the current **GEO-P0.2** was used only to review engineering-acceptance compatibility and interpretation boundaries. The research-performance `evaluated_under` remains null; the newer preregistration is not applied retroactively. H1/H2/H3, native geometric confidence G0, VGGT, and repair controls were not evaluated.

## Inputs, implementation, and evidence entry points

- Role 02's formal handoff (historical internal handoff) and main engineering report (original local artifact: `round1/README.md`). Inputs are the Middlebury Motorcycle left/right images, obtained through a pinned scikit-image release commit: 2 images at 741×500, actually preprocessed to 518×336, in left-to-right order.
- Actual configuration (original local artifact: `round1/run-02/config.json`): MapAnything Apache, source `3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9`; model revision `00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a`; BF16, memory-efficient, minibatch=1, seed=0. Raw predictions used `apply_mask=False`, confidence mask=False, and multiview confidence=False.
- The [execution entry point](../scripts/motorcycle/run_baseline.py) and [export logic](../scripts/motorcycle/export_replay.py) were inspected read-only. Weights were strictly loaded and the GPU synchronized before image preprocessing; inference timing covered `model.infer` through GPU synchronization. Raw arrays were saved before applying the native display mask to the same result. There was no second forward pass.
- The [protocol relationship record](../records/motorcycle/protocol-alignment.json) and both saved protocol versions match role 01's P0.1 snapshot and current P0.2 file byte for byte.

## Checks performed and quantitative results

This review read files on the CPU using local Python/NumPy; it did not execute role 02's inference script. Machine-readable evidence: [REVIEW_R1.json](REVIEW_R1.json), containing the scope, measured hashes of 25 files, array statistics, and unit conversions. The source delivery manifest SHA256 is `e47d765fdeaa041bbe3f45f2dd767b25d3f721cc61d510179bc0f74b4d8f0613`.

| Check | Role 01's observed result | Supported interpretation |
| --- | --- | --- |
| Artifact consistency | SHA256 and byte size of all 25 key files match role 02's manifest, covering inputs, two raw/two display NPZ files, run-02 artifacts, configuration/resources, selected logs, scripts, and protocol snapshots | Saved results match the stated delivery version; this is not a file-by-file review of all 849 files |
| Raw predictions | Loaded with `allow_pickle=False`; camera/intrinsics/conf/depth/points are finite in both views, and all 174,048 raw depth pixels per view are positive | Outputs are readable and numerically valid at a basic level; finite numbers do not establish correct geometry |
| Camera matrices | Last rows satisfy the homogeneous-transform format; rotation determinant≈1; maximum absolute deviations in `RᵀR-I` are approximately 2.58e-11 and 5.96e-8 | Pose format is internally consistent; no error against external reference poses was evaluated |
| Raw/display relationship | conf is elementwise identical in both views; depth/pts3d inside the display mask are elementwise identical to raw values | Learned conf is preserved, and display processing does not rewrite the geometry of retained points |
| Display mask | Left/right retained pixels: 148,914 / 148,936; zero display-depth values: 25,134 / 25,112; total raw pixels: 348,096 | 297,850 retained in total, or 85.5655%; this is the model-mask retention ratio, not accuracy or reference coverage |
| GLB | Independently parsed GLB v2 header/JSON/accessor; POINTS primitives total 297,850 | Exported point count exactly matches the display mask; GLB coordinates were not directly mixed with raw camera coordinates |
| Resources | Recomputed 38 raw samples: whole-GPU peak 7,780 MiB, process RSS peak 9,298,391,040 bytes | Sampling summary is correct; sampling at approximately 1-second intervals may miss transient peaks |
| Visuals and RRD | Actually inspected `diagnostics.png` and `viewer-web.png`; figures label this an engineering smoke test, geometric accuracy unverified, confidence not a probability. Role 02's `rrd verify` log reports 1 file with no errors | Screenshots show real saved results with appropriate scope statements; role 01 did not restart the viewer or repeat drag interactions |

Raw confidence ranges are left `[1, 9.552864]` and right `[1, 8.399891]`, clearly not 0–1 probabilities of correctness. Black borders/zero values in the depth figures include the effects of display masking; they cannot be interpreted as the raw model producing no depth at those pixels. The upstream GLB exporter applies a 180° rotation around the X axis; camera/depth accuracy evaluation should use the NPZ's OpenCV camera-to-world definition.

### Cost definitions

The following reviews role 02's single successful cold-start record. These are neither new measurements by role 01 nor averages over repeated experiments. Original sources: [result.json](../records/motorcycle/result.json), resources.json (original local artifact: `round1/run-02/resources.json`), and the [cost summary](../records/motorcycle/cost-summary.json).

| Quantity | Value and limitation |
| --- | --- |
| Model loading | 14.087 s, using previously downloaded local weights |
| Inference | 11.050 s, 2 images, 518×336, BF16, GPU synchronized; successful inference n=1 |
| Export | 13.651 s, including raw tensor writes, display masking, NPZ/GLB/RRD/figures |
| Loading start through completion | 39.429 s, including inter-stage overhead, image preprocessing, monitor shutdown, etc.; cannot simply be equated with the sum of the three stages; excludes initial installation/download and viewer acceptance |
| PyTorch allocated / reserved peak | 7.18823 / 7.69922 GiB; peak counters reset before inference, with resident weights included; a different measurement from whole-GPU sampling |
| nvidia-smi whole-GPU sampled peak | 7,780 MiB, including the desktop and other processes; only approximately 408 MiB below the reported 8,188 MiB capacity at that time, with no guarantee this difference is actually available to the next model run |
| Sampled RSS peak | 8.65980 GiB for the current process, not total system memory |
| Initial preparation | Role 02 recorded 567.981 s for downloading weights and approximately 268.584 s for dependency installation; installation duration comes from log times and was not remeasured here. Parallel activities cannot be summed as human labor time |

Two-image feasibility therefore does not establish four-image feasibility. If the main task later assigns a four-image TUM run, first perform capacity acceptance under comparable settings and follow the agreed OOM/budget stop rules; this result does not authorize early expansion to P1/P2. Added service/API cost of CNY0 is role 02's cost record. Active user time, electricity, and total end-to-end cost were not fully measured.

## Failures, missing evidence, and publication scope

- The `run-01` log confirms an exception from psutil receiving a WindowsPath before model loading. The corrected str adapter and `run-02` are preserved. This engineering-adaptation failure must not be counted as a model-geometry failure, and preparation costs must not be hidden.
- Native desktop viewer failure and Web viewer success are preserved separately. Role 01 inspected the successful screenshots and recording-verification logs but did not independently replay the viewer, perform a clean install, or run a second inference. The accepted claim is therefore “existing replayable artifacts and replay entry points,” not successful independent clean-install reproduction.
- Role 01 did not rehash the 4.914GB checkpoint or the complete source tree. Strict loading and validation against the Hub LFS belong to role 02's records. The JSON lists the 25 files actually hashed in this review; matching hashes establish artifact consistency only.
- There is no GT, difficult scene, pair label, second model, G0, or repair differential. Research-validation scenes=0; H1/H2/H3 remain untested. No conclusion about high-confidence errors, diagnostic gains, or repair benefits is supported.
- Redistribution terms for the original Middlebury photographs have not been verified. Inputs, figures containing photographs, and point-cloud screenshots remain within local verification scope. This review adds no licensing determination or public upload.

Original wording suitable for the website: **On 2026-09-22, one real two-image engineering run of MapAnything Apache was completed on an RTX 4060 Laptop 8 GiB device. Both inputs were preprocessed to 518×336, a single inference took 11.05 seconds, and inspectable outputs and a recording were preserved. Engineering status: “prototype operational”; geometric accuracy, disambiguation, and repair effects remain unverified.** Any memory metric must preserve the distinction between allocated, reserved, and whole-GPU sampled values. If 85.57% is used, describe it only as the display-mask retention ratio. This report does not require the website to show that ratio, which offers readers limited value.

## Follow-up and review entry points

The P0 delivery is accepted; P1/P2 remain unstarted. During this review, the main task separately assigned role 02 the first P0.2 TUM four-frame window in the shared briefing (historical internal handoff): 45 minutes wall clock, 5 minutes GPU time, and 0.6GB of new data; at most one standard-518 attempt, with a 392 fallback on the same four frames allowed after OOM only if preregistered and supported upstream. Evaluate only six reference R/t pairs; do not select the later two windows; this is not H2 calibration. That assignment is not a completed result of this report. Role 01 does not run the GPU or modify role 02's source directory.

Review procedure: recalculate SHA256/size using the relative paths in `REVIEW_R1.json.checked_files`; read both raw/display pairs in NumPy without pickle, compare conf and depth/pts3d within the mask, and count finite values and valid pixels; sum POINTS counts from GLB accessors; recompute GPU/RSS peaks from raw resources rows; compare both protocol snapshots. This is CPU file review and does not require restoring the model environment. Actual inference and viewer commands are maintained in role 02's main report and are not duplicated into another execution entry point.
