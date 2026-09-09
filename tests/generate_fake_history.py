from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    BASE_DIR
    / "tests"
    / "fake_history.csv"
)


ROAD_WATER_VALUES = [
    2.3,
    3.8,
    4.5,
    6.2,
    9.8,
    13.5,
    17.2,
    22.4,
    28.8,
    35.6,
    42.8,
    48.1,
    53.2,
    61.7,
    72.4,
    58.3,
    46.2,
    31.5,
    18.4,
    9.2
]


def get_flood_level(road_water_pct):

    if road_water_pct < 5:
        return 0

    elif road_water_pct < 20:
        return 1

    elif road_water_pct < 50:
        return 2

    else:
        return 3


records = []

start_time = (
    datetime.now()
    - timedelta(minutes=19)
)


for i, road_water_pct in enumerate(
    ROAD_WATER_VALUES
):

    event_time = (
        start_time
        + timedelta(minutes=i)
    )

    flood_level = get_flood_level(
        road_water_pct
    )

    records.append({
        "timestamp": int(
            event_time.timestamp() * 1000
        ),
        "water_coverage_pct": round(
            road_water_pct * 0.65,
            1
        ),
        "road_water_pct": road_water_pct,
        "water_region_count": max(
            0,
            flood_level + 1
        ),
        "flood_level": flood_level,
        "confidence": round(
            0.90 + (i % 5) * 0.01,
            2
        ),
        "latitude": 22.6701 + i * 0.0001,
        "longitude": 120.4881 + i * 0.0001,
        "inference_fps": round(
            15.0 + (i % 4) * 0.3,
            1
        )
    })


df = pd.DataFrame(records)

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


print("=" * 50)
print("D Fake History Generator")
print("=" * 50)

print("Output :", OUTPUT_FILE)
print("Records:", len(df))

print()

print(
    df[
        [
            "timestamp",
            "road_water_pct",
            "flood_level"
        ]
    ].to_string(index=False)
)

print()
print("FAKE HISTORY GENERATION PASS")