let cy = null;

window.onload = () => {

    cy = cytoscape({

        container: document.getElementById("graph"),

        style: [

            {
                selector: "node",

                style: {
                    "background-color": "#4a90e2",
                    "label": "data(id)",
                    "text-valign": "center",
                    "text-halign": "center",
                    "color": "black",
                    "font-size": 12,
                    "width": 40,
                    "height": 40
                }
            },

            {
                selector: "edge",

                style: {
                    "curve-style": "bezier",
                    "target-arrow-shape": "triangle",
                    "line-color": "#666",
                    "target-arrow-color": "#666",
                    "width": 2
                }
            },

            {
                selector: ":selected",

                style: {
                    "background-color": "red",
                    "line-color": "red",
                    "target-arrow-color": "red"
                }
            }

        ]

    });

    cy.on("tap", "node", evt => {

        const node = evt.target;

        if (
            window.pywebview &&
            window.pywebview.api
        ) {
            window.pywebview.api.on_node_click(
                node.id()
            );
        }

    });

};


function loadGraph(data)
{

    const elements = [];

    for (const node of data.nodes)
    {
        elements.push({
            data: {
                id: node.id
            }
        });
    }

    for (const edge of data.links)
    {
        elements.push({
            data: {
                source: edge.source,
                target: edge.target
            }
        });
    }

    cy.elements().remove();

    cy.add(elements);

    cy.layout({

        name: "breadthfirst",
        
        roots: cy.getElementById(data.root),

        directed: true,

        spacingFactor: 1.5,

        animate: false,

        fit: true,

        padding: 50

    }).run();

}