import unittest

import constants
import neuron
from neuron import NeuronState


class TestNeuron(unittest.TestCase):
    def testEmpty(self):
        n = neuron.Neuron()
        self.assertTrue(n.IsBuilding())

        try:
            n.ValidateState()
        except ValueError:
            self.fail("this should never happen")

    def testValidateState(self):
        n = neuron.Neuron()
        n._state = NeuronState.READY
        with self.assertRaises(ValueError):
            n.ValidateState()

    def testVoltageNormalizer(self):
        n = neuron.Neuron()
        self.assertEqual(n.VoltageNormalizer(1), 1)
        self.assertEqual(n.VoltageNormalizer(1.5), 1)
        self.assertEqual(n.VoltageNormalizer(0.5), 0.5)
        self.assertEqual(n.VoltageNormalizer(-0.5), 0)

    def testFires(self):
        n = neuron.Neuron()
        # cheat by reaching into internals:
        n._state = NeuronState.READY | NeuronState.BUILDING | NeuronState.DECAYING
        n._voltage = constants.DEFAULT_UPPER_THRESHOLD + 0.01

        # first fire:
        self.assertEqual(n.FireBuildOrDecay(), NeuronState.ACTIVE)
        self.assertEqual(n._state, NeuronState.ACTIVE | NeuronState.DECAYING)

        # set voltage below upper_threshold:
        n._voltage = constants.DEFAULT_UPPER_THRESHOLD - 0.01
        # shouldn't fire:
        self.assertEqual(n.FireBuildOrDecay(), NeuronState.DECAYING)
        self.assertEqual(n._state, NeuronState.DECAYING)

    def testDecaysWhileBuilding(self):
        n = neuron.Neuron()
        n._state = NeuronState.BUILDING | NeuronState.DECAYING
        starting_voltage = constants.DEFAULT_LOWER_THRESHOLD + 0.01
        n._voltage = starting_voltage
        self.assertEqual(n.FireBuildOrDecay(), NeuronState.BUILDING)
        self.assertEqual(n._voltage, starting_voltage - constants.DEFAULT_DECAY)
        self.assertEqual(n._state, NeuronState.BUILDING | NeuronState.DECAYING)

    def testDecaysWhileActive(self):
        n = neuron.Neuron()
        n._state = NeuronState.ACTIVE | NeuronState.DECAYING
        starting_voltage = (
            constants.DEFAULT_UPPER_THRESHOLD + constants.DEFAULT_DECAY + 0.01
        )
        n._voltage = starting_voltage
        self.assertEqual(n.FireBuildOrDecay(), NeuronState.DECAYING)
        self.assertEqual(n._voltage, starting_voltage - constants.DEFAULT_DECAY)
        self.assertEqual(n._state, NeuronState.ACTIVE | NeuronState.DECAYING)

    def testDecaysWhileDecaying(self):
        n = neuron.Neuron()
        n._state = NeuronState.DECAYING
        n._voltage = constants.DEFAULT_LOWER_THRESHOLD - 0.01
        self.assertEqual(n.FireBuildOrDecay(), NeuronState.DECAYING)
        # adds BUILDING state:
        self.assertEqual(n._state, NeuronState.BUILDING | NeuronState.DECAYING)


if __name__ == "__main__":
    unittest.main()
