from dataclasses import dataclass
import math
from statistics import fmean

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

from field_continuous import Field
from vector_fields import PlotShow

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


def LeastResistantJump(p: Particle, f: Field):
    positions = []
    # sweep left to right with a specific granularity
    for i in np.linspace(-1, 1, p.jspec.granularity):
        radians = p.inertia.radians - (p.jspec.arc * i)
        offset = sp.Point(
            # get the offset coord by multiplying the radius * unit circle value:
            [p.jspec.radius * i for i in (math.cos(radians), math.sin(radians))]
        )
        # sp.Point allows this convenient expression:
        pos = p.position + offset
        positions.append(
            {"position": pos, "resistance": f.ResistanceAt(pos), "radians": radians}
        )
    return min(positions, key=lambda x: x["resistance"])


def UpdateRadians(rad):
    return rad % (math.pi * 2)


def Jump(p: Particle, f: Field):
    least = LeastResistantJump(p, f)
    newp = Particle(p.inertia, p.jspec, p.position)

    # update position:
    newp.position = least["position"]

    # adjust the inertial radians using the resistance at jump point:
    # TODO: resistance and inertia.magnitude should relate more strictly with
    # one another, along a normed number line:
    weights = (1, 1+least["resistance"])
    newp.inertia.radians = UpdateRadians(fmean((p.inertia.radians, least["radians"]), weights))
    return newp


def PlotPositions(positions):
    X = positions[:, [0]]
    Y = positions[:, [1]]
    I = range(len(positions))

    plt.scatter(X, Y, c=I)
    plt.colorbar(label="number of jumps")
    plt.axis("equal")
    PlotShow()


if __name__ == "__main__":
    c = sp.Point(0, 0)
    vradius = 2
    hradius = 4
    ge = sp.Ellipse(c, hradius, vradius)
    f = Field(ge)

    m = Inertia(1, math.pi / 2)
    jspec = JumpSpec(0.25, math.pi / 4, 5)
    initial = sp.Point(4, 0)
    p = Particle(m, jspec, initial)

    jumps = 100
    positions = []
    for i in range(jumps):
        p = Jump(p, f)
        # print(f"{p.inertia.radians = }")
        # print(f"{p.position.evalf() = }")
        positions.append(tuple(p.position.evalf()))

    positions = np.array(positions)
    PlotPositions(positions)
