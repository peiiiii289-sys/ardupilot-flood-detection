import json
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    BASE_DIR
    / "tests"
    / "dashboard_fake_result.json"
)


TEST_CASES = [
    {
        "name": "W0",
        "data": {
            "timestamp": 1786632000000,
            "water_coverage_pct": 2.1,
            "road_water_pct": 3.2,
            "water_region_count": 0,
            "flood_level": 0,
            "confidence": 0.96,
            "latitude": 22.6701,
            "longitude": 120.4881,
            "inference_fps": 16.4
        }
    },
    {
        "name": "W1",
        "data": {
            "timestamp": 1786632001000,
            "water_coverage_pct": 10.5,
            "road_water_pct": 12.8,
            "water_region_count": 1,
            "flood_level": 1,
            "confidence": 0.93,
            "latitude": 22.6702,
            "longitude": 120.4882,
            "inference_fps": 16.1
        }
    },
    {
        "name": "W2",
        "data": {
            "timestamp": 1786632002000,
            "water_coverage_pct": 25.3,
            "road_water_pct": 42.8,
            "water_region_count": 2,
            "flood_level": 2,
            "confidence": 0.91,
            "latitude": 22.6703,
            "longitude": 120.4883,
            "inference_fps": 15.7
        }
    },
    {
        "name": "W3",
        "data": {
            "timestamp": 1786632003000,
            "water_coverage_pct": 61.5,
            "road_water_pct": 72.4,
            "water_region_count": 5,
            "flood_level": 3,
            "confidence": 0.94,
            "latitude": 22.6704,
            "longitude": 120.4884,
            "inference_fps": 14.8
        }
    }
]


print("=" * 50)
print("D Dashboard W0-W3 QA Test")
print("=" * 50)


for case in TEST_CASES:

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            case["data"],
            f,
            ensure_ascii=False,
            indent=4
        )

    print()
    print(f"Running case : {case['name']}")
    print(
        "road_water_pct =",
        case["data"]["road_water_pct"]
    )
    print(
        "flood_level =",
        case["data"]["flood_level"]
    )

    time.sleep(5)


print()
print("=" * 50)
print("W0-W3 FAKE TEST COMPLETE")
print("=" * 50)