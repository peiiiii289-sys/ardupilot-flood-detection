from dashboard.qa_exporter import export_qa_results


def main():

    result = export_qa_results()

    print("=" * 60)
    print("D QA Formal Export")
    print("=" * 60)

    print()
    print("Total     :", result["total_cases"])
    print("Completed :", result["completed_cases"])
    print("PASS      :", result["pass_count"])
    print("FAIL      :", result["fail_count"])
    print("WAITING   :", result["waiting_count"])

    print(
        "Pass Rate :",
        f'{result["pass_rate"]:.1f}%'
    )

    print(
        "Completion:",
        f'{result["completion_rate"]:.1f}%'
    )

    print()
    print(
        "Detail :",
        result["detail_path"]
    )

    print(
        "Summary:",
        result["summary_path"]
    )

    print()
    print("QA EXPORT PASS")


if __name__ == "__main__":
    main()