import networkx as nx


def find_function_impact(function_graph, changed_function):

    if changed_function not in function_graph:
        return []

    reversed_graph = function_graph.reverse()

    affected_functions = nx.descendants(
        reversed_graph,
        changed_function
    )

    return list(affected_functions)


def get_functions_in_file(code_model, file_path):

    if file_path not in code_model:
        return []

    functions = []

    details = code_model[file_path]

    # Normal functions
    for function in details["functions"]:

        functions.append(
            f"{file_path}::{function}"
        )

    # Class methods
    for class_info in details["classes"]:

        class_name = class_info["name"]

        for method in class_info["methods"]:

            functions.append(
                f"{file_path}::{class_name}.{method}"
            )

    return functions