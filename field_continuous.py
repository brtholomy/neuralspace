from collections import namedtuple
from dataclasses import dataclass
import math
from statistics import fmean

import numpy as np
import sympy as sp


@dataclass
class Inertia:
    magnitude: float
    radians: float


@dataclass
class JumpSpec:
    radius: float
    arc: float
    granularity: int


@dataclass
class Particle:
    inertia: Inertia
    jspec: JumpSpec
    position: sp.Point


class Field:
    def __init__(self, ge, dist_func=None):
        self.ge = ge
        self.dist_func = self.Sigmoid if not dist_func else dist_func

    def Sigmoid(self, x):
        # A sigmoid curve displaced down and normalized to (0,1)
        return ((1 / (1 + math.exp(-x))) - 0.5) * 2

    def CosHyperbola(self, x):
        # The cosh hyperbola is gentler than x^2 or e^x
        return math.cosh(x) - 1

    def EulerHyperbola(self, x):
        # The most dramatic curve:
        return math.exp(x) - 1

    def _DistanceMetric(self, p1, p2):
        return abs(math.dist(p1, p2))

    def _AbsDistance(self, p):
        # draws a line from GeometryEntity center to the given point, and asks
        # for the intersections (the line is infinitely long, so it will
        # intersect twice for any ellipse if it's not an exact tangent).
        intersections = self.ge.intersection(sp.Line(self.ge.center, p))
        # find the intersection with the minimum distance.
        # note the use of .evalf() to convert the sympy rationals to float:
        return min(self._DistanceMetric(i.evalf(), p) for i in intersections)

    def ResistanceAt(self, point):
        return self.dist_func(self._AbsDistance(point))


def GetJumpPositions(p: Particle, f: Field):
    positions = []
    for i in np.linspace(-1, 1, p.jspec.granularity):
        radians = p.inertia.radians - (p.jspec.arc * i)
        offset = sp.Point(
            [p.jspec.radius * i for i in (math.cos(radians), math.sin(radians))]
        )
        pos = p.position + offset
        positions.append(
            {"position": pos, "resistance": f.ResistanceAt(pos), "radians": radians}
        )
    return positions


def Jump(p: Particle, f: Field):
    positions = GetJumpPositions(p, f)
    nearest = min(positions, key=lambda x: x["resistance"])

    newp = Particle(p.inertia, p.jspec, p.position)
    # update position:
    newp.position = nearest["position"]
    # adjust the inertial radians using the resistance at jump point:
    # TODO: resistance and inertia.magnitude should relate more strictly with
    # one another, along a normed number line:
    resistance_adj = p.inertia.magnitude - nearest["resistance"]
    print(f'{nearest["resistance"] = }')
    print(f"{resistance_adj = }")
    weights = (1, resistance_adj)
    newp.inertia.radians = fmean((p.inertia.radians, nearest["radians"]), weights)
    return newp


if __name__ == "__main__":
    c = sp.Point(0, 0)
    vradius = 2
    hradius = 2
    ge = sp.Ellipse(c, hradius, vradius)
    f = Field(ge)

    m = Inertia(1, math.pi / 2)
    jspec = JumpSpec(1, math.pi / 8, 3)
    initial = sp.Point(5, 7)
    p = Particle(m, jspec, initial)

    print(f"{p = }")
    for _ in range(10):
        p = Jump(p, f)
    print(f"{p.position.evalf() = }")
