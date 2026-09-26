import subprocess


def run_git_command(repo_path, command):

    result = subprocess.run(
        [
            "git",
            "-C",
            repo_path
        ] + command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        error = result.stderr.strip()

        raise RuntimeError(
            f"Git command failed:\n{error}"
        )

    return result.stdout


def parse_git_status(output):

    changes = []

    for line in output.splitlines():

        line = line.strip()

        if not line:
            continue

        parts = line.split("\t")

        status = parts[0]

        if status in {"M", "A", "D"}:

            if len(parts) >= 2:

                changes.append({
                    "status": status,
                    "path": parts[1]
                })

        elif status.startswith("R"):

            if len(parts) >= 3:

                changes.append({
                    "status": "R",
                    "old_path": parts[1],
                    "path": parts[2]
                })

    return changes


def get_changed_file_status(repo_path):

    output = run_git_command(
        repo_path,
        [
            "diff",
            "--name-status",
            "-M"
        ]
    )

    return parse_git_status(output)


def get_commit_file_status(
    repo_path,
    commit
):

    output = run_git_command(
        repo_path,
        [
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-status",
            "-M",
            "-r",
            commit
        ]
    )

    return parse_git_status(output)


def get_range_file_status(
    repo_path,
    base,
    head
):

    output = run_git_command(
        repo_path,
        [
            "diff",
            "--name-status",
            "-M",
            base,
            head
        ]
    )

    return parse_git_status(output)


# ========================================
# Changed line ranges
# ========================================

def parse_changed_line_ranges(output):

    changed_lines = {}

    current_file = None

    for line in output.splitlines():

        if line.startswith("+++ b/"):

            current_file = line[6:]

            changed_lines.setdefault(
                current_file,
                []
            )

            continue

        if line.startswith("--- "):

            continue

        if line.startswith("@@"):

            try:

                section = line.split("@@")[1].strip()

                new_part = section.split()[1]

                new_part = new_part.lstrip("+")

                if "," in new_part:

                    start, count = (
                        new_part.split(",")
                    )

                    start = int(start)
                    count = int(count)

                else:

                    start = int(new_part)
                    count = 1

                if count == 0:

                    continue

                end = start + count - 1

                if current_file:

                    changed_lines[
                        current_file
                    ].append(
                        (start, end)
                    )

            except (
                ValueError,
                IndexError
            ):

                continue

    return changed_lines


def get_changed_line_ranges(repo_path):

    output = run_git_command(
        repo_path,
        [
            "diff",
            "--unified=0"
        ]
    )

    return parse_changed_line_ranges(
        output
    )


def get_commit_changed_line_ranges(
    repo_path,
    commit
):

    output = run_git_command(
        repo_path,
        [
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--unified=0",
            "-p",
            "-r",
            commit
        ]
    )

    return parse_changed_line_ranges(
        output
    )


def get_range_changed_line_ranges(
    repo_path,
    base,
    head
):

    output = run_git_command(
        repo_path,
        [
            "diff",
            "--unified=0",
            base,
            head
        ]
    )

    return parse_changed_line_ranges(
        output
    )


# ========================================
# Existing filename functions
# ========================================

def get_changed_files(repo_path):

    changes = get_changed_file_status(
        repo_path
    )

    return [
        change["path"]
        for change in changes
    ]


def get_commit_changed_files(
    repo_path,
    commit
):

    changes = get_commit_file_status(
        repo_path,
        commit
    )

    return [
        change["path"]
        for change in changes
    ]


def get_range_changed_files(
    repo_path,
    base,
    head
):

    changes = get_range_file_status(
        repo_path,
        base,
        head
    )

    return [
        change["path"]
        for change in changes
    ]