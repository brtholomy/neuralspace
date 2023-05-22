import itertools as it
import math
from statistics import mean
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from scipy.interpolate import NearestNDInterpolator


def GetVertices(polygon):
    return polygon.get_path().vertices


def CircleVertices(center, radius):
    return GetVertices(patches.Circle(center, radius))


def EllipseVertices(center, width, height, angle):
    return (
        GetVertices(
            # these parameters aren't doing anything when I get the path:
            patches.Ellipse(center, width, height, angle=angle)
        )
        * (width, height)
        + center
    )


def RectangleVertices(center, width, height, angle):
    return (
        GetVertices(patches.Rectangle(center, width, height, angle=angle))
        * (width, height)
        + center
    )


def NN():
    vertices = CircleVertices()
    x, y = vertices[:, 0], vertices[:, 1]
    z = [np.hypot(x, y) for x, y in vertices]

    X = np.linspace(min(x) - 0.5, max(x) + 0.5, num=size)
    Y = np.linspace(min(y) - 0.5, max(y) + 0.5, num=size)

    X, Y = np.meshgrid(X, Y)
    interp = NearestNDInterpolator(list(zip(x, y)), z)
    Z = interp(X, Y)

    plt.pcolormesh(X, Y, Z, shading="auto")
    plt.plot(x, y, "ok", label="input point")

    plt.legend()
    plt.colorbar()
    plt.axis("equal")
    viz.PlotShow()


def Slope(point, vertex):
    px, py = point
    vx, vy = vertex
    return (py - vy), (px - vx)


def Radians(point, vertex):
    return math.atan2(*Slope(point, vertex))


def NearestVertex(point, vertices):
    ls = (
        {
            "coord": v,
            "radians": Radians(point, v),
            # "slope": Slope(point, v),
            "distance": np.linalg.norm(point - v),
        }
        for v in vertices
    )
    return min(ls, key=lambda x: x["distance"])


def ImpressField(field, vertices, strength):
    for i, (point, (distance, radians)) in enumerate(field):
        nearest = NearestVertex(point, vertices)
        field[i] = (
            point,
            (
                # adjusting the distance by a strength factor, not simply
                # resetting it:
                mean(((strength * nearest["distance"]), distance)),
                (strength * nearest["radians"]) - radians,
            ),
        )


def PlotField(field):
    X = field[:, [0], [0]]
    Y = field[:, [0], [1]]
    distances = field[:, [1], [0]]

    plt.scatter(X, Y, c=distances)
    plt.colorbar(label="firing path resistance")
    plt.axis("equal")
    viz.PlotShow()


if __name__ == "__main__":
    size = 100
    Z_FIELDS = 2

    # vertices = CircleVertices((0, 0), 0.5)
    # vertices = RectangleVertices((0., 0.), 0.9, 0.3, 30)
    vertices = EllipseVertices((0.3, 0.3), 0.9, 0.45, 30)
    hole = np.array([[-1.3, -1.3]])

    # x, y = vertices[:, 0], vertices[:, 1]
    # X = np.linspace(min(x) - 0.5, max(x) + 0.5, num=size)
    # Y = np.linspace(min(y) - 0.5, max(y) + 0.5, num=size)
    X = np.linspace(-1.5, 1.5, num=size)
    Y = np.linspace(-1.5, 1.5, num=size)

    coords = np.array(list(it.product(X, Y)))
    Z = np.zeros((len(coords), Z_FIELDS))
    field = np.array(list(zip(coords, Z)))

    ImpressField(field, hole, strength=0.5)
    ImpressField(field, vertices, strength=1)
    PlotField(field)
