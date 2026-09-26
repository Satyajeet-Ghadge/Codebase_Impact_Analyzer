import ast


class FunctionRangeVisitor(ast.NodeVisitor):

    def __init__(self):
        self.functions = []
        self.class_stack = []

    def visit_ClassDef(self, node):

        self.class_stack.append(node.name)

        self.generic_visit(node)

        self.class_stack.pop()

    def visit_FunctionDef(self, node):

        if self.class_stack:

            name = (
                ".".join(self.class_stack)
                + "."
                + node.name
            )

        else:

            name = node.name

        self.functions.append({
            "name": name,
            "start": node.lineno,
            "end": getattr(
                node,
                "end_lineno",
                node.lineno
            )
        })

        # Visit nested functions
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):

        if self.class_stack:

            name = (
                ".".join(self.class_stack)
                + "."
                + node.name
            )

        else:

            name = node.name

        self.functions.append({
            "name": name,
            "start": node.lineno,
            "end": getattr(
                node,
                "end_lineno",
                node.lineno
            )
        })

        self.generic_visit(node)


def get_function_ranges(file_path):

    try:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            source = file.read()

    except (
        FileNotFoundError,
        UnicodeDecodeError
    ):

        return []

    try:

        tree = ast.parse(source)

    except SyntaxError:

        return []

    visitor = FunctionRangeVisitor()

    visitor.visit(tree)

    return visitor.functions


def get_changed_functions(
    file_path,
    changed_line_ranges
):

    """
    Find functions whose source lines overlap
    with Git's changed line ranges.
    """

    functions = get_function_ranges(
        file_path
    )

    changed_functions = []

    for function in functions:

        function_start = function["start"]
        function_end = function["end"]

        for change_start, change_end in changed_line_ranges:

            if (
                change_start <= function_end
                and
                change_end >= function_start
            ):

                changed_functions.append(
                    function["name"]
                )

                break

    return changed_functions