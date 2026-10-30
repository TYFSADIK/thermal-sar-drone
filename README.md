# Thermal Search-and-Rescue Drone

Private research repo. An X500-class quadcopter with a FLIR Lepton thermal camera and Hailo AI HAT+ edge detection. It finds people in snow and brush and pushes detections to a live map.

Full write-up: [`docs/project-page.md`](docs/project-page.md)

## What's here

| File | Purpose |
|---|---|
| `sar/thermal.py` | Radiometric hotspot detector (centikelvin to °C, background contrast, blob filter) and a synthetic snowfield generator |
| `sar/georef.py` | Near-nadir pixel-to-lat/lon projection and a position error budget |
| `sar/pipeline.py` | Frame to detections, merging repeat sightings across frames, GeoJSON export |
| `sar/cot.py` | Cursor-on-Target markers for ATAK/WinTAK |
| `sar/hailo_infer.py` | Placeholder for the Hailo `.hef` model, so you can compare it with the threshold baseline |

## Quickstart

```bash
pip install -r requirements.txt
python demo.py && python -m unittest -v
```

## Next steps
- [ ] Capture Lepton frames on the Pi (`pylepton` or PureThermal UVC, Y16 radiometric) and save them to `data/` with pose
- [ ] Time-sync: tag every frame with the MAVLink `ATTITUDE` + `GLOBAL_POSITION_INT` nearest in time (pymavlink)
- [ ] Field test: place volunteers at surveyed points and report detection rate and position error vs AGL
- [ ] Tune `body_range_c` and `min_contrast_c` per season (summer brush is much harder than snow)
- [ ] Push CoT to the TAK server from the drone and show it live on ATAK

Fly under Transport Canada rules (Part IX). Get consent from volunteers before capturing them.
