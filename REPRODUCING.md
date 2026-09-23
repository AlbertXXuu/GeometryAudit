# Reproducing the P0 records

## CPU result verification

The root README commands work on a standalone checkout. The required NumPy version is in `requirements.txt`. `scripts/review_recorded.py` reads the committed TUM selection, model camera matrices and accepted comparison; it does not read another project, download images or run inference. Its numerical result matches the accepted six rotation/five translation entries within 1e-8 degrees.

This is a recalculation from recorded cameras. Repeating inference from images is a separate, more expensive operation. The original raw-array reviews are retained under `reports/` and their source hashes under `provenance.json`.

## GPU environment and external assets

The original environment used Python 3.11.0, CUDA-enabled PyTorch 2.5.1+cu118, NumPy 2.1.2, an RTX 4060 Laptop reporting 8188 MiB, BF16, `minibatch_size=1` and memory-efficient inference. Additional packages were frozen in [the recorded dependency list](archive/requirements-gpu-recorded.txt). That file supplements the base PyTorch/NumPy environment; it is not a claim that every transitive wheel remains available on every platform.

Create an isolated GPU environment and install the CUDA PyTorch build appropriate to the recorded runtime, followed by that dependency list. Do not install into a shared Python environment. No fresh GPU installation or inference was performed during this repository's packaging.

Use `.local/` for external artifacts, or set `GEOMETRY_AUDIT_ARTIFACTS` to an existing archive with this layout:

```text
<artifact-root>/
  round1/
    source/facebookresearch-map-anything-3d10cf7/
    weights/                         # model.safetensors + pinned model configuration
    torch/hub/                       # pinned DINOv2 Torch Hub source cache
    inputs/motorcycle_left.png
    inputs/motorcycle_right.png
    inputs-manifest.json
    model-metadata.json
    viewer/rerun.exe                 # optional Windows Rerun 0.24.1 executable
    run-02/                         # original local output, if retained
  tum-p0/
    inputs/                         # four PNG names and hashes from selection.json
    selection.json
    selection.sha256
    torch/hub/                       # same pinned DINOv2 source revision
    run-518/                        # original local output, if retained
```

All these large/input assets stay outside Git. Existing AlvenX P0 archives already use this layout, so they can be reused without copying weights or altering the original evidence.

| Dependency | Recorded source |
| --- | --- |
| MapAnything | [commit 3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9](https://github.com/facebookresearch/map-anything/tree/3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9) |
| Apache model | [revision 00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a](https://huggingface.co/facebook/map-anything-apache/tree/00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a), weight SHA256 `fa06c0fdccefc5048e072c85935d5789b1e36b307f3859033c17f9dcb9fd5201` |
| DINOv2 architecture | [commit 7764ea0f912e53c92e82eb78a2a1631e92725fc8](https://github.com/facebookresearch/dinov2/tree/7764ea0f912e53c92e82eb78a2a1631e92725fc8); the original Torch Hub cache directory is `facebookresearch_dinov2_main` but its contents were pinned to this commit |
| Motorcycle RGB | URLs and SHA256 in [inputs-manifest.json](records/motorcycle/inputs-manifest.json); source is scikit-image 0.25.2 |
| TUM fr1/xyz | [official dataset](https://cvg.cit.tum.de/data/datasets/rgbd-dataset/download#freiburg1_xyz); original archive SHA256 `a0236d97b8c30cd93b653656d2b6c293ff7c982a4130ef2a1a8beecdb124ef98` |

For a fresh artifact directory, obtain those pinned upstream distributions using their official tools and verify the hashes. Copy the two small Motorcycle metadata files from `records/motorcycle/`. For TUM, reproduce the fixed selection in [selection.json](records/tum/selection.json): nearest RGB frames at +2.0/+2.5/+3.0/+3.5 seconds, no repeated images, RGB tolerance 0.05 seconds and GT tolerance 0.02 seconds. Verify each selected PNG against its recorded hash before copying the selection and its checksum. Obtain only the required assets under their respective terms; model/code licenses do not grant rights to photographs.

The original data-selection code is preserved in `archive/execution-scripts/tum-p0/prepare_tum.py` for inspection. Its task-specific deadline and cleanup paths are historical, so it is not the current data-acquisition command. The active CPU verification is complete and self-contained; fresh model asset preparation remains an explicit manual prerequisite.

## Run a new inference

With the recorded environment and verified external assets available:

```powershell
$env:GEOMETRY_AUDIT_ARTIFACTS = 'C:\path\to\geometry-audit-artifacts'
python scripts/motorcycle/verify_artifacts.py --inputs-only
python scripts/motorcycle/run_baseline.py --output replay-motorcycle-001
python scripts/tum/run_tum.py --output replay-tum-001
```

Each command creates a new directory below its case root. Existing run directories are preserved. The maintained scripts differ from the original execution copies only in artifact-root selection, explicit safe output names and a rerun marker. Original model/preprocessing settings, raw-before-display export order and measurements are retained. Do not interpret a new execution as the original preregistered run.

Recorded R1 used P0.1; TUM used P0.2. Exact original protocol bytes are under `archive/protocols/`. The `docs/` copies only relocate internal publication links. The historical `run_with_budget.py` is evidence of the 2026-09-22 allocation; it does not grant or configure a fresh run budget.

## Replay an existing recording

Using the retained Windows viewer, no Python model environment is required:

```powershell
& "$env:GEOMETRY_AUDIT_ARTIFACTS/round1/viewer/rerun.exe" --serve-web --bind 127.0.0.1 --port 9878 --web-viewer-port 9092 "$env:GEOMETRY_AUDIT_ARTIFACTS/tum-p0/run-518/scene.rrd"
```

Open the local URL printed by Rerun and stop the service with Ctrl+C. The original Web replay was checked; this projectization did not repeat viewer interaction. Original NPZ cameras use OpenCV camera-to-world coordinates. GLB applies a 180-degree X-axis display transform and must not be substituted in the pose comparison.
