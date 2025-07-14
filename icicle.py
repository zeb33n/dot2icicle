from collections import defaultdict
from pathlib import Path
import sys
import plotly.express as px


class Node:
    def __init__(self, name: str):
        self.name: str = name
        self.children: list["Node"] = []

    def __repr__(self, indent=""):
        return (
            indent
            + repr(self.name)
            + "\n"
            + "".join(child.__repr__(indent + "  ") for child in self.children)
        )


def get_nodes() -> Node:
    edges = filter(lambda s: "->" in s, Path(sys.argv[1]).read_text().split("\n"))
    edge_list = []
    for edge in edges:
        parent, child = edge.replace('"', "").replace(";", "").split(" -> ")
        edge_list.append((parent, child))

    node_names = set(key for keys in edge_list for key in keys)
    nodes = {node_name: Node(node_name) for node_name in node_names}
    for parent, child in edge_list:
        nodes[parent].children.append(nodes[child])
        node_names -= {child}

    return nodes[next(iter(node_names))]


def get_data_for_plot(root: Node) -> dict[str, list[str]]:
    data = {"child": [], "parent": [""]}
    buckets = defaultdict(lambda: 0)

    def rec(node: Node):
        buckets[node.name] += 1
        id = node.name + str(buckets[node.name])
        data["child"].append(id)
        for child in node.children:
            data["parent"].append(id)
            rec(child)

    rec(root)
    return data


# need to id duplicates better. Split down the tree. add more edges
def plot():
    node = get_nodes()
    data = get_data_for_plot(node)

    fig = px.treemap(data, names="child", parents="parent")
    fig.update_traces(root_color="lightgrey")
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    fig.show(renderer="browser")


plot()
