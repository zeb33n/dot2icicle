from collections import defaultdict
from pathlib import Path
import sys
import plotly.express as px
from dataclasses import dataclass

from plotly.io import renderers


@dataclass
class Edge:
    parent: str
    child: str


def get_edges() -> list[Edge]:
    edges = filter(lambda s: "->" in s, Path(sys.argv[1]).read_text().split("\n"))
    out = []
    for edge in edges:
        out.append(Edge(*edge.split(" -> ")))
    return out


def id_duplicate_strings(ls: list[str]) -> list[str]:
    buckets = defaultdict(lambda: 0)
    for s in ls:
        buckets[s] += 1
    for i, s in enumerate(ls):
        if buckets[s] > 1:
            ls[i] = s + str(buckets[s])
            buckets[s] -= 1
    return ls


# need to id duplicates better. Split down the tree. add more edges
def plot(edges: list[Edge]):
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


plot(get_edges())
# plot2()
