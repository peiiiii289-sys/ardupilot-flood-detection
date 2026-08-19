#!/usr/bin/env python3

import os
import sys
import time
from pathlib import Path

# ============================================================
# 使用專案自己的 pymavlink / ardupilotmega dialect
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent
LOCAL_MAVLINK = PROJECT_ROOT / "modules" / "mavlink"

sys.path.insert(0, str(LOCAL_MAVLINK))

os.environ["MAVLINK20"] = "1"
os.environ["MAVLINK_DIALECT"] = "ardupilotmega"

from pymavlink import mavutil


# ============================================================
# MAVLink connection
# ============================================================

CONNECTION = "tcp:127.0.0.1:5762"

SOURCE_SYSTEM = 42
SOURCE_COMPONENT = 211


# ============================================================
# Fake FloodResult
#
# 這裡先使用團隊文件中的 W2 範例資料。
# A 模型完成後，只需要把這些假資料換成 A 的真實 FloodResult。
# ============================================================

WATER_COVERAGE_PCT = 25.3
ROAD_WATER_PCT = 42.8
WATER_REGION_COUNT = 2
FLOOD_LEVEL = 2
CONFIDENCE = 0.91
LATITUDE = 22.6701
LONGITUDE = 120.4881
INFERENCE_FPS = 15.7

SEND_INTERVAL_SEC = 1.0


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

    print()
    print("Connecting to ArduPlane SERIAL1 ...")

    master = mavutil.mavlink_connection(
        CONNECTION,
        source_system=SOURCE_SYSTEM,
        source_component=SOURCE_COMPONENT
    )

    print("Connected.")
    print("Sending AI_FLOOD_DETECTION_RESULT ...")
    print("Press Ctrl+C to stop.")
    print()

    try:

        while True:

            # Unix timestamp，毫秒
            timestamp = int(time.time() * 1000)

            master.mav.ai_flood_detection_result_send(
                timestamp,
                WATER_COVERAGE_PCT,
                ROAD_WATER_PCT,
                WATER_REGION_COUNT,
                FLOOD_LEVEL,
                CONFIDENCE,
                LATITUDE,
                LONGITUDE,
                INFERENCE_FPS
            )

            print(
                "FLOOD SENT | "
                f"timestamp={timestamp} "
                f"water={WATER_COVERAGE_PCT:.1f}% "
                f"road={ROAD_WATER_PCT:.1f}% "
                f"regions={WATER_REGION_COUNT} "
                f"level={FLOOD_LEVEL} "
                f"conf={CONFIDENCE:.2f} "
                f"lat={LATITUDE:.4f} "
                f"lon={LONGITUDE:.4f} "
                f"fps={INFERENCE_FPS:.1f}"
            )

            time.sleep(SEND_INTERVAL_SEC)

    except KeyboardInterrupt:

        print()
        print("Flood sender stopped.")


if __name__ == "__main__":
    main()
