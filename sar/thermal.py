"""Hotspot detection on radiometric thermal frames (FLIR Lepton 3.5: 160x120, centikelvin).

Pipeline: centikelvin -> Celsius -> adaptive threshold above scene background
-> connected blobs -> size and temperature filters -> detections.
"""
from dataclasses import dataclass

import numpy as np

LEPTON_W, LEPTON_H = 160, 120
LEPTON_HFOV_DEG = 57.0   # Lepton 3.5 horizontal FOV (check your module)


@dataclass
class Hotspot:
    cx: float            # pixel column (sub-pixel centroid)
    cy: float            # pixel row
    area_px: int
    peak_c: float
    mean_c: float
    contrast_c: float    # peak minus scene background


def centikelvin_to_c(frame: np.ndarray) -> np.ndarray:
    return frame.astype(np.float32) / 100.0 - 273.15


def _label(mask: np.ndarray):
    """4-connected component labelling without scipy."""
    labels = np.zeros(mask.shape, dtype=np.int32)
    cur = 0
    h, w = mask.shape
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not labels[y, x]:
                cur += 1
                stack = [(y, x)]
                labels[y, x] = cur
                while stack:
                    cy, cx = stack.pop()
                    for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not labels[ny, nx]:
                            labels[ny, nx] = cur
                            stack.append((ny, nx))
    return labels, cur


def find_hotspots(frame_c: np.ndarray, min_contrast_c=6.0, min_area=2, max_area=400,
                  body_range_c=(20.0, 40.0)) -> list[Hotspot]:
    """Find warm blobs. body_range_c is the apparent temperature of exposed skin/clothing.

    Apparent temperature through clothing in winter is often only 20-30 C, so
    the range is wide on purpose. Tune it against your own captures.
    """
    background = float(np.median(frame_c))
    mask = (frame_c - background) >= min_contrast_c
    labels, n = _label(mask)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(labels == i)
        area = len(xs)
        if not (min_area <= area <= max_area):
            continue
        vals = frame_c[ys, xs]
        peak = float(vals.max())
        if not (body_range_c[0] <= peak <= body_range_c[1]):
            continue
        w = vals - background
        out.append(Hotspot(float((xs * w).sum() / w.sum()), float((ys * w).sum() / w.sum()), area,
                           peak, float(vals.mean()), peak - background))
    return sorted(out, key=lambda h: -h.contrast_c)


def synthetic_frame(people=((80, 60),), background_c=-15.0, person_c=28.0, rng=None):
    """Snowfield at background_c with warm 3x5 px 'people' (approx. 1.7 m at 60 m AGL)."""
    rng = rng or np.random.default_rng(0)
    f = rng.normal(background_c, 0.8, (LEPTON_H, LEPTON_W)).astype(np.float32)
    for (x, y) in people:
        f[y - 2:y + 3, x - 1:x + 2] = person_c + rng.normal(0, 0.5, (5, 3))
    return f
