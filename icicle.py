from collections import defaultdict
from pathlib import Path
import sys
import plotly.express as px
from dataclasses import field, dataclass

from plotly.io import renderers


@dataclass
class Node:
    children: set[str] = field(default_factory=set)
    parents: set[str] = field(default_factory=set)


def get_nodes() -> dict[str, Node]:
    edges = filter(lambda s: "->" in s, Path(sys.argv[1]).read_text().split("\n"))
    nodes = defaultdict(Node)
    for edge in edges:
        parent, child = edge.replace('"', "").replace(";", "").split(" -> ")
        nodes[parent].children.add(child)
        nodes[child].parents.add(parent)
    return nodes


def expand_nodes(nodes: dict[str, Node]) -> dict[str, Node]:
    roots = [name for name, node in nodes.items() if len(node.parents) == 0]
    if len(roots) > 1:
        raise Exception("Too many root too many many root")
    root = roots[0]

    def rec(node_name: str):
        if len(nodes[node_name].parents) > 1:
            child = nodes.pop(node_name)
            new_nodes = {
                parent_name: node_name + str(i)
                for i, parent_name in enumerate(child.parents)
            }
            for parent_name, child_name in new_nodes.items():
                nodes[child_name] = Node(child.children, {parent_name})
                nodes[parent_name].children -= {node_name}
                nodes[parent_name].children.add(child_name)

        for child in nodes[node_name].children:
            rec(child)

    rec(root)

    return nodes


# need to id duplicates better. Split down the tree. add more edges
def plot(edges: list[Node]):
    data = {"child": [], "parent": []}
    for i, edge in enumerate(edges):
        data["child"].append(edge.child.replace('"', "").replace(";", ""))
        data["parent"].append(edge.parent.replace('"', ""))
    root = [
        edge.parent.replace('"', "")
        for edge in edges
        if edge.parent not in data["child"]
    ]
    data["child"].insert(0, root[0])
    data["parent"].insert(0, "")

    data["child"] = id_duplicate_strings(data["child"])

    print(data["child"])
    print(data["parent"])
    fig = px.icicle(data, names="child", parents="parent")
    fig.update_traces(root_color="lightgrey")
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    fig.show(renderer="browser")


expand_nodes(get_nodes())
# plot2()
