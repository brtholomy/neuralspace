from collections import namedtuple
from dataclasses import dataclass
import itertools as it
from math import floor

import numpy as np
import matplotlib.pyplot as plt


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


DEGREES_TO_COORD = {
    0: (1, 0),
    45: (1, 1),
    90: (0, 1),
    135: (-1, 1),
    180: (-1, 0),
    225: (-1, -1),
    270: (0, -1),
    315: (1, -1),
}


def DivideDirection(intertia):
    """Divides a continuous degree value among 8 possible coordinate offsets."""

    lower_deg = floor(intertia.direction / 45) * 45
    upper_deg = lower_deg + 45

    rem = intertia.direction % 45
    factor = rem / 45

    upper_ratio = factor
    lower_ratio = 1 - factor

    return (upper_deg, upper_ratio), (lower_deg, lower_ratio)


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

    (a_deg, a_ratio), (b_deg, b_ratio) = DivideDirection(particle.inertia)
    a_offset = DEGREES_TO_COORD[a_deg]
    b_offset = DEGREES_TO_COORD[b_deg]
    a_pos = GetOffsetPosition(particle.position, a_offset)
    b_pos = GetOffsetPosition(particle.position, b_offset)

    a_res = field.GetResistanceAt(a_pos)
    b_res = field.GetResistanceAt(b_pos)
    a_res_r = a_res - (a_res * a_ratio)
    b_res_r = b_res - (b_res * b_ratio)

    return a_pos if a_res_r < b_res_r else b_pos


class Field:
    """Represented as a dictionary keyed by tuple to resistance value."""

    def __init__(self, size, init):
        self._grid = {coord: init for coord in it.product(range(size), range(size))}

    def GetResistanceAt(self, pos):
        return self._grid[pos]



if __name__ == "__main__":
    f = Field(10, 0.1)
    i = Inertia(2, 90)
    p = Particle(i, (5, 5))

    p.position = GetNewPosition(f, p)
    print(f'{p.position = }')
    p.position = GetNewPosition(f, p)
    print(f'{p.position = }')
    p.position = GetNewPosition(f, p)
    print(f'{p.position = }')

    p.inertia.direction = 180
    p.position = GetNewPosition(f, p)
    print(f'{p.position = }')
