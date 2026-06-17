from .TorusBraidVisual import visualize_kauffman_state, visualize_tlword
from .Display import Display, VerticalSplit, HorizontalSplit, FigureContainer
from .BraidResolution import ResolutionCube

if __name__ == "__main__":

    """
    Example of multiple functionalities and composition of GUI components
    """
    window = Display(
        title="Braid Resolution",
        content=VerticalSplit(0.5)
    )
    window.content.right = HorizontalSplit(0.5)

    window.content.left = ResolutionCube(p=2, q=3)
    window.content.right.top = FigureContainer(visualize_tlword("011011"))
    window.content.right.bottom = ResolutionCube(p=1, q=3)

    window.display()


    """
    Example of an indirect map:
        0011 -> 1011 -> 1001 -> 1101
    """
    p = 2
    q = 3
    window = Display(
        title="Braid Resolution",
        content=VerticalSplit(0.5)
    )
    window.content.left = HorizontalSplit(0.5)
    window.content.right = HorizontalSplit(0.5)

    window.content.left.top = FigureContainer(visualize_tlword("01", p=p)) #0011
    window.content.right.top = FigureContainer(visualize_kauffman_state("1011", p=p, q=q))
    window.content.left.bottom = FigureContainer(visualize_kauffman_state("1001", p=p, q=q))
    window.content.right.bottom = FigureContainer(visualize_tlword("011", p=p)) #1101

    window.display()