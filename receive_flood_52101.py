#!/usr/bin/env python3

import os
import sys
import json
import socket
import subprocess
from pathlib import Path


# ============================================================
# Project / MAVLink setup
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
LOCAL_MAVLINK = PROJECT_ROOT / "modules" / "mavlink"

sys.path.insert(0, str(LOCAL_MAVLINK))

os.environ["MAVLINK20"] = "1"
os.environ["MAVLINK_DIALECT"] = "ardupilotmega"

from pymavlink import mavutil


# ============================================================
# B: MAVLink receiver
# ============================================================

MAVLINK_PORT = 14551


# ============================================================
# C: Windows SQLite receiver
# ============================================================

DB_UDP_PORT = 14552


def get_windows_host():
    """
    取得 WSL 對應的 Windows Host IP。

    優先使用環境變數 FLOOD_DB_HOST。
    若沒有指定，自動由 WSL default gateway 取得。
    """

    manual_host = os.environ.get("FLOOD_DB_HOST")

    if manual_host:
        return manual_host

    try:
        output = subprocess.check_output(
            ["ip", "route", "show", "default"],
            text=True
        ).strip()

        parts = output.split()

        if "via" in parts:
            index = parts.index("via")
            return parts[index + 1]

    except Exception:
        pass

    raise RuntimeError(
        "Cannot detect Windows Host IP. "
        "Please set FLOOD_DB_HOST manually."
    )


WINDOWS_HOST = get_windows_host()


# ============================================================
# FloodResult validation
# ============================================================

def validate_result(result):
    """
    驗證 FloodResult 九欄是否在合理範圍。
    不再比對固定測試值。
    """

    if result["timestamp"] <= 0:
        return False, "timestamp must be > 0"

    if not 0.0 <= result["water_coverage_pct"] <= 100.0:
        return False, "water_coverage_pct out of range"

    if not 0.0 <= result["road_water_pct"] <= 100.0:
        return False, "road_water_pct out of range"

    if result["water_region_count"] < 0:
        return False, "water_region_count must be >= 0"

    if result["flood_level"] not in (0, 1, 2, 3):
        return False, "flood_level must be 0~3"

    if not 0.0 <= result["confidence"] <= 1.0:
        return False, "confidence out of range"

    if not -90.0 <= result["latitude"] <= 90.0:
        return False, "latitude out of range"

    if not -180.0 <= result["longitude"] <= 180.0:
        return False, "longitude out of range"

    if result["inference_fps"] < 0:
        return False, "inference_fps must be >= 0"

    return True, "OK"


# ============================================================
# UDP sender B -> C
# ============================================================

forward_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

last_forward_key = None


# ============================================================
# Startup information
# ============================================================

print("=" * 60)
print(" RAW MAVLink 52101 Receiver + B -> C Forwarder")
print("=" * 60)
print(f"MAVLink listen     : 0.0.0.0:{MAVLINK_PORT}")
print("Expected message   : AI_FLOOD_DETECTION_RESULT")
print("Expected MSG ID    : 52101")
print("Expected fields    : 9")
print(f"Windows C target   : {WINDOWS_HOST}:{DB_UDP_PORT}")
print("=" * 60)
print()
print("Waiting for RAW 52101 ...")
print()


# ============================================================
# MAVLink connection
# ============================================================

master = mavutil.mavlink_connection(
    f"udpin:0.0.0.0:{MAVLINK_PORT}"
)


# ============================================================
# Main loop
# ============================================================

while True:

    msg = master.recv_match(
        type="AI_FLOOD_DETECTION_RESULT",
        blocking=True
    )

    if msg is None:
        continue


    # --------------------------------------------------------
    # Check MAVLink message ID
    # --------------------------------------------------------

    if msg.get_msgId() != 52101:
        print(
            "REJECT: unexpected MAVLink message ID:",
            msg.get_msgId()
        )
        continue


    # --------------------------------------------------------
    # Convert MAVLink message -> standard FloodResult
    # --------------------------------------------------------

    result = {
        "timestamp": int(msg.timestamp),
        "water_coverage_pct": float(msg.water_coverage_pct),
        "road_water_pct": float(msg.road_water_pct),
        "water_region_count": int(msg.water_region_count),
        "flood_level": int(msg.flood_level),
        "confidence": float(msg.confidence),
        "latitude": float(msg.latitude),
        "longitude": float(msg.longitude),
        "inference_fps": float(msg.inference_fps),
    }


    # --------------------------------------------------------
    # Display received data
    # --------------------------------------------------------

    print("=" * 60)
    print(" RAW 52101 RECEIVED")
    print("=" * 60)

    print("Message type         :", msg.get_type())
    print("Message ID           :", msg.get_msgId())
    print()

    print("1. timestamp           =", result["timestamp"])
    print("2. water_coverage_pct  =", result["water_coverage_pct"])
    print("3. road_water_pct      =", result["road_water_pct"])
    print("4. water_region_count  =", result["water_region_count"])
    print("5. flood_level         =", result["flood_level"])
    print("6. confidence          =", result["confidence"])
    print("7. latitude            =", result["latitude"])
    print("8. longitude           =", result["longitude"])
    print("9. inference_fps       =", result["inference_fps"])

    print()


    # --------------------------------------------------------
    # Validate FloodResult
    # --------------------------------------------------------

    valid, reason = validate_result(result)

    if not valid:

        print("FloodResult validation : FAIL")
        print("Reason                 :", reason)
        print("Forward to C           : SKIPPED")
        print("=" * 60)
        print()

        continue


    print("FloodResult validation : PASS")

    dedup_key = tuple(result.values())

    if dedup_key == last_forward_key:
        print("Duplicate check         : DUPLICATE")
        print("Forward to C           : SKIPPED")
        print("=" * 60)
        print()
        continue

    print("Duplicate check         : PASS")


    # --------------------------------------------------------
    # Convert FloodResult -> JSON
    # --------------------------------------------------------

    payload = json.dumps(
        result,
        ensure_ascii=False
    ).encode("utf-8")


    # --------------------------------------------------------
    # Forward B -> C
    # --------------------------------------------------------

    try:

        sent = forward_socket.sendto(
            payload,
            (WINDOWS_HOST, DB_UDP_PORT)
        )

        print(
            "Forward to C           : PASS"
        )

        print(
            f"Target                 : "
            f"{WINDOWS_HOST}:{DB_UDP_PORT}"
        )

        print(
            "UDP bytes              :",
            sent
        )

        last_forward_key = dedup_key

    except Exception as exc:

        print(
            "Forward to C           : FAIL"
        )

        print(
            "Reason                 :",
            exc
        )


    print("=" * 60)
    print()
