def calculate_impact_score(
    direct_files,
    indirect_files,
    affected_functions,
    affected_tests,
    max_depth
):

    score = 0

    # Direct dependencies are more important
    score += len(direct_files) * 2

    # Indirect dependencies still contribute
    score += len(indirect_files)

    # Function impact
    score += len(affected_functions) * 2

    # Test impact
    score += len(affected_tests) * 2

    # Deeper dependency chains increase impact
    score += max_depth * 2

    return score


def get_risk_level(score):

    if score <= 5:
        return "LOW"

    elif score <= 12:
        return "MEDIUM"

    return "HIGH"


def classify_file_impact(
    file_graph,
    changed_file,
    affected_files
):

    reversed_graph = file_graph.reverse()

    direct_files = set()

    if changed_file in reversed_graph:

        direct_files = set(
            reversed_graph.successors(
                changed_file
            )
        )

    indirect_files = set(
        affected_files
    ) - direct_files

    return (
        list(direct_files),
        list(indirect_files)
    )


def find_public_functions(
    code_model,
    functions
):

    public_functions = []

    for function in functions:

        function_name = function.split("::")[-1]

        # Handle class methods:
        # file.py::Class.method
        if "." in function_name:

            function_name = (
                function_name.split(".")[-1]
            )

        # Python naming convention:
        # _function = private/internal
        # function = public
        if not function_name.startswith("_"):

            public_functions.append(
                function
            )

    return public_functions