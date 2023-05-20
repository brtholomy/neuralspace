import math
import unittest

import sympy as sp

from field_continuous import Field


class TestField(unittest.TestCase):
    def MakeEllipse(self, ge_center=(0, 0), vradius=1, hradius=1):
        c = sp.Point(ge_center)
        return sp.Ellipse(c, hradius, vradius)

    def testAbsDistance(self):
        f = Field(self.MakeEllipse())
        self.assertAlmostEqual(f._AbsDistance((-1, -1)), 0.41, delta=0.01)
        self.assertAlmostEqual(
            f._AbsDistance((math.cos(1), math.sin(1))), 0, delta=0.01
        )
        self.assertAlmostEqual(f._AbsDistance((1, 1)), 0.41, delta=0.01)
        self.assertAlmostEqual(f._AbsDistance((2, 2)), 1.82, delta=0.01)
        self.assertAlmostEqual(f._AbsDistance((3, 3)), 3.24, delta=0.01)

    def testDefaultResistance(self):
        f = Field(self.MakeEllipse())
        # this series should show a sigmoid distribution curve, as we move from
        # the point of intersection away:
        self.assertAlmostEqual(
            f.ResistanceAt((math.cos(1), math.sin(1))), 0, delta=0.0001
        )
        self.assertAlmostEqual(f.ResistanceAt((1, 1)), 0.20, delta=0.01)
        self.assertAlmostEqual(f.ResistanceAt((2, 2)), 0.72, delta=0.01)
        self.assertAlmostEqual(f.ResistanceAt((3, 3)), 0.92, delta=0.01)
        self.assertAlmostEqual(f.ResistanceAt((4, 4)), 0.99, delta=0.01)
        self.assertAlmostEqual(f.ResistanceAt((5, 5)), 0.99, delta=0.01)
        self.assertAlmostEqual(f.ResistanceAt((6, 6)), 0.99, delta=0.01)
        self.assertAlmostEqual(f.ResistanceAt((7, 7)), 0.999, delta=0.001)

        # from the inside to the intersection:
        self.assertAlmostEqual(f.ResistanceAt((0.1, 0.1)), 0.40, delta=0.01)
        self.assertAlmostEqual(f.ResistanceAt((0.2, 0.2)), 0.34, delta=0.01)
        self.assertAlmostEqual(f.ResistanceAt((0.6, 0.6)), 0.07, delta=0.01)
        self.assertAlmostEqual(f.ResistanceAt((0.7, 0.7)), 0.005, delta=0.001)


if __name__ == "__main__":
    unittest.main()
