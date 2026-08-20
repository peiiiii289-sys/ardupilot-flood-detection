#pragma once

#include <stdint.h>

class AP_FloodDetection
{
public:
    void update(uint64_t timestamp,
                float water_coverage_pct,
                float road_water_pct,
                uint16_t water_region_count,
                uint8_t flood_level,
                float confidence,
                float latitude,
                float longitude,
                float inference_fps,
                uint32_t now_ms)
    {
        _timestamp = timestamp;
        _water_coverage_pct = water_coverage_pct;
        _road_water_pct = road_water_pct;
        _water_region_count = water_region_count;
        _flood_level = flood_level;
        _confidence = confidence;
        _latitude = latitude;
        _longitude = longitude;
        _inference_fps = inference_fps;

        _last_update_ms = now_ms;
        _have_result = true;
    }

    bool have_result() const { return _have_result; }

    uint64_t timestamp() const { return _timestamp; }
    float water_coverage_pct() const { return _water_coverage_pct; }
    float road_water_pct() const { return _road_water_pct; }
    uint16_t water_region_count() const { return _water_region_count; }
    uint8_t flood_level() const { return _flood_level; }
    float confidence() const { return _confidence; }
    float latitude() const { return _latitude; }
    float longitude() const { return _longitude; }
    float inference_fps() const { return _inference_fps; }

    uint32_t last_update_ms() const { return _last_update_ms; }

    bool result_recent(uint32_t now_ms, uint32_t timeout_ms) const
    {
        return _have_result &&
               (now_ms - _last_update_ms) <= timeout_ms;
    }

private:
    uint64_t _timestamp = 0;

    float _water_coverage_pct = 0.0f;
    float _road_water_pct = 0.0f;

    uint16_t _water_region_count = 0;
    uint8_t _flood_level = 0;

    float _confidence = 0.0f;

    float _latitude = 0.0f;
    float _longitude = 0.0f;

    float _inference_fps = 0.0f;

    uint32_t _last_update_ms = 0;
    bool _have_result = false;
};
