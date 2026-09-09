from pathlib import Path
import json
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

FAKE_RESULT_PATH = (
    BASE_DIR
    / "tests"
    / "dashboard_fake_result.json"
)

FAKE_FALLBACK_PATH = (
    BASE_DIR
    / "tests"
    / "sample_flood_result.json"
)

FAKE_HISTORY_PATH = (
    BASE_DIR
    / "tests"
    / "fake_history.csv"
)


# ==================================================
# Fake Mode
# ==================================================

def load_fake_latest():

    with open(
        FAKE_RESULT_PATH if FAKE_RESULT_PATH.exists() else FAKE_FALLBACK_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def load_fake_history():

    return pd.read_csv(
        FAKE_HISTORY_PATH
    )


# ==================================================
# Database Mode
# ==================================================

def load_db_latest(db_path):

    conn = sqlite3.connect(db_path)

    try:

        query = """
        SELECT
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
        ORDER BY timestamp DESC
        LIMIT 1
        """

        df = pd.read_sql_query(
            query,
            conn
        )

    finally:

        conn.close()


    if df.empty:

        return None


    row = df.iloc[0].to_dict()

    row["timestamp"] = int(row["timestamp"])
    row["water_region_count"] = int(row["water_region_count"])
    row["flood_level"] = int(row["flood_level"])

    return row


def load_db_history(db_path):

    conn = sqlite3.connect(db_path)

    try:

        query = """
        SELECT
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
        ORDER BY timestamp ASC
        """

        return pd.read_sql_query(
            query,
            conn
        )

    finally:

        conn.close()