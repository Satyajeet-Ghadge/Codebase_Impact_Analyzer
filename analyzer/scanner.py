import os


def scan_repository(repo_path):

    files = []

    for root, directories, filenames in os.walk(repo_path):

        # Ignore unnecessary directories
        directories[:] = [
            directory
            for directory in directories
            if directory not in {
                ".git",
                "__pycache__",
                "venv",
                ".venv"
            }
        ]

        for filename in filenames:

            if not filename.endswith(".py"):
                continue

            full_path = os.path.join(
                root,
                filename
            )

            relative_path = os.path.relpath(
                full_path,
                "."
            )

            # Normalize path separators
            relative_path = relative_path.replace(
                os.sep,
                "/"
            )

            files.append(relative_path)

    return files