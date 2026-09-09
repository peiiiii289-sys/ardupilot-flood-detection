import sys
import time
from pathlib import Path


# ==================================================
# C 專案路徑
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)


# ==================================================
# 使用 C 的正式資料庫寫入函式
# ==================================================

from database.database import save_result


# ==================================================
# 模擬 W0 ~ W3
# ==================================================

CASES = [
    {
        "water_coverage_pct": 2.5,
        "road_water_pct": 3.0,
        "water_region_count": 0,
        "flood_level": 0,
        "confidence": 0.92,
        "latitude": 22.6701,
        "longitude": 120.4881,
        "inference_fps": 15.5,
    },

    {
        "water_coverage_pct": 9.8,
        "road_water_pct": 12.0,
        "water_region_count": 1,
        "flood_level": 1,
        "confidence": 0.93,
        "latitude": 22.6702,
        "longitude": 120.4882,
        "inference_fps": 15.3,
    },

    {
        "water_coverage_pct": 28.5,
        "road_water_pct": 35.0,
        "water_region_count": 2,
        "flood_level": 2,
        "confidence": 0.94,
        "latitude": 22.6703,
        "longitude": 120.4883,
        "inference_fps": 15.1,
    },

    {
        "water_coverage_pct": 61.5,
        "road_water_pct": 72.4,
        "water_region_count": 5,
        "flood_level": 3,
        "confidence": 0.95,
        "latitude": 22.6704,
        "longitude": 120.4884,
        "inference_fps": 14.8,
    },
]


# ==================================================
# Live Loop
# ==================================================

print("=" * 60)
print("D Live Simulator")
print("=" * 60)
print("每 1 秒寫入一筆 FloodResult")
print("資料循環：W0 -> W1 -> W2 -> W3")
print("按 Ctrl+C 可停止")
print("=" * 60)


index = 0


try:

    while True:

        result = CASES[
            index % len(CASES)
        ].copy()

        # 每筆都產生新的毫秒 timestamp
        result["timestamp"] = int(
            time.time() * 1000
        )

        ok = save_result(
            result
        )

        print(
            f'W{result["flood_level"]} | '
            f'road={result["road_water_pct"]:.1f}% | '
            f'water={result["water_coverage_pct"]:.1f}% | '
            f'confidence={result["confidence"]:.2f} | '
            f'save={ok}'
        )

        index += 1

        time.sleep(1)


except KeyboardInterrupt:

    print()
    print("=" * 60)
    print("Live Simulator stopped.")
    print("=" * 60)