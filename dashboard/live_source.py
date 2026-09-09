import time

from dashboard.data_source import (
    load_db_latest,
    load_db_history,
)


# ==================================================
# Live 狀態門檻
# ==================================================

STALE_AFTER_SECONDS = 3
OFFLINE_AFTER_SECONDS = 5


# ==================================================
# Live 狀態判定
# ==================================================

def evaluate_live_status(
    timestamp_ms,
    now_ms=None,
    stale_after_s=STALE_AFTER_SECONDS,
    offline_after_s=OFFLINE_AFTER_SECONDS,
):

    if timestamp_ms is None:
        return {
            "status": "OFFLINE",
            "age_seconds": None,
            "message": "目前沒有收到任何 FloodResult"
        }

    if now_ms is None:
        now_ms = int(
            time.time() * 1000
        )

    age_seconds = (
        now_ms - int(timestamp_ms)
    ) / 1000.0

    # 避免系統時間有極小誤差時出現負數
    age_seconds = max(
        0.0,
        age_seconds
    )

    if age_seconds < stale_after_s:

        status = "ONLINE"
        message = "Live 資料正常持續更新"

    elif age_seconds < offline_after_s:

        status = "STALE"
        message = "Live 資料更新延遲"

    else:

        status = "OFFLINE"
        message = "超過 5 秒沒有收到新的 FloodResult"

    return {
        "status": status,
        "age_seconds": round(
            age_seconds,
            1
        ),
        "message": message
    }


# ==================================================
# Live 最新資料
# ==================================================

def load_live_latest(db_path):

    result = load_db_latest(
        db_path
    )

    if result is None:

        live_state = evaluate_live_status(
            None
        )

        return None, live_state

    live_state = evaluate_live_status(
        result["timestamp"]
    )

    return result, live_state


# ==================================================
# Live 歷史資料
# ==================================================

def load_live_history(db_path):

    return load_db_history(
        db_path
    )