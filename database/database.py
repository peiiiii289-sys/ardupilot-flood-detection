from __future__ import annotations

import math
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "flood_data.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

REQUIRED_FIELDS = (
    "timestamp",
    "water_coverage_pct",
    "road_water_pct",
    "water_region_count",
    "flood_level",
    "confidence",
    "latitude",
    "longitude",
    "inference_fps",
)


def _connect(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path | str = DB_PATH) -> None:
    """依 schema.sql 初始化資料庫；不刪除既有資料。"""
    if not SCHEMA_PATH.is_file():
        raise FileNotFoundError(f"找不到 schema.sql：{SCHEMA_PATH}")

    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with closing(_connect(db_path)) as conn:
        conn.executescript(schema_sql)
        conn.commit()


def _is_finite_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(float(value))


def validate_result(result: Mapping[str, Any]) -> bool:
    """驗證 FloodResult 是否符合團隊固定九欄、型別與範圍。"""
    if not isinstance(result, Mapping):
        return False

    if any(field not in result for field in REQUIRED_FIELDS):
        return False

    timestamp = result["timestamp"]
    if not isinstance(timestamp, int) or isinstance(timestamp, bool):
        return False
    if timestamp < 100_000_000_000:
        return False

    water_coverage_pct = result["water_coverage_pct"]
    if not _is_finite_number(water_coverage_pct):
        return False
    if not 0 <= float(water_coverage_pct) <= 100:
        return False

    road_water_pct = result["road_water_pct"]
    if not _is_finite_number(road_water_pct):
        return False
    if not 0 <= float(road_water_pct) <= 100:
        return False

    water_region_count = result["water_region_count"]
    if (
        not isinstance(water_region_count, int)
        or isinstance(water_region_count, bool)
        or water_region_count < 0
    ):
        return False

    flood_level = result["flood_level"]
    if (
        not isinstance(flood_level, int)
        or isinstance(flood_level, bool)
        or flood_level not in (0, 1, 2, 3)
    ):
        return False

    confidence = result["confidence"]
    if not _is_finite_number(confidence):
        return False
    if not 0 <= float(confidence) <= 1:
        return False

    latitude = result["latitude"]
    if not _is_finite_number(latitude):
        return False
    if not -90 <= float(latitude) <= 90:
        return False

    longitude = result["longitude"]
    if not _is_finite_number(longitude):
        return False
    if not -180 <= float(longitude) <= 180:
        return False

    inference_fps = result["inference_fps"]
    if not _is_finite_number(inference_fps):
        return False
    if float(inference_fps) < 0:
        return False

    return True


def save_result(
    result: Mapping[str, Any],
    db_path: Path | str = DB_PATH,
) -> bool:
    """驗證後寫入一筆 FloodResult。"""
    if not validate_result(result):
        return False

    init_db(db_path)

    sql = """
    INSERT INTO flood_detection (
        timestamp,
        water_coverage_pct,
        road_water_pct,
        water_region_count,
        flood_level,
        confidence,
        latitude,
        longitude,
        inference_fps
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    params = (
        int(result["timestamp"]),
        float(result["water_coverage_pct"]),
        float(result["road_water_pct"]),
        int(result["water_region_count"]),
        int(result["flood_level"]),
        float(result["confidence"]),
        float(result["latitude"]),
        float(result["longitude"]),
        float(result["inference_fps"]),
    )

    try:
        with closing(_connect(db_path)) as conn:
            conn.execute(sql, params)
            conn.commit()
        return True
    except sqlite3.DatabaseError:
        return False


def get_latest(
    db_path: Path | str = DB_PATH,
) -> Optional[Dict[str, Any]]:
    """依 timestamp 取得最新一筆；無資料時回傳 None。"""
    init_db(db_path)

    sql = """
    SELECT
        id,
        timestamp,
        water_coverage_pct,
        road_water_pct,
        water_region_count,
        flood_level,
        confidence,
        latitude,
        longitude,
        inference_fps
    FROM flood_detection
    ORDER BY timestamp DESC, id DESC
    LIMIT 1
    """

    with closing(_connect(db_path)) as conn:
        row = conn.execute(sql).fetchone()

    return dict(row) if row is not None else None


def get_history(
    start_time: int,
    end_time: int,
    db_path: Path | str = DB_PATH,
) -> List[Dict[str, Any]]:
    """依毫秒 timestamp 查詢指定時間範圍，按時間由舊到新排序。"""
    if (
        not isinstance(start_time, int)
        or isinstance(start_time, bool)
        or not isinstance(end_time, int)
        or isinstance(end_time, bool)
    ):
        raise TypeError("start_time 與 end_time 必須是整數 timestamp(ms)")

    if start_time > end_time:
        raise ValueError("start_time 不可大於 end_time")

    init_db(db_path)

    sql = """
    SELECT
        id,
        timestamp,
        water_coverage_pct,
        road_water_pct,
        water_region_count,
        flood_level,
        confidence,
        latitude,
        longitude,
        inference_fps
    FROM flood_detection
    WHERE timestamp BETWEEN ? AND ?
    ORDER BY timestamp ASC, id ASC
    """

    with closing(_connect(db_path)) as conn:
        rows = conn.execute(sql, (start_time, end_time)).fetchall()

    return [dict(row) for row in rows]