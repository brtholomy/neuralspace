from collections import namedtuple
from dataclasses import dataclass
import itertools as it
from math import floor

import numpy as np
import matplotlib.pyplot as plt

import constants as c


@dataclass
class Inertia:
    scalar: float

    # could be coordinate delta pair, or rotational offset in radians or degrees.
    # a single value would be easiest to store.
    # but a coordinate pair might be easiest to calculate.

    # In any case I have to divide the direction between at least 2 grid
    # coordinates proportionally, in order to update the scalar and direction.
    # rather than unit circle displacement, could it be "grid circle" displacement?
    # but a simple calculation from degrees/radians -> coordinate offset should suffice.
    direction: int


Position = namedtuple('Position', ['x', 'y'])


@dataclass
class Particle:
    inertia: Inertia
    position: Position


DEGREES_TO_OFFSET = {
    0: (1, 0),
    45: (1, 1),
    90: (0, 1),
    135: (-1, 1),
    180: (-1, 0),
    225: (-1, -1),
    270: (0, -1),
    315: (1, -1),
}

class Field:
    """Represented as a dictionary keyed by tuple to resistance value."""

    def __init__(self, size, init):
        self._grid = {coord: init for coord in it.product(range(size), range(size))}

    def GetResistanceAt(self, pos):
        return self._grid[pos]


def DivideDirection(intertia):
    """Divides a continuous degree value among 8 possible coordinate offsets."""

    lower_deg = floor(intertia.direction / c.FOURTYFIVE) * c.FOURTYFIVE
    upper_deg = lower_deg + c.FOURTYFIVE

    rem = intertia.direction % c.FOURTYFIVE
    factor = rem / c.FOURTYFIVE

    lower_ratio = 1 - factor
    upper_ratio = factor

    return (lower_deg, lower_ratio), (upper_deg, upper_ratio)


def GetOffsetPosition(pos, offset):
    return tuple(sum(stack) for stack in zip(pos, offset))


def GetNewPosition(field, particle):
    """Calculate new position of particle in field.

    The challenge here is to allow continuous float degree values while mapping
    position and resistance to a discreet 2 dimensional grid. We want to
    preserve proprotional distribution between the two possible resistances, so
    that although the particle has continuous intertial values, its position is
    influenced by a discreet field. This allows the particle to proceed along
    curves roughly represented by the grid, but not constrained by it.

    Note however, that the field strength calculation *is* constrained by the
    grid, since the field is represented as points which decay stepwise, not
    continually. This choice is made in order to keep the field strength
    calculations as a fast hash lookup, else we'd have to recalculate the field
    at every step.

    """

    (l_deg, l_ratio), (u_deg, u_ratio) = DivideDirection(particle.inertia)
    l_pos = GetOffsetPosition(particle.position, DEGREES_TO_OFFSET[l_deg])
    u_pos = GetOffsetPosition(particle.position, DEGREES_TO_OFFSET[u_deg])

    l_res = field.GetResistanceAt(l_pos)
    u_res = field.GetResistanceAt(u_pos)
    # we diminish the resistance by its ratio of the diagonal through the two
    # points.
    l_res_r = l_res - (l_res * l_ratio)
    u_res_r = u_res - (u_res * u_ratio)

    # swerving away from the point of resistance
    if l_res_r < u_res_r:
        new_pos = l_pos
        deg_Δ = l_res_r * c.FOURTYFIVE
    else:
        new_pos = u_pos
        deg_Δ = u_res_r * c.FOURTYFIVE * -1

    return new_pos, deg_Δ


def GetNewInertia(p, deg_Δ):
    p.inertia.direction += deg_Δ
    # TODO: calculate a new scalar value as well.
    return p.inertia


def UpdateParticle(f, p):
    p.position, deg_Δ = GetNewPosition(f, p)
    p.inertia = GetNewInertia(p, deg_Δ)
    return p
