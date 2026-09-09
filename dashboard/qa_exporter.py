from pathlib import Path
from datetime import datetime

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

BASIC_QA_PATH = (
    BASE_DIR
    / "tests"
    / "qa_results.csv"
)

LIVE_QA_PATH = (
    BASE_DIR
    / "tests"
    / "live_qa_results.csv"
)

EXTENDED_QA_PATH = (
    BASE_DIR
    / "tests"
    / "extended_qa_results.csv"
)

RESULT_DIR = (
    BASE_DIR
    / "docs"
    / "results"
)


def export_qa_results():

    RESULT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    now = datetime.now()

    generated_at = now.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    filename_time = now.strftime(
        "%Y%m%d_%H%M%S"
    )

    # ----------------------------------------------
    # T0 ~ T3
    # ----------------------------------------------

    basic = pd.read_csv(
        BASIC_QA_PATH
    )

    basic["status"] = basic.apply(
        lambda row:
        "PASS"
        if row["expected_level"]
        == row["actual_level"]
        else "FAIL",
        axis=1
    )

    basic_report = pd.DataFrame({
        "case_id": basic["case_id"],
        "description": basic["description"],
        "category": "Basic Flood Level QA",
        "expected": basic["expected_level"].apply(
            lambda x: f"W{int(x)}"
        ),
        "actual": basic["actual_level"].apply(
            lambda x: f"W{int(x)}"
        ),
        "road_water_pct": basic["road_water_pct"],
        "status": basic["status"],
        "dependency": "D_DASHBOARD",
        "notes": "W0-W3 basic classification verification",
        "recorded_at": generated_at
    })




    # ----------------------------------------------
    # L0 ~ L6：D Live QA
    # ----------------------------------------------

    live = pd.read_csv(
        LIVE_QA_PATH
    )

    live_report = pd.DataFrame({
        "case_id":
            live["case_id"],

        "description":
            live["description"],

        "category":
            "D Live QA",

        "expected":
            live["expected_behavior"],

        "actual":
            live["actual_result"],

        "road_water_pct":
            "",

        "status":
            live["status"],

        "dependency":
            live["dependency"],

        "notes":
            live["notes"],

        "recorded_at":
            generated_at
    })

    # ----------------------------------------------
    # T4 ~ T8
    # ----------------------------------------------

    extended = pd.read_csv(
        EXTENDED_QA_PATH
    )

    extended_report = pd.DataFrame({
        "case_id": extended["case_id"],
        "description": extended["description"],
        "category": "Extended Integration QA",
        "expected": extended["expected_behavior"],
        "actual": extended["actual_result"],
        "road_water_pct": "",
        "status": extended["status"],
        "dependency": extended["dependency"],
        "notes": extended["notes"],
        "recorded_at": generated_at
    })

    # ----------------------------------------------
    # 合併
    # ----------------------------------------------

    report = pd.concat(
        [
            basic_report,
            live_report,
            extended_report
        ],
        ignore_index=True
    )

    total_cases = len(report)

    pass_count = (
        report["status"] == "PASS"
    ).sum()

    fail_count = (
        report["status"] == "FAIL"
    ).sum()

    waiting_count = (
        report["status"] == "WAITING"
    ).sum()

    completed_cases = (
        pass_count
        + fail_count
    )

    completed_pass_rate = (
        pass_count / completed_cases * 100
        if completed_cases > 0
        else 0
    )

    completion_rate = (
        completed_cases / total_cases * 100
        if total_cases > 0
        else 0
    )

    summary = pd.DataFrame([
        {
            "generated_at": generated_at,
            "total_cases": total_cases,
            "completed_cases": completed_cases,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "waiting_count": waiting_count,
            "completed_pass_rate_pct": round(
                completed_pass_rate,
                1
            ),
            "qa_completion_pct": round(
                completion_rate,
                1
            )
        }
    ])

    detail_output = (
        RESULT_DIR
        / f"qa_results_{filename_time}.csv"
    )

    summary_output = (
        RESULT_DIR
        / f"qa_summary_{filename_time}.csv"
    )

    report.to_csv(
        detail_output,
        index=False,
        encoding="utf-8-sig"
    )

    summary.to_csv(
        summary_output,
        index=False,
        encoding="utf-8-sig"
    )

    return {
        "detail_path": detail_output,
        "summary_path": summary_output,
        "total_cases": total_cases,
        "completed_cases": int(completed_cases),
        "pass_count": int(pass_count),
        "fail_count": int(fail_count),
        "waiting_count": int(waiting_count),
        "pass_rate": float(
            round(
                completed_pass_rate,
                1
            )
        ),
        "completion_rate": float(
            round(
                completion_rate,
                1
            )
        ),
    }