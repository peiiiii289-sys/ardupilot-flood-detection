CREATE TABLE IF NOT EXISTS flood_detection (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    water_coverage_pct REAL,
    road_water_pct REAL,
    water_region_count INTEGER,
    flood_level INTEGER,
    confidence REAL,
    latitude REAL,
    longitude REAL,
    inference_fps REAL
);