#!/usr/bin/env python3

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from shared.flood_result import FloodResult
from mavlink.sender import send_flood_mavlink


TEST_CASES = [
    # W0: road_water_pct < 5%
    ("W0", 2.0, 0),

    # W1: 5% <= road_water_pct < 20%
    ("W1", 10.0, 1),

    # W2: 20% <= road_water_pct < 50%
    ("W2", 30.0, 2),

    # W3: road_water_pct >= 50%
    ("W3", 60.0, 3),
]


def main():
    print("==============================================")
    print(" Flood W0-W3 MAVLink Test")
    print("==============================================")

    for name, road_pct, level in TEST_CASES:

        result = FloodResult(
            timestamp=int(time.time() * 1000),
            water_coverage_pct=road_pct,
            road_water_pct=road_pct,
            water_region_count=level,
            flood_level=level,
            confidence=0.90,
            latitude=22.6701,
            longitude=120.4881,
            inference_fps=15.0
        )

        send_flood_mavlink(result)

        print(
            f"{name} SENT | "
            f"road={result.road_water_pct:.1f}% "
            f"level={result.flood_level} "
            f"confidence={result.confidence:.2f}"
        )

        time.sleep(3)

    print("==============================================")
    print(" W0-W3 test finished")
    print("==============================================")


if __name__ == "__main__":
    main()
