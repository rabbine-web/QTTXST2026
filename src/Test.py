from .Visuals.Display import Display, VerticalSplit, HorizontalSplit
from .Visuals.BraidResolution import ResolutionCube

if __name__ == "__main__":

    window = Display(title="Braid Resolution")
    vert_split = VerticalSplit(0.8)
    horz_split = HorizontalSplit(0.5)

    cube1 = ResolutionCube(p=2, q=3)
    cube2 = ResolutionCube(p=2, q=2)

    horz_split.bottom = cube2

    vert_split.left = cube1
    vert_split.right = horz_split
    
    window.content = vert_split

    window.display()