from multiprocessing import Process, Pipe

from src.Computation.mapping import cube_of_resolution, whittled_complex
from src.Visuals.Display import Display, FigureContainer, HorizontalSplit
from src.Visuals.GraphDisplay import GraphContainer
from src.Visuals.TorusBraidVisual import visualize_kauffman_state

parent_conn, child_conn = Pipe()

def run_graph(conn, n, k, dim):

    graph = whittled_complex(n, k)
    root_label = "0" * (k * (n - 1))

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
    k = 2
    dim = 2

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

        # print("DISPLAYING: ", state)
        display.content.top = FigureContainer(
            visualize_kauffman_state(state, k, n)
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