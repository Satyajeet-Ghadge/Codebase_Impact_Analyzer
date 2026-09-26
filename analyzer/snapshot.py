import os
import shutil
import subprocess
import tempfile
import zipfile


def create_git_snapshot(repo_path, ref):

    project_root = os.path.abspath(".")

    snapshot_root = tempfile.mkdtemp(
        prefix=".impact_snapshot_",
        dir=project_root
    )

    snapshot_repo = os.path.join(
        snapshot_root,
        os.path.basename(
            os.path.abspath(repo_path)
        )
    )

    os.makedirs(snapshot_repo)

    zip_path = snapshot_root + ".zip"

    try:

        result = subprocess.run(
            [
                "git",
                "-C",
                repo_path,
                "archive",
                "--format=zip",
                "-o",
                zip_path,
                ref
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:

            error = result.stderr.strip()

            raise RuntimeError(
                f"Could not create Git snapshot:\n{error}"
            )

        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as archive:

            archive.extractall(snapshot_repo)

        os.remove(zip_path)

        # IMPORTANT:
        # Return the actual repository directory,
        # not the temporary parent directory.
        return snapshot_repo.replace(
            os.sep,
            "/"
        )

    except Exception:

        if os.path.exists(zip_path):
            os.remove(zip_path)

        if os.path.exists(snapshot_root):
            shutil.rmtree(
                snapshot_root,
                ignore_errors=True
            )

        raise


def remove_git_snapshot(snapshot_path):

    if not snapshot_path:
        return

    # snapshot_path points to:
    # .impact_snapshot_xxx/sample_project
    #
    # We need to remove its parent:
    # .impact_snapshot_xxx

    snapshot_root = os.path.dirname(
        os.path.abspath(snapshot_path)
    )

    if os.path.exists(snapshot_root):
        shutil.rmtree(
            snapshot_root,
            ignore_errors=True
        )