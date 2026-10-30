"""Cursor-on-Target (CoT) XML for ATAK/WinTAK markers, sent over UDP multicast or TCP."""
import socket
import uuid
from datetime import datetime, timedelta, timezone


def _iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def cot_marker(lat, lon, callsign, remarks="", cot_type="a-u-G", ce_m=10.0, stale_s=300, uid=None):
    """a-u-G = unknown ground point. Use 'b-m-p-s-p-i' for a spot/point of interest."""
    now = datetime.now(timezone.utc)
    uid = uid or f"det-{uuid.uuid4()}"
    return (f'<?xml version="1.0" encoding="UTF-8"?>'
            f'<event version="2.0" uid="{uid}" type="{cot_type}" how="m-g" time="{_iso(now)}" '
            f'start="{_iso(now)}" stale="{_iso(now + timedelta(seconds=stale_s))}">'
            f'<point lat="{lat:.7f}" lon="{lon:.7f}" hae="0" ce="{ce_m:.1f}" le="9999999"/>'
            f'<detail><contact callsign="{callsign}"/><remarks>{remarks}</remarks></detail></event>')


def send_udp(xml: str, host="239.2.3.1", port=6969):
    """Default ATAK SA multicast. Use your TAK server's TCP input in the field."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    s.sendto(xml.encode(), (host, port))
    s.close()
