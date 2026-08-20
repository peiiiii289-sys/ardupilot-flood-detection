from dataclasses import dataclass


@dataclass
class FloodResult:
    timestamp: int
    water_coverage_pct: float
    road_water_pct: float
    water_region_count: int
    flood_level: int
    confidence: float
    latitude: float
    longitude: float
    inference_fps: float
