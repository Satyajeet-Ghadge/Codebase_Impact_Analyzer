import json


def build_report(
    changes,
    file_reports,
    overall_report
):

    return {
        "changes": changes,
        "file_reports": file_reports,
        "overall": overall_report
    }


def print_json_report(report):

    print(
        json.dumps(
            report,
            indent=4
        )
    )