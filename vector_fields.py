import itertools as it
import math
import numpy as np
import matplotlib.pyplot as plt

from scipy.interpolate import NearestNDInterpolator

from matplotlib.patches import Ellipse, Annulus
from matplotlib.path import Path
from matplotlib.patches import PathPatch


def PlotShow(plot=None):
    # special magic for avoiding a blocking call
    if plot:
        plt.show(plot, block=False)
    else:
        plt.show(block=False)
    # Pause to allow the input call to run:
    plt.pause(0.001)
    input("hit [enter] to end.")
    plt.close("all")


def CircleVertices(center, radius, size):
    circ = plt.Circle(center, radius, edgecolor="b", facecolor="None")
    return circ.get_path().vertices * size


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
    # plt.show()
    PlotShow()


def Radians(point, vertex):
    px, py = point
    vx, vy = vertex
    return math.atan2((py - vy), (px - vx))


def NearestVertex(point, vertices):
    ls = (
        {
            "coord": v,
            "radians": Radians(point, v),
            "distance": np.linalg.norm(point - v),
        }
        for v in vertices
    )
    return min(ls, key=lambda x: x["distance"])


def ImpressField(field, vertices):
    for i, (point, (distance, radians)) in enumerate(field):
        nearest = NearestVertex(point, vertices)
        field[i] = (
            point, (
                nearest["distance"] - distance,
                nearest["radians"] - radians
            )
        )


def PlotField(field):

    X = field[:, [0], [0]]
    Y = field[:, [0], [1]]
    distances = field[:, [1], [0]]

    plt.scatter(X, Y, c=distances)
    PlotShow()


if __name__ == "__main__":
    size = 100
    vertices = CircleVertices((0, 0), 0.7, size)

    x, y = vertices[:, 0], vertices[:, 1]
    X = np.linspace(min(x) - 0.5, max(x) + 0.5, num=size)
    Y = np.linspace(min(y) - 0.5, max(y) + 0.5, num=size)

    coords = np.array(list(it.product(X, Y)))
    Z = np.zeros(coords.shape)
    field = np.array(list(zip(coords, Z)))

    ImpressField(field, vertices)
    PlotField(field)
