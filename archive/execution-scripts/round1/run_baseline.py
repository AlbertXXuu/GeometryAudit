"""Bounded engineering smoke; raw predictions and measured resources, no accuracy claim."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import traceback
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source/facebookresearch-map-anything-3d10cf7"
os.environ["TORCH_HOME"] = str(ROOT / "torch")
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["MPLCONFIGDIR"] = str(ROOT / "matplotlib-cache")
sys.path.insert(0, str(SOURCE))
sys.path.insert(0, str(SOURCE / "scripts"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="run-01")
    args = parser.parse_args()
    out = ROOT / args.output
    out.mkdir(exist_ok=False)
    import numpy as np
    import psutil
    import torch
    from mapanything.models import MapAnything
    from mapanything.utils.image import load_images

    torch.manual_seed(0)
    torch.set_num_threads(4)
    config = {
        "role": "GEO-P0.1 ordinary engineering smoke, not research validation",
        "protocol_version": "GEO-P0.1",
        "protocol_sha256": "1978a7d70b828f86393e98d57578d75ec80339895d1dafd2b56f5ed72f8c6f07",
        "upstream_commit": "3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9",
        "model_id": "facebook/map-anything-apache",
        "model_revision": "00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a",
        "input_order": ["motorcycle_left.png", "motorcycle_right.png"],
        "preprocess": {"resize_mode": "fixed_mapping", "resolution_set": 518},
        "inference": {"memory_efficient_inference": True, "minibatch_size": 1,
                      "use_amp": True, "amp_dtype": "bf16", "apply_mask": False,
                      "mask_edges": True, "apply_confidence_mask": False,
                      "use_multiview_confidence": False, "confidence_percentile": 10},
        "seed": 0, "cpu_threads": 4, "strict_checkpoint_load": True,
        "display_postprocess": {"apply_mask": True, "mask_edges": True, "apply_confidence_mask": False,
                                "use_multiview_confidence": False},
        "command": subprocess.list2cmdline([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]]),
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }
    (out / "config.json").write_text(json.dumps(config, indent=2))
    env = {"python": sys.version, "executable": sys.executable, "torch": torch.__version__,
           "cuda_runtime": torch.version.cuda, "cuda_available": torch.cuda.is_available(),
           "ram": dict(psutil.virtual_memory()._asdict()), "disk": dict(psutil.disk_usage(str(ROOT))._asdict()),
           "gpu": torch.cuda.get_device_name(0), "bf16_supported": torch.cuda.is_bf16_supported(),
           "gpu_inventory": subprocess.check_output(["nvidia-smi"], text=True)}
    (out / "environment.json").write_text(json.dumps(env, indent=2))
    done = threading.Event()
    samples = []
    started = time.perf_counter()
    stage = "model_load"
    proc = psutil.Process()

    def sample():
        while not done.is_set():
            row = {"elapsed_s": time.perf_counter() - started, "stage": stage,
                   "rss_bytes": proc.memory_info().rss}
            try:
                row["gpu_csv"] = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=memory.used,utilization.gpu,power.draw", "--format=csv,noheader,nounits"],
                    text=True, timeout=4).strip()
            except Exception as exc:
                row["gpu_sample_error"] = str(exc)
            samples.append(row)
            done.wait(1)

    monitor = threading.Thread(target=sample, daemon=True)
    monitor.start()
    result = {"status": "started", "accuracy_evaluation": "not performed"}
    try:
        print("Loading local pinned model", flush=True)
        model = MapAnything.from_pretrained(str(ROOT / "weights"), local_files_only=True, strict=True).to("cuda").eval()
        torch.cuda.synchronize()
        result["model_load_s"] = time.perf_counter() - started
        print("Loading images", flush=True)
        views = load_images([str(ROOT / "inputs" / name) for name in config["input_order"]],
                            **config["preprocess"], verbose=True)
        result["preprocessed_shapes"] = [list(view["img"].shape) for view in views]
        stage = "inference"
        torch.cuda.reset_peak_memory_stats()
        t = time.perf_counter()
        with torch.inference_mode():
            predictions = model.infer(views, **config["inference"])
        torch.cuda.synchronize()
        result["inference_s"] = time.perf_counter() - t
        result["torch_peak_allocated_bytes"] = torch.cuda.max_memory_allocated()
        result["torch_peak_reserved_bytes"] = torch.cuda.max_memory_reserved()
        stage = "export"
        t = time.perf_counter()
        for i, pred in enumerate(predictions):
            raw = {k: v.detach().float().cpu().numpy() if v.dtype == torch.bfloat16 else v.detach().cpu().numpy()
                   for k, v in pred.items() if isinstance(v, torch.Tensor)}
            np.savez_compressed(out / f"raw-view-{i:02d}.npz", **raw)
        from mapanything.utils.inference import postprocess_model_outputs_for_inference
        predictions = postprocess_model_outputs_for_inference(predictions, views, **config["display_postprocess"])
        arrays = []
        for i, pred in enumerate(predictions):
            converted = {k: v.detach().float().cpu().numpy() if v.dtype == torch.bfloat16 else v.detach().cpu().numpy()
                         for k, v in pred.items() if isinstance(v, torch.Tensor)}
            np.savez_compressed(out / f"view-{i:02d}.npz", **converted)
            arrays.append(converted)
        del predictions, model
        torch.cuda.empty_cache()
        result["views"] = []
        for arr in arrays:
            mask = arr["mask"].astype(bool)
            result["views"].append({"shape": list(arr["conf"].shape),
                "pixel_count": int(mask.size), "valid_pixels": int(mask.sum()),
                "confidence_finite_fraction": float(np.isfinite(arr["conf"]).mean()),
                "confidence_quantiles": np.quantile(arr["conf"], [0, .1, .5, .9, 1]).tolist(),
                "depth_finite_fraction": float(np.isfinite(arr["depth_z"]).mean()),
                "camera_pose": arr["camera_poses"].tolist(), "intrinsics": arr["intrinsics"].tolist(),
                "saved_keys": sorted(arr)})
        from export_replay import export
        export(out)
        result["export_s"] = time.perf_counter() - t
        result["status"] = "success"
    except Exception as exc:
        result.update(status="failed", failed_stage=stage, error_type=type(exc).__name__, error=str(exc))
        (out / "traceback.txt").write_text(traceback.format_exc())
        traceback.print_exc()
    finally:
        done.set()
        monitor.join(timeout=6)
        result["total_s"] = time.perf_counter() - started
        result["peak_sampled_process_rss_bytes"] = max((x["rss_bytes"] for x in samples), default=None)
        result["resource_sample_period_s"] = 1
        result["gpu_memory_scope"] = "nvidia-smi includes other desktop processes; torch peaks are allocator counters for this process"
        (out / "resources.json").write_text(json.dumps(samples, indent=2))
        (out / "result.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2), flush=True)
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
