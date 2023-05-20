import math

import sympy as sp


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
