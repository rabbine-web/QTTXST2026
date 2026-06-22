import json
import webview
import tkinter as tk
from pathlib import Path

import igraph as ig


class GraphAPI:

    def __init__(self, on_click):
        self.on_click = on_click

    def on_node_click(self, node_id):
        if self.on_click is not None:
            self.on_click(node_id)


class GraphContainer():

    def __init__(
            self, 
            graph: ig.Graph, 
            on_click=None, 
            dim=3,
            root_node=None
        ):

        self.graph = graph
        self.on_click = on_click

        if dim==2:
            self.source = "force_graph_2d.html"
        elif dim==3:
            self.source = "force_graph_3d.html"
        else:
            raise ValueError("Dimension must be 2 or 3")

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

        if root_node is None:
            root_node = nodes[0]["id"]

        print("ROOT NODE: ", root_node)

        self.graph_data = {
            "nodes": nodes,
            "links": links,
            "root": root_node
        }

    def show(self):

        api = GraphAPI(self.on_click)

        html_path = (
            Path(__file__).parent
            / "resources"
            / self.source
        )

        tmp = tk.Tk()
        tmp.withdraw()

        screen_width = tmp.winfo_screenwidth()
        screen_height = tmp.winfo_screenheight()

        tmp.destroy()

        window = webview.create_window(
            "Graph",
            html_path.as_uri(),
            js_api=api,
            width=(screen_width // 2) + 7,
            height=screen_height,
            x=-7,
            y=0
        )

        def on_loaded():
            window.evaluate_js(
                f"loadGraph({json.dumps(self.graph_data)});"
            )

        window.events.loaded += on_loaded

        webview.start()
