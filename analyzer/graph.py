import networkx as nx

from analyzer.parser import extract_imports
from analyzer.dependency import resolve_import


def build_dependency_graph(files, repo_path):

    graph = nx.DiGraph()

    for file in files:

        graph.add_node(file)

        imports = extract_imports(file)

        for import_info in imports:

            dependency = resolve_import(
                import_info,
                repo_path
            )

            if dependency:
                graph.add_edge(
                    file,
                    dependency
                )

    return graph