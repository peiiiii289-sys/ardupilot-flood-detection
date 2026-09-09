import sqlite3
import tempfile
from pathlib import Path

from database.database import (
    get_history,
    get_latest,
    init_db,
    save_result,
)

FAKE_FLOOD_RESULT = {
    "timestamp": 1786632000000,
    "water_coverage_pct": 25.3,
    "road_water_pct": 42.8,
    "water_region_count": 2,
    "flood_level": 2,
    "confidence": 0.91,
    "latitude": 22.6701,
    "longitude": 120.4881,
    "inference_fps": 15.7,
}


def run_database_tests() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        test_db = Path(temp_dir) / "test_flood_data.db"

        init_db(test_db)
        assert save_result(FAKE_FLOOD_RESULT, test_db) is True

        latest = get_latest(test_db)
        assert latest is not None
        assert latest["timestamp"] == 1786632000000
        assert latest["flood_level"] == 2

        w0 = dict(FAKE_FLOOD_RESULT)
        w0.update({
            "timestamp": 1786631000000,
            "water_coverage_pct": 0.0,
            "road_water_pct": 0.0,
            "water_region_count": 0,
            "flood_level": 0,
        })

        w3 = dict(FAKE_FLOOD_RESULT)
        w3.update({
            "timestamp": 1786633000000,
            "water_coverage_pct": 50.0,
            "road_water_pct": 65.0,
            "water_region_count": 3,
            "flood_level": 3,
        })

        assert save_result(w0, test_db) is True
        assert save_result(w3, test_db) is True

        history = get_history(
            1786631000000,
            1786633000000,
            test_db,
        )
        assert [row["timestamp"] for row in history] == [
            1786631000000,
            1786632000000,
            1786633000000,
        ]

        invalid = dict(FAKE_FLOOD_RESULT)
        invalid["confidence"] = 1.5
        assert save_result(invalid, test_db) is False

        invalid_ts = dict(FAKE_FLOOD_RESULT)
        invalid_ts["timestamp"] = 1786632000
        assert save_result(invalid_ts, test_db) is False

        with sqlite3.connect(test_db) as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM flood_detection"
            ).fetchone()[0]

        assert count == 3

    print("C SQLite database verification: PASS")


if __name__ == "__main__":
    run_database_tests()
