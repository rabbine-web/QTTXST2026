from multiprocessing import Process, Pipe

import igraph as ig

from src.Computation.TemperleyLieb import (
    surviving_tl_states,
    tl_to_kauffman,
    kauffman_direct_maps
)
from src.Visuals.Display import (
    Display, 
    FigureContainer, 
    HorizontalSplit
)
from src.Visuals.GraphDisplay import GraphContainer
from src.Visuals.TorusBraidVisual import visualize_kauffman_state

parent_conn, child_conn = Pipe()

def whittled_graph(maxHomDegree: int, numStrands: int) -> ig.Graph:

    if (numStrands != 3):
        raise ValueError("numStrands must be 3")

    if (maxHomDegree < 0):
        raise ValueError("maxHomDegree must be at least 0")

    tl_by_degree = [surviving_tl_states(3, i) for i in range(maxHomDegree + 1)]
    tl_states = [state for states in tl_by_degree for state in states]
    kauffman_by_degree = [
        [
            tl_to_kauffman(state, maxHomDegree) for state in tl_states
        ] for tl_states in tl_by_degree
    ]
    kauffman_states = [state for states in kauffman_by_degree for state in states]

    G = ig.Graph(directed=True)

    G.add_vertices(kauffman_states)
    G.vs["label"] = [state.lstrip('0') or '0' for state in kauffman_states]
    G.vs["tl"] = tl_states

    direct_maps = kauffman_direct_maps(kauffman_by_degree)

    G.add_edges(direct_maps)

    return G


def run_graph(conn, n, k, dim):

    graph = whittled_graph(
        maxHomDegree=k, 
        numStrands=n
    )
    root_label = "0"

    GraphContainer(
        graph,
        on_click=lambda state: graph_click(conn, state),
        dim=dim,
        root_node=root_label
    ).show()

def graph_click(conn, state: str):
    
    print("CLICKED: ", state)
    conn.send(state)

if __name__ == "__main__":

    n = 3
    k = 500
    dim = 3

    graph_process = Process(
        target=run_graph,
        args=(child_conn, n, k, dim)
    )

    graph_process.start()

    display = Display(
        title ="3-Braid",
        content=HorizontalSplit(ratio=0.33),
        fullscreen=False
    )
    display.display()

    def display_state(state: str):

        display.content.top = FigureContainer(
            visualize_kauffman_state(
                state, 
                len(state)//2+1, 
                n
            )
        )
        display.refresh()

    def poll_graph():

        while parent_conn.poll():

            state = parent_conn.recv()

            display_state(state)

        display.root.after(
            50,
            poll_graph
        )

    poll_graph()
    display.root.mainloop()

    ## set size and position here to be full height, half width (of screen) and pushed to the right edge