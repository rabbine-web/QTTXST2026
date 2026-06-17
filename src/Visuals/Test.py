from .TorusBraidVisual import visualize_tlword
from .Display import Display, VerticalSplit, HorizontalSplit, FigureContainer
from .BraidResolution import ResolutionCube

if __name__ == "__main__":

    window = Display(
        title="Braid Resolution",
        content=VerticalSplit(0.5)
    )
    window.content.right = HorizontalSplit(0.5)

    window.content.left = ResolutionCube(p=2, q=3)
    window.content.right.top = FigureContainer(visualize_tlword("011011"))
    window.content.right.bottom = ResolutionCube(p=1, q=3)

    window.display()