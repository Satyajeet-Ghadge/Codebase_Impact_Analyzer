import os
import networkx as nx


def find_module_file(module_name, code_model):
    module_name = module_name.replace(".", os.sep)

    for file in code_model:

        normalized_file = file.replace("\\", "/")
        normalized_module = module_name.replace("\\", "/")

        if normalized_file.endswith(
            normalized_module + ".py"
        ):
            return file

    return None


def get_target_function(import_info, call_name):
    """
    Decide which actual function name a call refers to.
    """

    imported_name = import_info["name"]
    alias = import_info["alias"]

    # from database import connect
    if imported_name:

        # from database import connect as db_connect
        if alias and call_name == alias:
            return imported_name

        # from database import connect
        if call_name == imported_name:
            return imported_name

    return None


def build_function_graph(code_model):

    graph = nx.DiGraph()

    # -----------------------------------
    # 1. Create function nodes
    # -----------------------------------

    for file, details in code_model.items():

        for function in details["functions"]:

            node = f"{file}::{function}"

            graph.add_node(node)

        for class_info in details["classes"]:

            class_name = class_info["name"]

            for method in class_info["methods"]:

                node = (
                    f"{file}::"
                    f"{class_name}.{method}"
                )

                graph.add_node(node)

    # -----------------------------------
    # 2. Create function-call edges
    # -----------------------------------

    for file, details in code_model.items():

        imports = details["imports"]

        for function, calls in details["calls"].items():

            caller = f"{file}::{function}"

            for call in calls:

                # Check every imported module
                for import_info in imports:

                    module_name = import_info["module"]

                    target_file = find_module_file(
                        module_name,
                        code_model
                    )

                    if target_file is None:
                        continue

                    target_function = get_target_function(
                        import_info,
                        call
                    )

                    # Handle:
                    # from database import connect
                    #
                    # and:
                    # from database import connect as db_connect

                    if target_function:

                        target_functions = (
                            code_model[target_file]["functions"]
                        )

                        if target_function in target_functions:

                            target = (
                                f"{target_file}::"
                                f"{target_function}"
                            )

                            graph.add_edge(
                                caller,
                                target
                            )

                    # Handle:
                    # import database
                    #
                    # database.connect()
                    #
                    # The parser extracts "connect"
                    # from database.connect()

                    elif import_info["name"] is None:

                        target_functions = (
                            code_model[target_file]["functions"]
                        )

                        if call in target_functions:

                            target = (
                                f"{target_file}::"
                                f"{call}"
                            )

                            graph.add_edge(
                                caller,
                                target
                            )

    return graph