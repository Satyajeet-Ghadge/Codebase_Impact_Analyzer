import networkx as nx


def find_impact(graph, changed_file):

    if changed_file not in graph:
        return []

    reversed_graph = graph.reverse()

    affected_files = nx.descendants(
        reversed_graph,
        changed_file
    )

    return list(affected_files)