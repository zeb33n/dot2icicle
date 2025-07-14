from collections import defaultdict
from pathlib import Path
import sys
import plotly.express as px
from dataclasses import field, dataclass
from copy import deepcopy


@dataclass
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


# def expand_nodes(nodes: dict[str, Node]) -> dict[str, Node]:
#     roots = [name for name, node in nodes.items() if len(node.parents) == 0]
#     if len(roots) > 1:
#         raise Exception("Too many root too many many root")
#     root = roots[0]

#     seen = set()

#     def rec(node_name: str):
#         if node_name in seen:
#             return
#         seen.add(node_name)
#         if len(nodes[node_name].parents) > 1:
#             child = nodes.pop(node_name)
#             new_nodes = {
#                 parent_name: node_name + str(i)
#                 for i, parent_name in enumerate(child.parents)
#             }
#             children = []
#             for parent_name, child_name in new_nodes.items():
#                 nodes[child_name] = Node(child.children, {parent_name})
#                 nodes[parent_name].children -= {node_name}
#                 nodes[parent_name].children.add(child_name)
#                 children.append(child_name)
#             for child_name in children:
#                 ccs = deepcopy(nodes[child_name].children)
#                 for child_child in ccs:
#                     print(len(ccs))
#                     new_names = list(new_nodes.values())
#                     nodes[child_child].parents = (
#                         nodes[child_child].parents - {node_name}
#                     ).union(new_names)
#                     print(node_name)
#                     print(child_child)
#                     print(nodes[child_child].parents)
#                     rec(child_child)
#         else:
#             for child in nodes[node_name].children:
#                 rec(child)

#     rec(root)

#     return nodes


# while no nodes have
# loop through nodes
# if num parents > 1
# pop current node
# make copies of nodes with ids for num of parents
#


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

    for child, parent in zip(data["child"], data["parent"]):
        print(child)
        print(parent)
        print("")

    print(data["child"])
    print(data["parent"])
    fig = px.icicle(data, names="child", parents="parent")
    fig.update_traces(root_color="lightgrey")
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
    fig.show(renderer="browser")


plot()
