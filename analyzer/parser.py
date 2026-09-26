import ast


def parse_file(file_path):
    with open(file_path, "r") as file:
        source_code = file.read()

    return ast.parse(source_code)


def extract_imports(file_path):
    tree = parse_file(file_path)

    imports = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):

            for alias in node.names:

                imports.append({
                    "module": alias.name,
                    "name": None,
                    "alias": alias.asname
                })

        elif isinstance(node, ast.ImportFrom):

            if node.module:

                for alias in node.names:

                    imports.append({
                        "module": node.module,
                        "name": alias.name,
                        "alias": alias.asname
                    })

    return imports


def extract_code_structure(file_path):
    tree = parse_file(file_path)

    structure = {
        "classes": [],
        "functions": []
    }

    for node in tree.body:

        if isinstance(node, ast.ClassDef):

            class_info = {
                "name": node.name,
                "methods": []
            }

            for child in node.body:

                if isinstance(
                    child,
                    (ast.FunctionDef, ast.AsyncFunctionDef)
                ):
                    class_info["methods"].append(child.name)

            structure["classes"].append(class_info)

        elif isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):

            structure["functions"].append(node.name)

    return structure


def extract_function_calls(file_path):
    tree = parse_file(file_path)

    function_calls = {}

    for node in ast.walk(tree):

        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):

            calls = []

            for child in ast.walk(node):

                if isinstance(child, ast.Call):

                    if isinstance(child.func, ast.Name):
                        calls.append(child.func.id)

                    elif isinstance(child.func, ast.Attribute):
                        calls.append(child.func.attr)

            function_calls[node.name] = calls

    return function_calls