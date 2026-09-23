"""Use Rerun's existing layout API to separate RGB from its depth overlay."""
from pathlib import Path
import rerun.blueprint as b

root=Path(__file__).resolve().parent
layout=b.Blueprint(
    b.Horizontal(
        b.Spatial3DView(origin='/mapanything',name='TUM fr1/xyz — four-view reconstruction'),
        b.Vertical(
            b.Spatial2DView(origin='/mapanything/camera_0/pinhole',contents=['$origin/rgb'],name='Input 0 — TUM CC BY 4.0'),
            b.Spatial2DView(origin='/mapanything/camera_3/pinhole',contents=['$origin/rgb'],name='Input 3 — TUM CC BY 4.0'))),
    collapse_panels=True)
layout.save('MapAnything_TUM_fr1_xyz_P0_4views',str(root/'run-518/viewer.rbl'))
print('Saved native Rerun layout; all four views remain in the recording')
