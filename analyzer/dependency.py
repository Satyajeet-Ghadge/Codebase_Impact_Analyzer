import os


def resolve_import(import_info, repo_path):

    module_name = import_info["module"]

    module_path = module_name.replace(
        ".",
        os.sep
    ) + ".py"

    candidate = os.path.join(
        repo_path,
        module_path
    )

    if os.path.exists(candidate):
        return candidate.replace(
            os.sep,
            "/"
        )

    return None