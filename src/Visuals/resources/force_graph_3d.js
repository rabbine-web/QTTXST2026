let Graph = null;

window.onload = () => {

    Graph = ForceGraph3D()(
        document.getElementById("graph")
    );

    Graph.backgroundColor("#ffffff")
         .nodeColor(() => "#1f77b4")
         .linkColor(() => "#444444");

    Graph.onNodeClick(node => {

        console.log("clicked", node.id);

        if (
            window.pywebview &&
            window.pywebview.api
        ) {
            window.pywebview.api.on_node_click(node.id);
        }

    });

};


function loadGraph(data)
{
    Graph.graphData(data);
}