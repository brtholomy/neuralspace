from dataclasses import dataclass
import math
from statistics import fmean

import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
from tqdm import tqdm

from field_continuous import Field
import visualization as viz

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

        # FIXME: this arg is an attempt to speed up. sympy can be horribly
        # slow, because of the conversion from real to rational numbers.
        # https://github.com/sympy/sympy/issues/6716#issuecomment-37007389
        # however, if we instantiate the Point here as a float, it will just get
        # converted to a rational during the intersection() call later, which
        # seems to make it even worse.
        # evaluate=False
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
    weights = (1, 1 + least["resistance"])
    newp.inertia.radians = UpdateRadians(
        fmean((p.inertia.radians, least["radians"]), weights)
    )
    return newp


if __name__ == "__main__":
    center = sp.Point(0, 0)
    vradius = 2
    hradius = 4
    firing = sp.Ellipse(center, hradius, vradius)

    center = sp.Point(-4, 0)
    vradius = 0.2
    hradius = 0.2
    resting = sp.Ellipse(center, hradius, vradius)

    f = Field(firing)
    f.AddShape(resting, f.EulerHyperbola)

    m = Inertia(magnitude=1, radians=math.pi / 2)
    jspec = JumpSpec(radius=0.25, arc=math.pi / 4, granularity=5)
    initial = sp.Point(4, 0)
    p = Particle(m, jspec, initial)

    jumps = 100
    positions = []
    for i in tqdm(range(jumps)):
        p = Jump(p, f)
        positions.append(tuple(p.position.evalf()) + (p.inertia.radians,))

    # Prefer to append to a vanilla list and cast, because numpy arrays do much
    # better with a single invocation:
    positions = np.asarray(positions, dtype=np.float64)

    # viz.PlotPositions(positions)
    # viz.PlotField(f, (5, 5), 100)
    viz.Record(positions, frames_per_sec=10)
