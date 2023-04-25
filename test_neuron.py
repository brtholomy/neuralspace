import unittest

import neuron


class TestNeuron(unittest.TestCase):
    def setUp(self):
        pass

    def testEmpty(self):
        n = neuron.Neuron()
        self.assertTrue(n.IsBuilding())

        try:
            n.ValidateState()
        except ValueError:
            self.fail('this should never happen')

    def testVoltageNormalizer(self):
        n = neuron.Neuron()
        self.assertEqual(n.VoltageNormalizer(1), 1)
        self.assertEqual(n.VoltageNormalizer(1.5), 1)
        self.assertEqual(n.VoltageNormalizer(0.5), 0.5)
        self.assertEqual(n.VoltageNormalizer(-0.5), 0)


if __name__ == "__main__":
    unittest.main()
