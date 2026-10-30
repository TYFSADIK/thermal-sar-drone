"""Frame -> hotspots -> georeferenced detections -> de-duplicated map markers."""
import json
import math
import time

from .georef import Pose, pixel_to_ground, position_error_m
from .thermal import find_hotspots


class DetectionMap:
    """Merges repeat sightings of the same person across frames (within merge_m)."""

    def __init__(self, merge_m=8.0):
        self.merge_m = merge_m
        self.items = []

    def add(self, lat, lon, conf, t):
        for it in self.items:
            dn = (lat - it["lat"]) * 111320
            de = (lon - it["lon"]) * 111320 * math.cos(math.radians(lat))
            if math.hypot(dn, de) < self.merge_m:
                k = it["hits"]
                it["lat"] = (it["lat"] * k + lat) / (k + 1)
                it["lon"] = (it["lon"] * k + lon) / (k + 1)
                it["hits"] += 1
                it["conf"] = max(it["conf"], conf)
                it["last"] = t
                return it
        it = {"id": len(self.items) + 1, "lat": lat, "lon": lon, "conf": conf, "hits": 1, "first": t, "last": t}
        self.items.append(it)
        return it

    def geojson(self):
        return json.dumps({"type": "FeatureCollection", "features": [
            {"type": "Feature", "geometry": {"type": "Point", "coordinates": [i["lon"], i["lat"]]},
             "properties": {k: v for k, v in i.items() if k not in ("lat", "lon")}} for i in self.items]})


def process_frame(frame_c, pose: Pose, dmap: DetectionMap, t=None):
    t = t or time.time()
    out = []
    for h in find_hotspots(frame_c):
        lat, lon, gsd = pixel_to_ground(h.cx, h.cy, pose)
        conf = min(1.0, h.contrast_c / 30.0) * min(1.0, h.area_px / 10.0)
        it = dmap.add(lat, lon, round(conf, 2), t)
        out.append({**it, "ce_m": round(position_error_m(pose.agl_m), 1), "gsd_m": round(gsd, 2)})
    return out
