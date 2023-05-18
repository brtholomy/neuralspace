import numpy as np
import sympy as sp

import math


def DistanceMetric(p1, p2):
    return math.dist(p1, p2)


def DistanceFromCircleCircumference(p, c, r):
    return DistanceMetric(p, c) - r


def SolveSymbolicPoint(p):
    # FIXME: this is a hack. Note the (0) arg does nothing, because the symbolic
    # formula sympy gives us has no variable. The only reason I'm using sympy is
    # for the ease of generating the correct formulae for arbitrary geometrical
    # shapes. Converting to numerical solutions like this would argue for numpy,
    # but then again this works.
    point = tuple(sp.lambdify("x", f)(0) for f in p)
    return point


def DistanceFromCircumference(p, e):
    # draws a line from GeometryEntity center to the given point, and asks for
    # the intersections (the line is infinitely long).
    intersections = e.intersection(sp.Line(e.center, p))
    inters_solved = [SolveSymbolicPoint(i) for i in intersections]
    return min(DistanceMetric(i, p) for i in inters_solved)


if __name__ == "__main__":
    c = sp.Point(0, 0)
    vradius = 5
    hradius = 2
    e = sp.Ellipse(c, hradius, vradius)
    p = sp.Point(5, 5)
    d = DistanceFromCircumference(p, e)
    print(f"{d = }")
