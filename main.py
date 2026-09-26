import os
import sys
import argparse
import networkx as nx
import atexit



from analyzer.git_analyzer import (
    get_changed_file_status,
    get_commit_file_status,
    get_range_file_status,
    get_changed_line_ranges,
    get_commit_changed_line_ranges,
    get_range_changed_line_ranges
)

from analyzer.scanner import scan_repository

from analyzer.code_model import (
    build_code_model
)

from analyzer.snapshot import (
    create_git_snapshot,
    remove_git_snapshot
)

from analyzer.graph import (
    build_dependency_graph
)


from analyzer.function_graph import (
    build_function_graph
)

from analyzer.impact_analyzer import (
    find_impact
)

from analyzer.function_impact import (
    find_function_impact
)

from analyzer.change_detector import (
    get_changed_functions
)

from analyzer.test_analyzer import (
    find_test_files,
    find_affected_tests
)

from analyzer.risk_analyzer import (
    calculate_impact_score,
    get_risk_level,
    classify_file_impact,
    find_public_functions
)

from analyzer.report import (
    build_report,
    print_json_report
)


# ========================================
# Configuration
# ========================================

parser = argparse.ArgumentParser(
    description="Analyze code changes and their potential impact."
)

parser.add_argument(
    "--repo",
    default="sample_project",
    help="Path to the repository"
)

parser.add_argument(
    "--commit",
    help="Analyze changes introduced by a Git commit"
)

parser.add_argument(
    "--base",
    help="Base Git commit or branch for range analysis"
)

parser.add_argument(
    "--head",
    help="Head Git commit or branch for range analysis"
)

parser.add_argument(
    "--format",
    choices=["text", "json"],
    default="text",
    help="Output format"
)

parser.add_argument(
    "--ci",
    action="store_true",
    help="Run in CI mode and fail when the risk threshold is reached"
)

parser.add_argument(
    "--fail-on",
    choices=["low", "medium", "high"],
    default="high",
    help="Risk level that should cause CI failure"
)

args = parser.parse_args()

repo_path = args.repo

analysis_repo_path = repo_path
snapshot_path = None

if args.commit:
    snapshot_path = create_git_snapshot(
        repo_path,
        args.commit
    )
    analysis_repo_path = snapshot_path

elif args.base and args.head:
    snapshot_path = create_git_snapshot(
        repo_path,
        args.head
    )
    analysis_repo_path = snapshot_path

if snapshot_path:
    atexit.register(
        remove_git_snapshot,
        snapshot_path
    )

def display_path(path):

    if not snapshot_path:
        return path

    normalized_path = (
        path.replace("\\", "/")
    )

    normalized_snapshot = (
        snapshot_path.replace("\\", "/")
    )

    normalized_repo = (
        repo_path.replace("\\", "/")
    )

    if normalized_path.startswith(
        normalized_snapshot + "/"
    ):

        relative_part = (
            normalized_path[
                len(normalized_snapshot) + 1:
            ]
        )

        return (
            normalized_repo.rstrip("/")
            + "/"
            + relative_part
        )

    return path


def display_function(function):

    if "::" not in function:

        return display_path(function)

    file_part, function_name = (
        function.split(
            "::",
            1
        )
    )

    return (
        display_path(file_part)
        + "::"
        + function_name
    )

analysis_repo_path = repo_path

snapshot_path = None


# ========================================
# Create Git snapshot when needed
# ========================================

if args.commit:

    snapshot_path = create_git_snapshot(
        repo_path,
        args.commit
    )

    analysis_repo_path = snapshot_path


elif args.base and args.head:

    snapshot_path = create_git_snapshot(
        repo_path,
        args.head
    )

    analysis_repo_path = snapshot_path


if snapshot_path:

    atexit.register(
        remove_git_snapshot,
        snapshot_path
    )


# ========================================
# 1. Scan repository
# ========================================

files = scan_repository(
    analysis_repo_path
)


# ========================================
# 2. Separate test files
# ========================================

test_files = find_test_files(
    files
)

production_files = [
    file
    for file in files
    if file not in test_files
]


# ========================================
# 3. Build production code model
# ========================================

code_model = build_code_model(
    production_files
)


# ========================================
# 4. Build file dependency graph
# ========================================

file_graph = build_dependency_graph(
    production_files,
    analysis_repo_path
)

# ========================================
# 5. Build function dependency graph
# ========================================

function_graph = build_function_graph(
    code_model
)


# ========================================
# 6. Get Git changes + line ranges
# ========================================

if args.commit:

    changes = get_commit_file_status(
        repo_path,
        args.commit
    )

    changed_line_ranges_by_file = (
        get_commit_changed_line_ranges(
            repo_path,
            args.commit
        )
    )

elif args.base and args.head:

    changes = get_range_file_status(
        repo_path,
        args.base,
        args.head
    )

    changed_line_ranges_by_file = (
        get_range_changed_line_ranges(
            repo_path,
            args.base,
            args.head
        )
    )

elif args.base or args.head:

    print(
        "\nError: --base and --head "
        "must be used together."
    )

    raise SystemExit(1)

else:

    changes = get_changed_file_status(
        repo_path
    )

    changed_line_ranges_by_file = (
        get_changed_line_ranges(
            repo_path
        )
    )


# ========================================
# 7. Get analyzable changed files
# ========================================

changed_files = []

for change in changes:

    # Deleted files no longer exist
    if change["status"] == "D":
        continue

    changed_files.append(
        change["path"]
    )


# ========================================
# 8. Overall impact tracking
# ========================================

all_affected_files = set()

all_affected_functions = set()

all_affected_tests = set()

all_direct_files = set()

all_indirect_files = set()

all_public_functions = set()

all_changed_functions = set()

overall_max_depth = 0

file_reports = []


# ========================================
# 9. Analyze each changed file
# ========================================

for file in changed_files:

    changed_file = os.path.join(
        analysis_repo_path,
        file
    ).replace(os.sep, "/")

    # ====================================
    # File impact
    # ====================================

    affected_files = find_impact(
        file_graph,
        changed_file
    )

    all_affected_files.update(
        affected_files
    )

    # ====================================
    # Direct / indirect impact
    # ====================================

    direct_files, indirect_files = (
        classify_file_impact(
            file_graph,
            changed_file,
            affected_files
        )
    )

    all_direct_files.update(
        direct_files
    )

    all_indirect_files.update(
        indirect_files
    )

    # ====================================
    # Dependency depth
    # ====================================

    max_depth = 0

    if changed_file in file_graph:

        reversed_graph = (
            file_graph.reverse()
        )

        for affected_file in affected_files:

            try:

                depth = nx.shortest_path_length(
                    reversed_graph,
                    changed_file,
                    affected_file
                )

                max_depth = max(
                    max_depth,
                    depth
                )

            except nx.NetworkXNoPath:

                continue

    overall_max_depth = max(
        overall_max_depth,
        max_depth
    )

    # ====================================
    # EXACT changed functions
    # ====================================

    changed_line_ranges = (
        changed_line_ranges_by_file.get(
            file,
            []
        )
    )

    # Git paths may sometimes contain the
    # repository directory.
    if not changed_line_ranges:

        for git_file, ranges in (
            changed_line_ranges_by_file.items()
        ):

            normalized_git_file = (
                git_file.replace("\\", "/")
            )

            normalized_file = (
                file.replace("\\", "/")
            )

            if (
                normalized_git_file == normalized_file
                or
                normalized_git_file.endswith(
                    "/" + normalized_file
                )
            ):

                changed_line_ranges = ranges

                break

    changed_function_names = (
        get_changed_functions(
            changed_file,
            changed_line_ranges
        )
    )

    changed_functions = [
        f"{changed_file}::{function}"
        for function in changed_function_names
    ]

    all_changed_functions.update(
        changed_functions
    )

    # ====================================
    # Function impact
    # ====================================

    all_file_affected_functions = set(
        changed_functions
    )

    for function in changed_functions:

        affected_functions = (
            find_function_impact(
                function_graph,
                function
            )
        )

        all_file_affected_functions.update(
            affected_functions
        )

    production_affected_functions = [

        function

        for function
        in all_file_affected_functions

        if function not in changed_functions

        and "\\tests\\" not in function

        and "/tests/" not in function
    ]

    all_affected_functions.update(
        production_affected_functions
    )

    # ====================================
    # Public functions
    # ====================================

    public_affected_functions = (
        find_public_functions(
            code_model,
            production_affected_functions
        )
    )

    all_public_functions.update(
        public_affected_functions
    )

    # ====================================
    # Test impact
    # ====================================

    affected_tests = find_affected_tests(
        test_files,
        code_model,
        all_file_affected_functions
    )

    all_affected_tests.update(
        affected_tests
    )

    # ====================================
    # Per-file score
    # ====================================

    impact_score = calculate_impact_score(
        direct_files,
        indirect_files,
        production_affected_functions,
        affected_tests,
        max_depth
    )

    risk_level = get_risk_level(
        impact_score
    )

    # ====================================
    # Store structured report
    # ====================================

    file_reports.append({

        "file": file,

        "changed_functions": (
            changed_functions
        ),

        "affected_files": (
            affected_files
        ),

        "direct_files": (
            direct_files
        ),

        "indirect_files": (
            indirect_files
        ),

        "affected_functions": (
            production_affected_functions
        ),

        "public_functions": (
            public_affected_functions
        ),

        "affected_tests": (
            affected_tests
        ),

        "maximum_depth": (
            max_depth
        ),

        "impact_score": (
            impact_score
        ),

        "risk_level": (
            risk_level
        )
    })


# ========================================
# 10. Overall tests
# ========================================

overall_test_functions = set(
    all_changed_functions
)

overall_test_functions.update(
    all_affected_functions
)

overall_affected_tests = (
    find_affected_tests(
        test_files,
        code_model,
        overall_test_functions
    )
)


# ========================================
# 11. Overall report
# ========================================

overall_score = calculate_impact_score(
    all_direct_files,
    all_indirect_files,
    all_affected_functions,
    overall_affected_tests,
    overall_max_depth
)

overall_risk = get_risk_level(
    overall_score
)


overall_report = {

    "changed_files": len(changes),

    "affected_files": len(
        all_affected_files
    ),

    "affected_functions": len(
        all_affected_functions
    ),

    "public_functions": len(
        all_public_functions
    ),

    "affected_tests": len(
        overall_affected_tests
    ),

    "maximum_depth": (
        overall_max_depth
    ),

    "direct_files": len(
        all_direct_files
    ),

    "indirect_files": len(
        all_indirect_files
    ),

    "impact_score": (
        overall_score
    ),

    "risk_level": (
        overall_risk
    )
}


# ========================================
# 12. Build final report
# ========================================

report = build_report(
    changes,
    file_reports,
    overall_report
)


# ========================================
# 13. JSON / Text output
# ========================================

if args.format == "json":

    print_json_report(
        report
    )

else:

    print("\n" + "=" * 55)

    print(
        "              CODEBASE IMPACT ANALYZER"
    )

    print("=" * 55)

    # ====================================
    # Changes
    # ====================================

    print("\nChanges")

    print("-" * 55)

    if not changes:

        print("  No changed files found.")

    else:

        for change in changes:

            status = change["status"]

            if status == "M":

                print(
                    f"  Modified: {change['path']}"
                )

            elif status == "A":

                print(
                    f"  Added: {change['path']}"
                )

            elif status == "D":

                print(
                    f"  Deleted: {change['path']}"
                )

            elif status == "R":

                print(
                    f"  Renamed: "
                    f"{change['old_path']} → "
                    f"{change['path']}"
                )

    # ====================================
    # Individual reports
    # ====================================

    for file_report in file_reports:

        print(
            "\n" + "-" * 55
        )

        print(
            f"Impact of: "
            f"{file_report['file']}"
        )

        print("-" * 55)

        print(
            "\nPotentially Affected Files:"
        )

        if file_report["affected_files"]:

            for file in file_report[
                "affected_files"
            ]:

                print(
                    f"  {file}"
                )

        else:

            print("  None")

        print(
            "\nChanged Functions:"
        )

        if file_report[
            "changed_functions"
        ]:

            for function in file_report[
                "changed_functions"
            ]:

                print(
                    f"  {function}"
                )

        else:

            print("  None")

        print(
            "\nPotentially Affected Functions:"
        )

        if file_report[
            "affected_functions"
        ]:

            for function in file_report[
                "affected_functions"
            ]:

                print(
                    f"  {function}"
                )

        else:

            print("  None")

        print(
            "\nPotentially Affected Tests:"
        )

        if file_report[
            "affected_tests"
        ]:

            for test in file_report[
                "affected_tests"
            ]:

                print(
                    f"  {test}"
                )

        else:

            print("  None")

        print("\nImpact Summary")

        print("-" * 55)

        print(
            f"  Files affected:      "
            f"{len(file_report['affected_files'])}"
        )

        print(
            f"  Functions affected:  "
            f"{len(file_report['affected_functions'])}"
        )

        print(
            f"  Public functions:    "
            f"{len(file_report['public_functions'])}"
        )

        print(
            f"  Tests affected:      "
            f"{len(file_report['affected_tests'])}"
        )

        print(
            f"  Maximum depth:       "
            f"{file_report['maximum_depth']}"
        )

        print(
            f"  Direct files:        "
            f"{len(file_report['direct_files'])}"
        )

        print(
            f"  Indirect files:      "
            f"{len(file_report['indirect_files'])}"
        )

        print(
            f"  Impact Score:        "
            f"{file_report['impact_score']}"
        )

        print(
            f"  Risk Level:          "
            f"{file_report['risk_level']}"
        )

    # ====================================
    # Overall report
    # ====================================

    print(
        "\n" + "=" * 55
    )

    print(
        "              OVERALL IMPACT REPORT"
    )

    print(
        "=" * 55
    )

    print(
        f"\n  Changed files:        "
        f"{overall_report['changed_files']}"
    )

    print(
        f"  Affected files:       "
        f"{overall_report['affected_files']}"
    )

    print(
        f"  Affected functions:   "
        f"{overall_report['affected_functions']}"
    )

    print(
        f"  Public functions:     "
        f"{overall_report['public_functions']}"
    )

    print(
        f"  Affected tests:       "
        f"{overall_report['affected_tests']}"
    )

    print(
        f"  Maximum depth:        "
        f"{overall_report['maximum_depth']}"
    )

    print(
        f"  Direct files:         "
        f"{overall_report['direct_files']}"
    )

    print(
        f"  Indirect files:       "
        f"{overall_report['indirect_files']}"
    )

    print(
        f"  Impact Score:         "
        f"{overall_report['impact_score']}"
    )

    print(
        f"  Risk Level:           "
        f"{overall_report['risk_level']}"
    )

    print(
        "\n" + "=" * 55
    )


# ========================================
# 14. CI mode
# ========================================

if args.ci:

    risk_values = {
        "low": 1,
        "medium": 2,
        "high": 3
    }

    actual_risk = risk_values[
        overall_risk.lower()
    ]

    failure_threshold = risk_values[
        args.fail_on.lower()
    ]

    print(
        f"\nCI Mode: "
        f"threshold = {args.fail_on.upper()}"
    )

    if actual_risk >= failure_threshold:

        print(
            "CI Result: FAILED"
        )

        sys.exit(1)

    else:

        print(
            "CI Result: PASSED"
        )

        sys.exit(0)