# Relative-pose error audit — next protocol draft

Version: `GEO-POSE-0.1-draft` · 2026-09-26 · **closed without execution; never frozen**.

**Current disposition:** the [2026-09-26 prior-art decision](PRIOR-ART-DECISION-2026-09-26.md) retires `CAND-GEO-01` under its current reliability-adapter definition. This draft is retained as preparation history. Its proposed stages, settings, resource prerequisites and future-tense instructions below are inactive; they do not authorize further scene admission, implementation or inference.

This draft addresses the recorded gap between a successful geometry run and an independently supported error prediction. The accepted [TUM comparison](../reports/REPORT_TUM_P0.md) checks six relative rotations and five translation directions, but reference uncertainty is not bounded. The former `G` in [GEO-P0.2](PROTOCOL.md) fits image matches independently; it does not test the model's pose. Its `CG` result cannot establish a high-confidence model-conflict detector. This file proposes a separate testable question and preserves every original protocol and result.

## 1. Question, outputs and stages

For a fixed model and four-image context, can a combination of learned confidence and image evidence that conflicts with the model's relative pose rank independently referenced pose errors better than either signal alone, at the same retained coverage or false-alarm budget?

The primary object is the **predicted relative rotation** for an unordered image pair. Translation direction is a separate secondary endpoint with its own eligibility and denominator. Metric translation/depth and full reconstruction repair are outside this first comparison. A scene contributes one four-image context and six pair records; six pairs are correlated observations, not six independent scenes.

1. **Reference feasibility:** verify acquisition provenance, physical-scene identity, usable cameras/images, reference uncertainty and fixed image selection. Report admitted, pending and rejected candidates with reasons. The proposed 6–10 physical-scene target is not currently met; see [candidate register](SCENE-CANDIDATES.md).
2. **Development observation:** after reference admission, protocol freeze and an actual resource allocation, run the complete admitted list with MapAnything. Preserve successful outputs, errors, missing outputs and unknown labels. This list becomes development data permanently. It cannot later become the confirmatory holdout.
3. **Held-out comparison:** independently acquire and lock other physical scenes, tune only on development/calibration scenes, and evaluate fixed scores and thresholds once. Estimate the required number of scenes from development variation and a practically useful effect; 30–50 is a possible planning range, not a power guarantee.
4. **Extension:** a second model covers the same locked scene list, including hard cases and failures. A repair test needs separately established diagnostic value, a fixed backend and coverage-preserving interventions.

No stage begins merely because the previous document exists. This draft is the E-GEO-01 deliverable; CPU/preflight findings are separate from new inference results.

## 2. Reference eligibility and labels

Store each reference in an evaluation-only record: acquisition source, reference-generating sensors/algorithm, timestamp association, intrinsics/extrinsics convention, units, uncertainty evidence, image identity and reviewer disposition. No reference pose/depth, identity label or uncertainty decision enters a score or frame selector through the evaluated model's output.

All camera transforms use optical OpenCV camera-to-world `T_wc`, with x right, y down, z forward. For cameras i and j, compute `T_ji = solve(T_wc_j, T_wc_i)`. Convert other conventions explicitly and verify round trips. Use unclipped original model cameras, never GLB display transforms. With `R_p` and `R_r`, rotation discrepancy is `acos(clip((trace(R_p R_r^T)-1)/2,-1,1))` in degrees. Translation discrepancy is the directed angle between relative translations; do not take the absolute dot product or align each pair separately. These reproduce the existing numerical contract.

**Proposed practical tolerances:** rotation `tau_R=5°`; secondary translation direction `tau_t=10°`. They are engineering choices for an observable pilot endpoint, not universal task-utility standards. Review their intended use and freeze them before new outputs are seen. Report continuous discrepancies as well. Do not retune them to obtain more failures from the known TUM result.

For each pair and endpoint record a justified angular uncertainty `u` for the independent reference. It must account for sensor/registration accuracy, camera calibration and timestamp/motion effects relevant to that pair. A laser scanner's distance accuracy alone does not supply camera-orientation uncertainty. An empirical sensitivity range must be labelled empirical, not a guaranteed or statistical confidence bound. If a usable bound cannot be supported, set `u=null` and the hard label to `unknown-reference`.

Where an accepted bound exists, let `L=max(0,e-u)` and `U=min(180,e+u)`:

- `correct`: `U <= tau`;
- `error`: `L > tau`;
- `unknown-boundary`: the interval intersects the tolerance;
- `unknown-reference`: missing/unreliable reference, convention or uncertainty;
- `missing-output` / `invalid-output`: no model pose or a non-finite/non-rigid pose, recorded as an operational failure separately from a geometric label.

Translation additionally requires the conservative lower bound on reference baseline to exceed `0.05 m`, a nonzero predicted translation and a supported direction-error bound. Pure rotation, near-zero baseline or uncertainty that makes direction unstable remains `not-eligible-translation`. It does not remove that pair's eligible rotation endpoint. Reference discrepancies without accepted uncertainty may still be reported descriptively, clearly separated from error rates.

Reference choice is fixed without viewing C/G scores or the model error. ETH3D's camera poses come from image/scan alignment, so they are an independent construction relative to MapAnything, but can share texture-related failure modes with image-based scores. TUM motion capture has a different sensor path, but its camera calibration and time association still require checking. A second SfM fit, two models agreeing or a cycle derived from the same global poses is not an independent label.

## 3. Scores and directly relevant baselines

All scores increase with risk. The primary comparison reuses the same model checkpoint, original images, `context_N=4`, image order and native 518 preprocessing. Save the exact resize/crop mappings, unfiltered learned confidence, intrinsics, cameras, depth and missing fields. Ground-truth intrinsics are not supplied to one method alone; any later calibrated-input track is separate and equal for all methods.

The shared low-cost correspondence set is bidirectional SIFT matching with nearest-neighbour ratio `0.8`, using images in the fixed model pixel coordinate system. Save all tentative coordinates and descriptor/matcher settings before scores are read. Fewer than 20 tentative matches means match-dependent methods abstain; retain the pair. Spatial concentration, planar degeneracy and invalid Sampson denominators are recorded. Exact extraction limits, library revision and degeneracy checks remain implementation-freeze fields, not hidden defaults.

| Method | Proposed score / role |
| --- | --- |
| B0 | Keep every valid model output. This supplies the unfiltered reference risk and operational coverage. |
| C | For each shared match take the smaller raw learned confidence at its two endpoints; take the pair's 10th percentile and negate it. Keep the raw scale and NaN counts; this is not a correctness probability. |
| G_pose | Form `F_model = K_j^-T [t_ji]_x R_ji K_i^-1` from model cameras/intrinsics. Score the fraction of shared matches whose square-root Sampson distance exceeds `1.5` model-image pixels. Store distances as well as the fraction. No fitting to reference cameras occurs. Near-zero translation, singular K or degenerate F means abstention. |
| G_fit | Historical inexpensive control: independently fit a fundamental matrix to the same matches, then recompute the fraction beyond the same Sampson threshold. Fixed seed 0, probability 0.999 and maximum 10,000 iterations; pin the actual estimator/API. This measures how well the matches fit some epipolar geometry, not whether the model pose is correct. |
| CG_pose | Development-scene empirical CDFs turn C and G_pose into risk ranks; take their unweighted mean. Use scene-equal weights, midranks for ties and clipping at the calibration range. Freeze this single combination; no held-out weight search. Missing either input causes abstention. |
| G0 native | MapAnything's existing multiview depth-consistency confidence, aggregated at the same match coordinates. Keep learned C separately. Reuse the same raw forward output only if pinned upstream code supports an equivalent postprocessing route; otherwise record a distinct run and its cost. This directly controls whether existing model geometry confidence already suffices. |
| Strong independent-match comparison | SIFT + the released LightGlue SIFT matcher, followed by a pinned robust relative-pose estimator, using the same model intrinsics and image pairs. Compare rotation disagreement with the model (`G_LG-R`) and eligible translation disagreement separately. Robust-fit support is also reported. This is a proposed composition of existing tools, not a published pose-quality detector and not ground truth. Freeze its feature cap, matching threshold, estimator and cheirality/degeneracy rules before use. |

The LightGlue comparison changes the correspondence source intentionally; report its own match coverage and full preparation/inference cost. Also report G_pose/G_fit on those matches as a matcher-sensitivity analysis, separate from the primary shared-SIFT comparison. This prevents attributing better matches to the proposed combination. Current CPU preflight did not install OpenCV, LightGlue or the model dependencies, and no score in this table has been newly computed.

G_pose's epipolar residual depends jointly on rotation, translation direction, intrinsics and correspondence error. Under the primary rotation endpoint it is a candidate predictive signal, not a rotation-specific detector or a causal diagnosis. Stratify results by translation eligibility/baseline, geometric degeneracy and match support; retain the case where rotation is correct but another component produces conflict. Pure-rotation or unstable-translation abstentions must remain visible in rotation coverage.

**Pinned G0 source check:** at MapAnything commit `3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9`, `mapanything/utils/inference.py:285` defines `postprocess_model_outputs_for_inference`; its lines 384–403 collect `depth_z`, `intrinsics`, `camera_poses` and `non_ambiguous_mask`, call `compute_multiview_depth_confidence` and replace `conf`. The callee is in `mapanything/utils/multiview_confidence.py:125`, with absolute/relative depth association defaults 0.02/0.02. All four retained TUM raw NPZs contain these inputs and the original learned `conf`. This identifies a possible forward-free recomputation path; it has **not been executed or validated**. Missing dependencies, restored tensor shapes/dtypes and equivalence with native postprocessing remain pending. Keep any recomputed G0 in new files and preserve learned C; the native depth mask is part of G0 and must be disclosed rather than used to prefilter C/G_pose inputs.

[MapAnything](https://github.com/facebookresearch/map-anything) documents native multiview confidence; [LightGlue's official implementation](https://github.com/cvg/LightGlue) supplies learned SIFT matching; [OpenCV's camera geometry documentation](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html) defines the robust geometry interfaces to pin. These sources establish available components, not performance on this protocol.

[Doppelgangers++](https://doppelgangers25.github.io/doppelgangers_plusplus/) and [XDG](https://github.com/xtcpete/xdg) remain strong comparisons if a distinct-physical-surface aliasing subset is actually established. Their pair-identity probabilities are not relative-rotation error labels. Keep their native task results separate and optionally evaluate their risk ranks on the common pose endpoint; an unrelated label cannot stand in for a pose-error baseline. Missing direct comparators permit a feasibility report, not a state-of-the-art or novelty claim.

## 4. Scene selection, splits and denominator integrity

Use `physical_scene_id` for a real place and static arrangement. Different sequences, timestamps, camera trajectories, resolutions or repeated captures in the same place share that ID. If two named datasets may overlap, join them in the same `physical_group_id` until evidence supports separation; unresolved identity cannot supply an independence count or cross-split separation. Related objects on the same tabletop do not automatically create independent scenes.

Select one ordinary four-image context per admitted scene using a deterministic reference-geometry/visibility rule before model execution. Keep only reference-based eligibility in this selection, never predicted confidence, errors or successful runs. Prefer four images with useful baseline and overlapping visible structure, store the exact selected filenames/hash/order and every exclusion. A separate stress context is allowed only if predefined from acquisition characteristics, shares the same scene group, and is reported separately from ordinary controls. The selector and pair list require a versioned freeze before inference.

All first-stage candidates are development observations. No random pair/frame split is valid. Later calibration and holdout partition whole physical groups; thresholds and CDFs are fitted only on calibration groups. Model-training overlap and prior benchmark exposure are separately recorded as known/inferred/unknown; scene-disjoint analysis here does not prove a dataset was unseen by pretrained weights.

Keep four quantities distinct: original scheduled pairs `N`, reference-labelable pairs `N_ref`, score-available pairs `N_score`, and retained usable pairs `N_retained`. Report label coverage `N_ref/N`, score coverage `N_score/N`, operational retention `N_retained/N`, unknown-reference count and missing-output rate. A missing score is never silently treated as a low-risk acceptance.

For a paired risk-ranking comparison, first freeze the common set of reference-labelable, score-available pairs for the compared methods. Use equal retained fractions 50%, 75%, 90% and 100% on that same set; round retained counts down and break equal-score ties by fixed pair ID. Do not claim end-to-end superiority from this common-set result alone: also report each method against the original `N`, where abstentions/missing outputs reduce delivered coverage. Show achieved counts because four-image contexts have coarse retention resolution.

At a deployable alarm operating point, select a risk threshold on calibration scenes with scene-macro false alarm on correct pairs no greater than 5%, maximizing error recall; ties prefer fewer false alarms, then a more conservative threshold. Report achieved per-scene false alarms and threshold precision limits. An all-retain threshold is an allowed result. Keep this fixed on heldout groups. Unknown labels do not enter correct/error denominators; eligible errors with no score count as missed errors in end-to-end error recall. False-alarm denominators include all eligible correct pairs and report their abstentions separately.

Report per-scene counts and risk/coverage curves, macro summaries first, micro summaries second. Any paired difference or uncertainty interval uses the physical group as the sampling unit, never six independent pairs from one context. A scene with no eligible errors has undefined error recall; retain its other metrics. No observed error, no observed false alarm, or a tiny pilot does not establish production reliability. Do not use an error-enriched stress subset to imply a natural-workflow precision.

## 5. Continue, stop and freeze checklist

- Proceed from reference inspection only when the admitted scene/group list, selected-image hashes, coordinate checks and uncertainty dispositions are reviewable. If fewer than six independently supported scenes are available, report the actual number and decide on a smaller feasibility stage; do not silently claim the 6–10 target passed.
- A supported hard-label comparison needs both correct and error labels. If independent reference uncertainty is unavailable, continue only as a descriptive reference-discrepancy study under an explicit revised scope. If errors are absent, keep the observation; a larger/different predefined acquisition stage requires a new allocation, not repeated selection until errors appear.
- G_pose can fail because matches, translation or geometry are degenerate; record abstention and coverage. A weak G_fit result only rejects that baseline/combination. Neither null result disproves every geometric diagnostic.
- Freeze actual score implementation, image list, direct baseline configurations, split, tolerances and resource caps before new inference. This draft leaves those admission items visibly incomplete. An existing weight hash and passed CPU check do not satisfy them.
- End the current stage on the allocated wall/download/storage/attempt limit, unrecoverable inputs, reference ineligibility or unobservable signal. Retain invalid attempts. Retries need an explicitly budgeted policy; no second resolution, second model or rescue tuning is implied.
- Use held-out effect sizes and uncertainty to decide whether further work is justified. Inconclusive small-sample evidence means inconclusive. Only a sufficiently discriminating comparison with no practically useful increment supports dropping the proposed combination.

Current conclusion: **protocol draft and preflight only; zero new inference runs, zero new error labels, zero newly admitted independent research scenes**. The first useful next result is a frozen reference/scene admission packet, followed by environment preparation inside a new bounded allocation.
