import json
import tempfile
import webview

import igraph as ig

from .Display import Container


class GraphAPI:

    def __init__(self, on_click):
        self.on_click = on_click

    def on_node_click(self, node_id):
        if self.on_click is not None:
            self.on_click(node_id)


class GraphContainer(Container):

    def __init__(self, graph: ig.Graph, on_click=None):
        self.graph = graph
        self.on_click = on_click

        nodes = [
            {
                "id": str(v["label"])
                if "label" in v.attributes()
                else str(v.index)
            }
            for v in self.graph.vs
        ]

        links = [
            {
                "source": nodes[e.source]["id"],
                "target": nodes[e.target]["id"]
            }
            for e in self.graph.es
        ]

        graph_data = {
            "nodes": nodes,
            "links": links
        }

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://unpkg.com/3d-force-graph"></script>
    <style>
        html, body {{
            margin: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
        }}

        #graph {{
            width: 100vw;
            height: 100vh;
        }}
    </style>
</head>
<body>

<div id="graph"></div>

<script>

const data = {json.dumps(graph_data)};

const Graph = ForceGraph3D()(
    document.getElementById('graph')
);

Graph.graphData(data);

Graph.onNodeClick(node => {{

    console.log("clicked", node.id);

    if (
        window.pywebview &&
        window.pywebview.api
    ) {{
        window.pywebview.api.on_node_click(node.id);
    }}

}});

</script>

</body>
</html>
"""

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".html",
            delete=False,
            encoding="utf-8"
        ) as f:

            f.write(html)
            path = f.name

        api = GraphAPI(self.on_click)

        webview.create_window(
            "Graph",
            path,
            js_api=api,
            width=800,
            height=600
        )

        webview.start()

    def draw(self, frame: tk.Frame) -> None:
        
        pass
