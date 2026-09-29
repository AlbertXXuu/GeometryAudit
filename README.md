<p align="center">
  <img src="docs/assets/alvenx-wordmark.svg" width="320" alt="AlvenX">
  <br>
  <sub>GEOMETRY EVIDENCE</sub>
</p>

# GeometryAudit

Reproducible experiments for auditing foundation-model multiview geometry. This repository contains the recorded MapAnything Apache P0 runs, their protocols, and an independently checkable relative-pose calculation.

Status: **recorded experiments and reproducibility evidence**. Two engineering cases are recorded: Motorcycle stereo and one four-frame TUM `freiburg1_xyz` window. On **2026-09-26**, the current reliability-adapter research candidate (`CAND-GEO-01`) was retired following a prior-art review of GeoCond. See the [decision and its limits](docs/PRIOR-ART-DECISION-2026-09-26.md). The recorded experiments remain available; they do not establish ambiguity diagnosis, confidence complementarity or repair gains.

## Recorded results

| Case | Model inputs | Synchronized inference | Accepted evidence |
| --- | --- | --- | --- |
| Motorcycle | 2 × 518×336 | 11.050 s | Raw/display consistency, camera format, exports and replay |
| TUM fr1/xyz | 4 × 518×392 | 11.870 s | Six relative rotations; five eligible translation directions |

Both are single runs on an RTX 4060 Laptop reporting 8188 MiB. Timing excludes model loading, export and setup. The four-view run used standard `fixed_mapping=518`; 392 is its image height. TUM pairs share cameras and are not six independent scenes. Reference noise has not been independently bounded.

The TUM recorded rotation errors span **0.585605–3.021899°**, and eligible translation-direction errors span **5.493252–8.439680°**. Pair 1–2 has a 0.026964 m reference baseline and remains ineligible for translation evaluation. These are ordinary-scene reference comparisons, not diagnostic or repair gains.

## Recompute the recorded pose comparison

Python 3.11 and NumPy are sufficient; no model, image download or GPU is needed:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe scripts/review_recorded.py
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe scripts/check_repository.py
```

On Linux/macOS use `.venv/bin/python` instead. `review_recorded.py` rebuilds reference rotations from the recorded xyzw quaternions, computes `solve(T_j, T_i)` from recorded model cameras, and compares all six pairs with the accepted report. It leaves committed records unchanged. `--output <new-file.json>` optionally saves a separate recalculation.

This checks the published numeric record. The earlier independent review also checked the original NPZ arrays and complete frozen selection metadata; see the TUM review in [English](reports/REPORT_TUM_P0.en.md) or [简体中文](reports/REPORT_TUM_P0.md).

## Run the model or replay local artifacts

The supported local artifact layout and pinned external dependencies are described in [REPRODUCING.md](REPRODUCING.md). The GPU entry points are:

```powershell
python scripts/motorcycle/run_baseline.py --help
python scripts/tum/run_tum.py --help
```

Model weights, input photographs and raw NPZ/GLB/RRD files are external artifacts. The maintained runners accept their common location through `GEOMETRY_AUDIT_ARTIFACTS`, defaulting to this repository's ignored `.local/` directory. Fresh inference always needs a new output directory. Packaging validation did not rerun the GPU model or perform a fresh GPU environment installation.

## Evidence and provenance

Research preparation was closed **2026-09-26** after the prior-art decision. The unexecuted
[relative-pose audit draft](docs/PROTOCOL-NEXT.md) and [candidate register](docs/SCENE-CANDIDATES.md)
are retained as historical preparation. They are not an active experiment queue. None of the
eight source entries was admitted as a new independently referenced physical scene.

The recorded pose recalculation, eight CPU tests and 42 imported-file hashes passed again.
Local preflight found the retained model checkpoint intact and CUDA available, but the former
temporary model environment is absent and required inference packages are missing. No new
model inference or scene admission was completed. The proposed new experiment is now stopped;
a future research effort needs a separately justified question and decision. The original
protocols, archived scripts and imported results remain unchanged.

- [Protocol GEO-P0.2](docs/PROTOCOL.md), [historical P0.1](docs/PROTOCOL_GEO-P0.1.md), [method landscape](docs/LANDSCAPE.md).
- Motorcycle review: [English](reports/REPORT.en.md) · [简体中文](reports/REPORT.md).
- TUM review: [English](reports/REPORT_TUM_P0.en.md) · [简体中文](reports/REPORT_TUM_P0.md).
- [Motorcycle records](records/motorcycle/), [TUM records](records/tum/), [original-to-repository provenance](provenance.json).
- `archive/` preserves the exact original execution scripts, including historical one-run budgets. They document the original run; the current entry points are under `scripts/`.
- [Data/model attribution](THIRD_PARTY_NOTICES.md). No input photograph or third-party model/source distribution is bundled.

The website is the presentation layer: [AlvenX research note](https://alvenx.com/notes/2026-09-22-multiview-geometry). This repository carries the experiment code and evidence, including the subsequently reviewed TUM result.

The English reports are complete translations of the dated Chinese originals. The originals and their recorded evidence remain unchanged; each translation links back to its source and this bilingual index.
