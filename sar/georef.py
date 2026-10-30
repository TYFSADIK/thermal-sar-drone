"""Pixel -> ground lat/lon with the simplified near-nadir projection model.

Assumptions (the big error sources, in order):
  1. Flat ground at the takeoff altitude (no DEM)
  2. Camera pointing straight down apart from the measured roll/pitch
  3. GNSS and attitude logged at the same instant as the frame (time sync!)
"""
import math
from dataclasses import dataclass

EARTH_R = 6371000.0


@dataclass
class Pose:
    lat: float
    lon: float
    agl_m: float
    yaw_deg: float     # heading, 0 = north, clockwise
    pitch_deg: float = 0.0
    roll_deg: float = 0.0


def pixel_to_ground(px, py, pose: Pose, width=160, height=120, hfov_deg=57.0):
    """Return (lat, lon, ground_sample_distance_m)."""
    f = (width / 2) / math.tan(math.radians(hfov_deg) / 2)   # focal length in pixels
    # camera frame: x right, y forward (top of image = forward), z down
    ang_x = math.atan((px - width / 2) / f) + math.radians(pose.roll_deg)
    ang_y = math.atan((height / 2 - py) / f) + math.radians(pose.pitch_deg)
    right = pose.agl_m * math.tan(ang_x)
    fwd = pose.agl_m * math.tan(ang_y)
    yaw = math.radians(pose.yaw_deg)
    north = fwd * math.cos(yaw) - right * math.sin(yaw)
    east = fwd * math.sin(yaw) + right * math.cos(yaw)
    lat = pose.lat + math.degrees(north / EARTH_R)
    lon = pose.lon + math.degrees(east / (EARTH_R * math.cos(math.radians(pose.lat))))
    return lat, lon, pose.agl_m / f


def position_error_m(agl_m, attitude_err_deg=2.0, gnss_err_m=2.5, alt_err_m=1.0, off_nadir_deg=20.0):
    """Rough 1-sigma error budget for a detection, for the spec-gap table."""
    att = agl_m * math.tan(math.radians(attitude_err_deg))
    alt = alt_err_m * math.tan(math.radians(off_nadir_deg))
    return math.sqrt(att ** 2 + gnss_err_m ** 2 + alt ** 2)
