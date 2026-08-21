#!/usr/bin/env python3

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
LOCAL_MAVLINK = PROJECT_ROOT / "modules" / "mavlink"

sys.path.insert(0, str(LOCAL_MAVLINK))

os.environ["MAVLINK20"] = "1"
os.environ["MAVLINK_DIALECT"] = "ardupilotmega"

from pymavlink import mavutil


PORT = 14551

print("==================================================")
print(" RAW MAVLink 52101 Receiver")
print("==================================================")
print(f"Listening UDP port : {PORT}")
print("Expected message   : AI_FLOOD_DETECTION_RESULT")
print("Expected MSG ID    : 52101")
print("Expected fields    : 9")
print("==================================================")
print()
print("Waiting for RAW 52101 ...")
print()

master = mavutil.mavlink_connection(
    f"udpin:0.0.0.0:{PORT}"
)

while True:
    msg = master.recv_match(
        type="AI_FLOOD_DETECTION_RESULT",
        blocking=True
    )

    if msg is None:
        continue

    print("==================================================")
    print(" RAW 52101 RECEIVED")
    print("==================================================")

    print("Message type       :", msg.get_type())
    print("Message ID         :", msg.get_msgId())
    print()

    print("1. timestamp           =", msg.timestamp)
    print("2. water_coverage_pct  =", msg.water_coverage_pct)
    print("3. road_water_pct      =", msg.road_water_pct)
    print("4. water_region_count  =", msg.water_region_count)
    print("5. flood_level         =", msg.flood_level)
    print("6. confidence          =", msg.confidence)
    print("7. latitude            =", msg.latitude)
    print("8. longitude           =", msg.longitude)
    print("9. inference_fps       =", msg.inference_fps)

    print()
    print("==================================================")

    expected_ok = (
        msg.get_msgId() == 52101
        and abs(msg.water_coverage_pct - 25.3) < 0.1
        and abs(msg.road_water_pct - 42.8) < 0.1
        and msg.water_region_count == 2
        and msg.flood_level == 2
        and abs(msg.confidence - 0.91) < 0.01
        and abs(msg.latitude - 22.6701) < 0.001
        and abs(msg.longitude - 120.4881) < 0.001
        and abs(msg.inference_fps - 15.7) < 0.1
    )

    if expected_ok:
        print("PASS: RAW 52101 + FloodResult 9 fields received")
    else:
        print("FAIL: 52101 received, but one or more values differ")

    print("==================================================")
    print()

    break
