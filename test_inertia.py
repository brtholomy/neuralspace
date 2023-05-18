import unittest
from inertia import *


class TestPosition(unittest.TestCase):
    def testStraight(self):
        f = Field(10, 0.1)
        i = Inertia(1, 90)
        p = Particle(i, (1, 1))

        p = UpdateParticle(f, p)
        self.assertEqual(p.position, (1, 2))
        p = UpdateParticle(f, p)
        self.assertEqual(p.position, (1, 3))
        p = UpdateParticle(f, p)
        self.assertEqual(p.position, (1, 4))

    def testDiagonal(self):
        f = Field(10, 0.1)
        i = Inertia(1, 45)
        p = Particle(i, (1, 1))

        p = UpdateParticle(f, p)
        self.assertEqual(p.position, (2, 2))
        p = UpdateParticle(f, p)
        self.assertEqual(p.position, (3, 3))
        p = UpdateParticle(f, p)
        self.assertEqual(p.position, (4, 4))

    def testShallowAngle(self):
        f = Field(10, 0.1)
        angle = 20
        i = Inertia(1, angle)
        p = Particle(i, (0, 0))

        p = UpdateParticle(f, p)
        self.assertEqual(p.position, (1, 0))
        p = UpdateParticle(f, p)
        self.assertEqual(p.position, (2, 0))
        p = UpdateParticle(f, p)
        # eventually the diagonal shows:
        self.assertEqual(p.position, (3, 1))

    def testSteepAngle(self):
        f = Field(10, 0.1)
        angle = 70
        i = Inertia(1, angle)
        p = Particle(i, (0, 0))

        p = UpdateParticle(f, p)
        self.assertEqual(p.position, (0, 1))
        p = UpdateParticle(f, p)
        self.assertEqual(p.position, (0, 2))
        p = UpdateParticle(f, p)
        # eventually the diagonal shows:
        self.assertEqual(p.position, (1, 3))


if __name__ == "__main__":
    unittest.main()
