"""Run: python demo.py  -> two people in a snowfield, seen in two consecutive frames."""
from sar.cot import cot_marker
from sar.georef import Pose
from sar.pipeline import DetectionMap, process_frame
from sar.thermal import synthetic_frame

dmap = DetectionMap()
pose = Pose(lat=45.4215, lon=-75.6972, agl_m=60, yaw_deg=30)
for i in range(2):
    frame = synthetic_frame(people=((40 + i, 30), (120, 90)))
    for d in process_frame(frame, pose, dmap, t=i):
        print(f"frame {i}: det #{d['id']} {d['lat']:.6f},{d['lon']:.6f} conf={d['conf']} hits={d['hits']} ±{d['ce_m']} m")
print(dmap.geojson()[:120], "...")
print(cot_marker(dmap.items[0]["lat"], dmap.items[0]["lon"], "SAR-1", "thermal hotspot")[:120], "...")
