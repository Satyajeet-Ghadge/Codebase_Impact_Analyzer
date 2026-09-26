import os

from analyzer.parser import (
    extract_imports,
    extract_function_calls
)


def find_test_files(files):

    test_files = []

    for file in files:

        filename = os.path.basename(file)

        if (
            filename.startswith("test_")
            or filename.endswith("_test.py")
        ):
            test_files.append(file)

    return test_files


def get_test_dependencies(test_file):

    imports = extract_imports(test_file)
    calls = extract_function_calls(test_file)

    return {
        "imports": imports,
        "calls": calls
    }


def find_test_function_dependencies(
    test_file,
    code_model
):

    dependencies = []

    test_info = get_test_dependencies(test_file)

    imports = test_info["imports"]

    for import_info in imports:

        imported_function = import_info["name"]

        if not imported_function:
            continue

        module_name = import_info["module"]

        for file in code_model:

            filename = os.path.splitext(
                os.path.basename(file)
            )[0]

            if filename == module_name:

                functions = (
                    code_model[file]["functions"]
                )

                if imported_function in functions:

                    target = (
                        f"{file}::"
                        f"{imported_function}"
                    )

                    dependencies.append(target)

    return dependencies


def find_affected_tests(
    test_files,
    code_model,
    affected_functions
):

    affected_tests = []

    for test_file in test_files:

        dependencies = find_test_function_dependencies(
            test_file,
            code_model
        )

        for dependency in dependencies:

            if dependency in affected_functions:

                affected_tests.append(test_file)

                break

    return affected_tests