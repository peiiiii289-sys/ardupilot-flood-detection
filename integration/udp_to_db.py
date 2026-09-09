import json
import socket
import sys
from pathlib import Path


# --------------------------------------------------
# 專案根目錄
# --------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


# --------------------------------------------------
# C 組既有 SQLite 模組
# --------------------------------------------------
from database.database import save_result, get_latest


# --------------------------------------------------
# UDP 設定
# --------------------------------------------------
UDP_HOST = "0.0.0.0"
UDP_PORT = 14552

REQUIRED_FIELDS = [
    "timestamp",
    "water_coverage_pct",
    "road_water_pct",
    "water_region_count",
    "flood_level",
    "confidence",
    "latitude",
    "longitude",
    "inference_fps",
]


def normalize_flood_result(data):
    """
    確認收到的 JSON 包含 FloodResult 固定九欄。
    不允許 B/C/D 自行改欄位。
    """

    if not isinstance(data, dict):
        raise ValueError("FloodResult 必須是 JSON object")

    missing = [
        field
        for field in REQUIRED_FIELDS
        if field not in data
    ]

    if missing:
        raise ValueError(
            "缺少 FloodResult 欄位: "
            + ", ".join(missing)
        )

    return {
        field: data[field]
        for field in REQUIRED_FIELDS
    }


def main():

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    sock.bind((UDP_HOST, UDP_PORT))

    print("=" * 60)
    print(" B -> C FloodResult UDP Receiver")
    print("=" * 60)
    print(f"Listening : {UDP_HOST}:{UDP_PORT}")
    print("Target DB : database/flood_data.db")
    print("Fields    : 9")
    print("=" * 60)
    print()
    print("Waiting for FloodResult ...")
    print()

    while True:

        raw_data, sender = sock.recvfrom(65535)

        try:

            text = raw_data.decode("utf-8")

            data = json.loads(text)

            result = normalize_flood_result(data)

            print("=" * 60)
            print("FloodResult received")
            print("=" * 60)
            print(f"Sender              : {sender[0]}:{sender[1]}")
            print(f"timestamp           : {result['timestamp']}")
            print(f"water_coverage_pct  : {result['water_coverage_pct']}")
            print(f"road_water_pct      : {result['road_water_pct']}")
            print(f"water_region_count  : {result['water_region_count']}")
            print(f"flood_level         : {result['flood_level']}")
            print(f"confidence          : {result['confidence']}")
            print(f"latitude            : {result['latitude']}")
            print(f"longitude           : {result['longitude']}")
            print(f"inference_fps       : {result['inference_fps']}")
            print()

            saved = save_result(result)

            if saved:

                latest = get_latest()

                print("SQLite save          : PASS")

                if latest:
                    print(
                        f"SQLite latest id     : "
                        f"{latest.get('id')}"
                    )

                print("=" * 60)
                print()

            else:

                print("SQLite save          : FAIL")
                print("=" * 60)
                print()

        except Exception as exc:

            print("=" * 60)
            print("FloodResult rejected")
            print("=" * 60)
            print(f"Reason: {exc}")
            print("=" * 60)
            print()


if __name__ == "__main__":
    main()
