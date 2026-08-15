#!/usr/bin/env python3

import os
import sys
import time
from pathlib import Path

# 使用目前這個 flood 專案裡剛生成的 pymavlink dialect
PROJECT_ROOT = Path(__file__).resolve().parent
LOCAL_MAVLINK = PROJECT_ROOT / "modules" / "mavlink"

sys.path.insert(0, str(LOCAL_MAVLINK))

os.environ["MAVLINK20"] = "1"
os.environ["MAVLINK_DIALECT"] = "ardupilotmega"

from pymavlink import mavutil


CONNECT = "tcp:127.0.0.1:5762"

SYSID = 42
COMPID = 211


def main():
    print("========================================")
    print(" Flood Detection MAVLink Test Sender")
    print("========================================")
    print(f"Connect : {CONNECT}")
    print(f"SYSID   : {SYSID}")
    print(f"COMPID  : {COMPID}")
    print()

    master = mavutil.mavlink_connection(
        CONNECT,
        source_system=SYSID,
        source_component=COMPID,
    )

    print("Connected to ArduPlane SERIAL1")
    print("Sending AI_FLOOD_DETECTION_RESULT...")
    print("Press Ctrl+C to stop.")
    print()

    try:
        while True:
            time_boot_ms = int(time.monotonic() * 1000) & 0xFFFFFFFF

            image_width = 1920
            image_height = 1080

            water_coverage_pct = 63.5
            road_water_pct = 48.2

            flood_level = 2
            confidence = 0.92

            inference_fps = 18.5

            master.mav.ai_flood_detection_result_send(
                time_boot_ms,
                image_width,
                image_height,
                water_coverage_pct,
                road_water_pct,
                flood_level,
                confidence,
                inference_fps,
            )

            print(
                f"FLOOD SENT | "
                f"water={water_coverage_pct:.1f}% "
                f"road={road_water_pct:.1f}% "
                f"level={flood_level} "
                f"conf={confidence:.2f} "
                f"fps={inference_fps:.1f}"
            )

            # 先用 1 Hz 測試，避免 GCS 訊息洗版
            time.sleep(1)

    except KeyboardInterrupt:
        print()
        print("Flood sender stopped.")


if __name__ == "__main__":
    main()
