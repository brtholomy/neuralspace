import math

import sympy as sp
from sympy.geometry.entity import GeometryEntity


class Field:
    def __init__(self, ge: GeometryEntity, dist_func=None):
        dist_func = self.Sigmoid if not dist_func else dist_func
        self._shapes = [(ge, dist_func)]

    def AddShape(self, ge: GeometryEntity, dist_func=None):
        dist_func = self.Sigmoid if not dist_func else dist_func
        self._shapes.append((ge, dist_func))

    def Sigmoid(self, x):
        # A sigmoid curve displaced down and normalized to (0,1).
        # Note we ensure the incoming value is >= 0
        x = abs(x)
        return ((1 / (1 + math.exp(-x))) - 0.5) * 2

    def CosHyperbola(self, x):
        # The cosh hyperbola is gentler than x^2 or e^x
        return min(1, math.cosh(x) - 1)

    def EulerHyperbola(self, x):
        # The most dramatic curve, maxing out at 1:
        return min(1, math.exp(x) - 1)

    def _DistanceMetric(self, p1, p2):
        return abs(math.dist(p1, p2))

    def _AbsDistance(self, ge, p):
        # draws a line from GeometryEntity center to the given point, and asks
        # for the intersections (the line is infinitely long, so it will
        # intersect twice for any ellipse if it's not an exact tangent).
        intersections = ge.intersection(sp.Line(ge.center, p))

        # find the intersection with the minimum distance.
        # NOTE: the use of .evalf() to convert the sympy rationals to float,
        # which is what slows everything down. Unfortunately there doesn't seem
        # to be a way to prevent the list of Point() returned by intersection()
        # from creating rational internal representations.
        return min(self._DistanceMetric(i.evalf(), p) for i in intersections)

    def ResistanceAt(self, point):
        res = 0
        for ge, dfunc in self._shapes:
            res += dfunc(self._AbsDistance(ge, point))
        return res
