#!/usr/bin/env python3

import os
import sys
import time
from pathlib import Path

# ============================================================
# 使用專案自己的 pymavlink / ardupilotmega dialect
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOCAL_MAVLINK = PROJECT_ROOT / "modules" / "mavlink"

sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(LOCAL_MAVLINK))

os.environ["MAVLINK20"] = "1"
os.environ["MAVLINK_DIALECT"] = "ardupilotmega"

from pymavlink import mavutil

from shared.flood_result import FloodResult


# ============================================================
# MAVLink connection
# ============================================================

CONNECTION = "tcp:127.0.0.1:5762"
SOURCE_SYSTEM = 1
SOURCE_COMPONENT = 211

_master = None


def _get_master():
    global _master

    if _master is None:
        _master = mavutil.mavlink_connection(
            CONNECTION,
            source_system=SOURCE_SYSTEM,
            source_component=SOURCE_COMPONENT
        )

    return _master


# ============================================================
# B 對外正式介面
# ============================================================

def send_flood_mavlink(result):
    """
    將標準 FloodResult 透過 MAVLink 52101 傳送給 ArduPilot。
    """

    master = _get_master()

    master.mav.ai_flood_detection_result_send(
        int(result.timestamp),
        float(result.water_coverage_pct),
        float(result.road_water_pct),
        int(result.water_region_count),
        int(result.flood_level),
        float(result.confidence),
        float(result.latitude),
        float(result.longitude),
        float(result.inference_fps)
    )


# ============================================================
# 單獨執行時的 Fake W2 測試
# ============================================================

def main():

    print("==============================================")
    print(" AI FLOOD MAVLink Sender")
    print("==============================================")
    print(f"Connection : {CONNECTION}")
    print(f"System ID  : {SOURCE_SYSTEM}")
    print(f"Component  : {SOURCE_COMPONENT}")
    print("Message ID : 52101")
    print("Fields     : 9")
    print("==============================================")
    print("Sending Fake W2 FloodResult ...")
    print("Press Ctrl+C to stop.")
    print()

    try:
        while True:

            result = FloodResult(
                timestamp=int(time.time() * 1000),
                water_coverage_pct=25.3,
                road_water_pct=42.8,
                water_region_count=2,
                flood_level=2,
                confidence=0.91,
                latitude=22.6701,
                longitude=120.4881,
                inference_fps=15.7
            )

            send_flood_mavlink(result)

            print(
                "FLOOD SENT | "
                f"timestamp={result.timestamp} "
                f"water={result.water_coverage_pct:.1f}% "
                f"road={result.road_water_pct:.1f}% "
                f"regions={result.water_region_count} "
                f"level={result.flood_level} "
                f"conf={result.confidence:.2f} "
                f"lat={result.latitude:.4f} "
                f"lon={result.longitude:.4f} "
                f"fps={result.inference_fps:.1f}"
            )

            time.sleep(1.0)

    except KeyboardInterrupt:
        print()
        print("Flood sender stopped.")


if __name__ == "__main__":
    main()
