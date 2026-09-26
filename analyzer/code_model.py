from analyzer.parser import (
    extract_imports,
    extract_code_structure,
    extract_function_calls
)


def build_code_model(files):
    code_model = {}

    for file in files:

        structure = extract_code_structure(file)
        calls = extract_function_calls(file)
        imports = extract_imports(file)

        code_model[file] = {
            "imports": imports,
            "classes": structure["classes"],
            "functions": structure["functions"],
            "calls": calls
        }

    return code_model