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

        // 若先前曾 timeout，收到新資料時標記為已恢復
        if (_link_lost) {
            _link_lost = false;
            _recovery_pending = true;
        }
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

    void update_link_health(uint32_t now_ms, uint32_t timeout_ms)
    {
        if (!_have_result) {
            return;
        }

        if (!result_recent(now_ms, timeout_ms) && !_link_lost) {
            _link_lost = true;
            _timeout_start_ms = now_ms;
            _timeout_pending = true;
        }
    }

    bool link_lost() const { return _link_lost; }

    bool timeout_pending() const { return _timeout_pending; }
    void clear_timeout_pending() { _timeout_pending = false; }

    bool recovery_pending() const { return _recovery_pending; }
    void clear_recovery_pending() { _recovery_pending = false; }

    uint32_t timeout_duration_ms(uint32_t now_ms) const
    {
        if (!_link_lost || _timeout_start_ms == 0) {
            return 0;
        }
        return now_ms - _timeout_start_ms;
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

    bool _link_lost = false;
    bool _timeout_pending = false;
    bool _recovery_pending = false;
    uint32_t _timeout_start_ms = 0;
};
