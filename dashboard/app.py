from pathlib import Path
import os
import json
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from dashboard.data_source import (
    load_db_latest,
    load_db_history,
)

from dashboard.live_source import (
    load_live_latest,
    load_live_history,
)

from dashboard.qa_exporter import export_qa_results


# ==================================================
# 專案路徑
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FAKE_DATA_PATH = BASE_DIR / "tests" / "dashboard_fake_result.json"
FAKE_FALLBACK_PATH = BASE_DIR / "tests" / "sample_flood_result.json"
HISTORY_PATH = BASE_DIR / "tests" / "fake_history.csv"

DB_PATH = Path(
    os.environ.get(
        "FLOOD_DB_PATH",
        BASE_DIR / "database" / "flood_data.db",
    )
).expanduser()

# ==================================================
# 資料讀取
# ==================================================

def load_fake_result():
    with open(
        FAKE_DATA_PATH if FAKE_DATA_PATH.exists() else FAKE_FALLBACK_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def load_fake_history():
    df = pd.read_csv(HISTORY_PATH)

    df["datetime"] = pd.to_datetime(
        df["timestamp"],
        unit="ms"
    )

    return df


# ==================================================
# Flood Level
# ==================================================

def flood_level_text(level):
    levels = {
        0: "W0 正常",
        1: "W1 輕微積水",
        2: "W2 中度積水",
        3: "W3 大範圍積水"
    }

    return levels.get(
        level,
        "未知等級"
    )


def timestamp_to_text(timestamp_ms):
    try:
        dt = datetime.fromtimestamp(
            timestamp_ms / 1000
        )

        return dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    except (
        TypeError,
        ValueError,
        OSError
    ):
        return "時間格式錯誤"


# ==================================================
# 頁面設定
# ==================================================

st.set_page_config(
    page_title="UAV 積水偵測系統",
    layout="wide"
)

st.title(
    "UAV 無人機道路積水偵測系統"
)

st.caption(
    "Version 2 | Application & QA Dashboard"
)


# ==================================================
# 資料來源選擇
# ==================================================

st.sidebar.header("系統設定")

data_source_mode = st.sidebar.radio(
    "資料來源",
    [
        "Fake",
        "SQLite DB",
        "Live"
    ]
)

if data_source_mode == "Fake":

    st.sidebar.success(
        "目前使用 Fake 測試資料"
    )

elif data_source_mode == "SQLite DB":

    if DB_PATH.exists():

        st.sidebar.success(
            "SQLite 資料庫已連線"
        )

        st.sidebar.caption(
            str(DB_PATH)
        )

    else:

        st.sidebar.error(
            "找不到 SQLite 資料庫"
        )

else:

    if DB_PATH.exists():

        st.sidebar.info(
            "Live 模式已啟用"
        )

        st.sidebar.caption(
            "即時監看 C SQLite 新資料"
        )

    else:

        st.sidebar.error(
            "Live 模式找不到 SQLite 資料庫"
        )

# ==================================================
# 分頁
# ==================================================

tab_live, tab_history, tab_qa, tab_extended_qa = st.tabs(
    [
        "即時監控",
        "歷史分析",
        "QA 測試",
        "擴充 QA"
    ]
)


# ==================================================
# 即時監控
# ==================================================

with tab_live:

    st.caption(
        "資料更新頻率：每 1 秒"
    )

    @st.fragment(run_every="1s")
    def live_dashboard():

        try:

            live_state = None

            if data_source_mode == "Fake":

                result = load_fake_result()


            elif data_source_mode == "SQLite DB":

                result = load_db_latest(
                    str(DB_PATH)
                )

                if result is None:

                    st.warning(
                        "SQLite 資料庫目前沒有資料"
                    )

                    return


            elif data_source_mode == "Live":

                result, live_state = load_live_latest(
                    str(DB_PATH)
                )

                if result is None:

                    st.error(
                        "LIVE STATUS：OFFLINE"
                    )

                    st.warning(
                        live_state["message"]
                    )

                    return


        except Exception as e:

            st.error(
                f"讀取 FloodResult 失敗：{e}"
            )

            return

        level = int(
            result["flood_level"]
        )

        if data_source_mode == "Live":

            st.subheader(
                "Live 連線狀態"
            )

            status = live_state["status"]

            age = live_state["age_seconds"]

            if status == "ONLINE":

                st.success(
                    f"LIVE STATUS：ONLINE｜"
                    f"最後更新 {age:.1f} 秒前"
                )

            elif status == "STALE":

                st.warning(
                    f"LIVE STATUS：STALE｜"
                    f"最後更新 {age:.1f} 秒前"
                )

            else:

                st.error(
                    f"LIVE STATUS：OFFLINE｜"
                    f"最後更新 {age:.1f} 秒前"
                )

            st.caption(
                live_state["message"]
            )

        st.subheader(
            "即時偵測狀態"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "道路積水比例",
                f'{result["road_water_pct"]:.1f}%'
            )

        with col2:
            st.metric(
                "畫面積水比例",
                f'{result["water_coverage_pct"]:.1f}%'
            )

        with col3:
            st.metric(
                "風險等級",
                flood_level_text(level)
            )

        with col4:
            st.metric(
                "AI 信心值",
                f'{result["confidence"] * 100:.1f}%'
            )

        st.divider()

        st.subheader(
            "偵測詳細資料"
        )

        left, right = st.columns(2)

        with left:
            st.write(
                "**事件時間：**",
                timestamp_to_text(
                    result["timestamp"]
                )
            )

            st.write(
                "**積水區域數量：**",
                result["water_region_count"]
            )

            st.write(
                "**AI 推論速度：**",
                f'{result["inference_fps"]:.1f} FPS'
            )

        with right:
            st.write(
                "**GPS 緯度：**",
                result["latitude"]
            )

            st.write(
                "**GPS 經度：**",
                result["longitude"]
            )

            st.write(
                "**資料來源：**",
                data_source_mode
            )

        st.divider()

        st.subheader(
            "積水風險判定"
        )

        if level == 0:
            st.success(
                "W0：正常或幾乎無積水"
            )

        elif level == 1:
            st.info(
                "W1：局部輕微積水"
            )

        elif level == 2:
            st.warning(
                "W2：中度積水影響"
            )

        elif level == 3:
            st.error(
                "W3：大範圍積水，高風險"
            )

        else:
            st.error(
                "Flood Level 資料異常"
            )

        st.divider()

        with st.expander(
            "查看完整 FloodResult"
        ):
            st.json(result)

    live_dashboard()


# ==================================================
# 歷史分析
# ==================================================

with tab_history:

    st.caption("歷史資料更新頻率：每 2 秒")

    @st.fragment(run_every="2s")
    def history_dashboard():

        st.subheader(
            "歷史積水分析"
        )

        try:

            if data_source_mode == "Fake":

                history = load_fake_history()


            elif data_source_mode == "SQLite DB":

                history = load_db_history(
                    str(DB_PATH)
                )


            elif data_source_mode == "Live":

                history = load_live_history(
                    str(DB_PATH)
                )


            if history.empty:

                st.warning(
                    "目前沒有歷史資料"
                )

                return


            if "datetime" not in history.columns:

                history["datetime"] = pd.to_datetime(
                    history["timestamp"],
                    unit="ms"
                )


        except Exception as e:

            st.error(
                f"讀取歷史資料失敗：{e}"
            )

            return

        # ------------------------------------------
        # 統計摘要
        # ------------------------------------------

        total_records = len(history)

        average_road_water = (
            history["road_water_pct"].mean()
        )

        max_road_water = (
            history["road_water_pct"].max()
        )

        high_risk_count = (
            history["flood_level"] == 3
        ).sum()


        c1, c2, c3, c4 = st.columns(4)


        with c1:
            st.metric(
                "歷史資料筆數",
                total_records
            )


        with c2:
            st.metric(
                "平均道路積水",
                f"{average_road_water:.1f}%"
            )


        with c3:
            st.metric(
                "最高道路積水",
                f"{max_road_water:.1f}%"
            )


        with c4:
            st.metric(
                "W3 高風險事件",
                int(high_risk_count)
            )


        # ------------------------------------------
        # 道路積水比例時間圖
        # ------------------------------------------

        st.divider()

        st.subheader(
            "道路積水比例時間變化"
        )


        fig1, ax1 = plt.subplots()

        ax1.plot(
            history["datetime"],
            history["road_water_pct"],
            marker="o"
        )

        ax1.set_xlabel("Time")
        ax1.set_ylabel("Road Water (%)")

        ax1.set_title(
            "Road Water Percentage Over Time"
        )

        ax1.tick_params(
            axis="x",
            rotation=45
        )

        fig1.tight_layout()

        st.pyplot(fig1)

        plt.close(fig1)


        # ------------------------------------------
        # W0 ~ W3 統計
        # ------------------------------------------

        st.divider()

        st.subheader(
            "W0～W3 次數統計"
        )


        level_counts = (
            history["flood_level"]
            .value_counts()
            .reindex(
                [0, 1, 2, 3],
                fill_value=0
            )
        )


        # 額外顯示數字，方便 QA
        count_cols = st.columns(4)

        with count_cols[0]:
            st.metric(
                "W0 次數",
                int(level_counts.loc[0])
            )

        with count_cols[1]:
            st.metric(
                "W1 次數",
                int(level_counts.loc[1])
            )

        with count_cols[2]:
            st.metric(
                "W2 次數",
                int(level_counts.loc[2])
            )

        with count_cols[3]:
            st.metric(
                "W3 次數",
                int(level_counts.loc[3])
            )


        fig2, ax2 = plt.subplots()

        ax2.bar(
            ["W0", "W1", "W2", "W3"],
            level_counts.values
        )

        ax2.set_xlabel(
            "Flood Level"
        )

        ax2.set_ylabel(
            "Count"
        )

        ax2.set_title(
            "Flood Level Distribution"
        )

        ax2.set_ylim(
            0,
            max(level_counts.values) + 1
        )

        fig2.tight_layout()

        st.pyplot(fig2)

        plt.close(fig2)


        # ------------------------------------------
        # 歷史資料明細
        # ------------------------------------------

        st.divider()

        st.subheader(
            "歷史資料明細"
        )


        display_df = history[
            [
                "datetime",
                "road_water_pct",
                "water_coverage_pct",
                "water_region_count",
                "flood_level",
                "confidence",
                "latitude",
                "longitude",
                "inference_fps"
            ]
        ].copy()


        display_df["flood_level"] = (
            display_df["flood_level"]
            .map({
                0: "W0",
                1: "W1",
                2: "W2",
                3: "W3"
            })
        )


        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )


    history_dashboard()

# ==================================================
# QA 測試
# ==================================================

with tab_qa:

    st.caption("QA 資料更新頻率：每 1 秒")

    if st.button(
        "匯出最新 QA 報告",
        key="export_qa_report"
    ):

        try:

            export_result = export_qa_results()

            st.success(
                "QA 報告匯出完成"
            )

            st.write(
                "**詳細結果：**",
                str(
                    export_result["detail_path"]
                )
            )

            st.write(
                "**摘要結果：**",
                str(
                    export_result["summary_path"]
                )
            )

            st.write(
                f'PASS：{export_result["pass_count"]}　'
                f'FAIL：{export_result["fail_count"]}　'
                f'WAITING：{export_result["waiting_count"]}'
            )

            st.write(
                f'已執行測試通過率：'
                f'{export_result["pass_rate"]:.1f}%'
            )

            st.write(
                f'QA 完成率：'
                f'{export_result["completion_rate"]:.1f}%'
            )

        except Exception as e:

            st.error(
                f"QA 報告匯出失敗：{e}"
            )

    @st.fragment(run_every="1s")
    def qa_dashboard():

        st.subheader("系統 QA 測試結果")

        QA_PATH = (
            BASE_DIR
            / "tests"
            / "qa_results.csv"
        )

        try:
            qa = pd.read_csv(QA_PATH)

        except Exception as e:
            st.error(
                f"讀取 QA 測試資料失敗：{e}"
            )
            return


        # ------------------------------------------
        # 自動 PASS / FAIL
        # ------------------------------------------

        qa["result"] = qa.apply(
            lambda row:
            "PASS"
            if row["expected_level"]
            == row["actual_level"]
            else "FAIL",
            axis=1
        )


        total_count = len(qa)

        pass_count = (
            qa["result"] == "PASS"
        ).sum()

        fail_count = (
            qa["result"] == "FAIL"
        ).sum()

        pass_rate = (
            pass_count / total_count * 100
            if total_count > 0
            else 0
        )


        # ------------------------------------------
        # QA 摘要
        # ------------------------------------------

        q1, q2, q3, q4 = st.columns(4)

        with q1:
            st.metric(
                "測試案例",
                total_count
            )

        with q2:
            st.metric(
                "PASS",
                int(pass_count)
            )

        with q3:
            st.metric(
                "FAIL",
                int(fail_count)
            )

        with q4:
            st.metric(
                "通過率",
                f"{pass_rate:.1f}%"
            )


        st.divider()


        # ------------------------------------------
        # W0 ~ W3 顯示
        # ------------------------------------------

        qa_display = qa.copy()

        level_map = {
            0: "W0",
            1: "W1",
            2: "W2",
            3: "W3"
        }

        qa_display["expected_level"] = (
            qa_display["expected_level"]
            .map(level_map)
        )

        qa_display["actual_level"] = (
            qa_display["actual_level"]
            .map(level_map)
        )

        qa_display = qa_display.rename(
            columns={
                "case_id": "案例",
                "description": "測試內容",
                "expected_level": "預期等級",
                "actual_level": "系統輸出",
                "road_water_pct": "道路積水比例 (%)",
                "result": "結果"
            }
        )


        st.subheader(
            "預期結果 vs 系統輸出"
        )

        st.dataframe(
            qa_display,
            use_container_width=True,
            hide_index=True
        )


        st.divider()


        # ------------------------------------------
        # QA 最終判定
        # ------------------------------------------

        if fail_count == 0:

            st.success(
                "QA 基本分級測試全部通過"
            )

        else:

            st.error(
                f"QA 測試有 {fail_count} 個案例失敗"
            )


    qa_dashboard()

    # ==================================================
    # Live QA
    # ==================================================

    @st.fragment(run_every="2s")
    def live_qa_dashboard():

        st.divider()

        st.subheader(
            "D Live QA 測試結果"
        )

        LIVE_QA_PATH = (
            BASE_DIR
            / "tests"
            / "live_qa_results.csv"
        )

        try:

            live_qa = pd.read_csv(
                LIVE_QA_PATH
            )

        except Exception as e:

            st.error(
                f"讀取 Live QA 資料失敗：{e}"
            )

            return


        total_count = len(
            live_qa
        )

        pass_count = (
            live_qa["status"] == "PASS"
        ).sum()

        fail_count = (
            live_qa["status"] == "FAIL"
        ).sum()

        waiting_count = (
            live_qa["status"] == "WAITING"
        ).sum()


        if total_count > 0:

            pass_rate = (
                pass_count
                / total_count
                * 100
            )

        else:

            pass_rate = 0


        c1, c2, c3, c4 = st.columns(4)


        with c1:

            st.metric(
                "Live QA 案例",
                total_count
            )


        with c2:

            st.metric(
                "PASS",
                int(pass_count)
            )


        with c3:

            st.metric(
                "FAIL",
                int(fail_count)
            )


        with c4:

            st.metric(
                "通過率",
                f"{pass_rate:.1f}%"
            )


        live_qa_display = live_qa.rename(
            columns={
                "case_id": "案例",
                "description": "測試內容",
                "expected_behavior": "預期行為",
                "actual_result": "實際結果",
                "status": "狀態",
                "dependency": "測試模組",
                "notes": "備註"
            }
        )


        st.dataframe(
            live_qa_display,
            use_container_width=True,
            hide_index=True
        )


        if fail_count > 0:

            st.error(
                f"Live QA 有 {fail_count} 個案例失敗"
            )

        elif waiting_count > 0:

            st.warning(
                f"Live QA 尚有 {waiting_count} 個案例等待驗證"
            )

        else:

            st.success(
                "D Live QA 全部通過：7 / 7 PASS"
            )


    live_qa_dashboard()

# ==================================================
# 擴充 QA：T4 ~ T8
# ==================================================

with tab_extended_qa:

    st.caption("擴充 QA 狀態更新頻率：每 2 秒")

    @st.fragment(run_every="2s")
    def extended_qa_dashboard():

        st.subheader(
            "T4～T8 擴充測試"
        )

        EXTENDED_QA_PATH = (
            BASE_DIR
            / "tests"
            / "extended_qa_results.csv"
        )

        try:

            ext = pd.read_csv(
                EXTENDED_QA_PATH
            )

        except Exception as e:

            st.error(
                f"讀取擴充 QA 資料失敗：{e}"
            )

            return


        # ------------------------------------------
        # 狀態統計
        # ------------------------------------------

        total_count = len(ext)

        pass_count = (
            ext["status"] == "PASS"
        ).sum()

        fail_count = (
            ext["status"] == "FAIL"
        ).sum()

        waiting_count = (
            ext["status"] == "WAITING"
        ).sum()


        q1, q2, q3, q4 = st.columns(4)


        with q1:

            st.metric(
                "測試案例",
                total_count
            )


        with q2:

            st.metric(
                "PASS",
                int(pass_count)
            )


        with q3:

            st.metric(
                "FAIL",
                int(fail_count)
            )


        with q4:

            st.metric(
                "WAITING",
                int(waiting_count)
            )


        st.divider()


        # ------------------------------------------
        # 測試案例表
        # ------------------------------------------

        display_ext = ext.rename(
            columns={
                "case_id": "案例",
                "description": "測試內容",
                "purpose": "測試目的",
                "dependency": "依賴模組",
                "expected_behavior": "預期行為",
                "actual_result": "實際結果",
                "status": "狀態",
                "notes": "備註"
            }
        )


        st.subheader(
            "測試狀態"
        )


        st.dataframe(
            display_ext,
            use_container_width=True,
            hide_index=True
        )


        st.divider()


        # ------------------------------------------
        # 依賴模組說明
        # ------------------------------------------

        st.subheader(
            "目前待整合項目"
        )


        waiting = ext[
            ext["status"] == "WAITING"
        ]


        if len(waiting) == 0:

            st.success(
                "T4～T8 已全部完成測試"
            )

        else:

            st.warning(
                f"目前仍有 {len(waiting)} 個案例等待真實模組整合"
            )


        for _, row in waiting.iterrows():

            st.write(
                f'**{row["case_id"]}｜{row["description"]}**'
                f'　依賴：{row["dependency"]}'
            )


    extended_qa_dashboard()