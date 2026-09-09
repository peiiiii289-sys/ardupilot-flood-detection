from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    BASE_DIR
    / "tests"
    / "extended_qa_results.csv"
)


CASES = [
    {
        "case_id": "T4",
        "description": "陰影",
        "purpose": "測試是否將道路陰影誤判為積水",
        "dependency": "A_AI",
        "expected_behavior": "不得因陰影本身造成錯誤積水判定",
        "actual_result": "",
        "status": "WAITING",
        "notes": "等待 A 的真實 AI 模型與測試影像"
    },
    {
        "case_id": "T5",
        "description": "強反光",
        "purpose": "測試反射光是否造成積水誤判",
        "dependency": "A_AI",
        "expected_behavior": "不得因強反光本身造成錯誤積水判定",
        "actual_result": "",
        "status": "WAITING",
        "notes": "等待 A 的真實 AI 模型與測試影像"
    },
    {
        "case_id": "T6",
        "description": "車輛或物體遮擋",
        "purpose": "測試遮擋情況下的辨識穩定性",
        "dependency": "A_AI",
        "expected_behavior": "遮擋情況下輸出應保持合理且可判讀",
        "actual_result": "",
        "status": "WAITING",
        "notes": "等待 A 的真實 AI 模型與遮擋場景"
    },
    {
        "case_id": "T7",
        "description": "手機串流斷線",
        "purpose": "測試 Camera 輸入中斷與備援",
        "dependency": "C_CAMERA",
        "expected_behavior": "偵測到輸入中斷並可切換至備援來源",
        "actual_result": "",
        "status": "WAITING",
        "notes": "等待 C Camera 模組整合"
    },
    {
        "case_id": "T8",
        "description": "MAVLink 暫時失聯",
        "purpose": "測試通訊失聯與恢復狀態",
        "dependency": "B_MAVLINK",
        "expected_behavior": "可顯示通訊異常並在連線恢復後正常更新",
        "actual_result": "",
        "status": "WAITING",
        "notes": "等待 B MAVLink 整合"
    }
]


df = pd.DataFrame(CASES)

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


print("=" * 60)
print("D Extended QA Framework Generator")
print("=" * 60)

print("Output :", OUTPUT_FILE)
print("Cases  :", len(df))

print()

print(
    df[
        [
            "case_id",
            "description",
            "dependency",
            "status"
        ]
    ].to_string(index=False)
)

print()
print("EXTENDED QA FRAMEWORK PASS")