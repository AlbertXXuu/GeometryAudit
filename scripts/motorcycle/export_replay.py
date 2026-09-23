"""Re-export saved model tensors with the upstream GLB and Rerun helpers."""
from pathlib import Path
import os
import sys

ARTIFACTS = Path(os.environ.get("GEOMETRY_AUDIT_ARTIFACTS", str(Path(__file__).resolve().parents[2] / ".local"))).resolve()
ROOT = ARTIFACTS / "round1"
SOURCE = ROOT / "source/facebookresearch-map-anything-3d10cf7"
sys.path[:0] = [str(SOURCE), str(SOURCE / "scripts")]
os.environ["MPLCONFIGDIR"] = str(ROOT / "matplotlib-cache")


def export(out):
    import numpy as np
    import rerun as rr
    from mapanything.utils.viz import predictions_to_glb
    from demo_images_only_inference import log_data_to_rerun
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    arrays = []
    for path in sorted(out.glob("view-*.npz")):
        with np.load(path, allow_pickle=False) as z:
            arrays.append({key: z[key] for key in z.files})
    rr.init("MapAnything_Motorcycle_round1", spawn=False)
    rr.save(str(out / "scene.rrd"))
    rr.log("mapanything", rr.ViewCoordinates.RDF, static=True)
    world, colors, masks = [], [], []
    fig, axes = plt.subplots(len(arrays), 3, figsize=(12, 6), constrained_layout=True)
    for i, arr in enumerate(arrays):
        image = arr["img_no_norm"][0]
        points = arr["pts3d"][0]
        mask = arr["mask"][0, ..., 0].astype(bool) & np.isfinite(points).all(axis=-1)
        depth = arr["depth_z"][0, ..., 0]
        conf = arr["conf"][0]
        log_data_to_rerun(image, depth, arr["camera_poses"][0], arr["intrinsics"][0],
                         points, mask, f"mapanything/camera_{i}", f"mapanything/points_{i}")
        rr.log(f"diagnostics/view_{i}/learned_confidence", rr.Tensor(conf))
        world.append(points)
        colors.append(image.copy())
        masks.append(mask)
        axes[i, 0].imshow(image.clip(0, 1)); axes[i, 0].set_title(f"View {i}: model input")
        im = axes[i, 1].imshow(depth, cmap="viridis")
        axes[i, 1].set_title("Predicted depth (model metric scale)"); fig.colorbar(im, ax=axes[i, 1], shrink=.7)
        im = axes[i, 2].imshow(conf, cmap="magma")
        axes[i, 2].set_title("Learned confidence (not probability)"); fig.colorbar(im, ax=axes[i, 2], shrink=.7)
        for axis in axes[i]: axis.set_axis_off()
    fig.suptitle("MapAnything Apache | Motorcycle stereo pair | Engineering smoke\nActual model outputs; geometric accuracy not evaluated", fontsize=12)
    fig.savefig(out / "diagnostics.png", dpi=160); plt.close(fig)
    rr.disconnect()
    scene = predictions_to_glb({"world_points": np.stack(world), "images": np.stack(colors),
                                "final_masks": np.stack(masks)}, as_mesh=False)
    scene.export(str(out / "scene.glb"))


if __name__ == "__main__":
    export(Path(sys.argv[1]).resolve())
