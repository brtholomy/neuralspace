import random
import unittest
from unittest.mock import MagicMock, patch

import constants
from neuron import Neuron, NeuronState, Activation, GrowthAction, GrowthFactor



class MockNeuron(Neuron):
    def _CompareValueGenerator(self):
        return 0.5

    def _GrowthDecayGenerator(self):
        return 0.01

    def _ChooseGrowthAction(self):
        return GrowthAction.SPAWN

    def _NeuronGenerator(self):
        return MockNeuron()


class TestNeuronCore(unittest.TestCase):
    def testEmpty(self):
        n = Neuron()
        self.assertTrue(n._IsBuilding())

    def testVoltageNormalizer(self):
        n = Neuron()
        self.assertEqual(n._VoltageNormalizer(1), 1)
        self.assertEqual(n._VoltageNormalizer(1.5), 1)
        self.assertEqual(n._VoltageNormalizer(0.5), 0.5)
        self.assertEqual(n._VoltageNormalizer(-0.5), 0)

    def testFires(self):
        n = Neuron()
        # cheat by reaching into internals:
        n._state = NeuronState.BUILDING
        starting_voltage = constants.DEFAULT_UPPER_THRESHOLD + 0.01
        active_voltage = 1
        n._voltage = starting_voltage

        # first fire:
        self.assertEqual(n._FireOrDecay(), Activation(NeuronState.ACTIVE, active_voltage))
        # should still be active:
        self.assertEqual(n._state, NeuronState.ACTIVE)

    def testDecaysWhileBuilding(self):
        n = Neuron()
        n._state = NeuronState.BUILDING
        starting_voltage = constants.DEFAULT_LOWER_THRESHOLD + 0.01
        ending_voltage = starting_voltage - constants.DEFAULT_DECAY
        n._voltage = starting_voltage

        # the return value should reflect a decay:
        self.assertEqual(n._FireOrDecay(), Activation(NeuronState.BUILDING, ending_voltage))
        # it should have decayed and be reflected in internal state:
        self.assertEqual(n._voltage, starting_voltage - constants.DEFAULT_DECAY)
        # it should be still building:
        self.assertEqual(n._state, NeuronState.BUILDING)

    def testDecaysWhileActive(self):
        n = Neuron()
        n._state = NeuronState.ACTIVE
        starting_voltage = (
            constants.DEFAULT_UPPER_THRESHOLD + constants.DEFAULT_DECAY + 0.01
        )
        n._voltage = starting_voltage
        ending_voltage = starting_voltage - constants.DEFAULT_DECAY

        self.assertEqual(n._FireOrDecay(), Activation(NeuronState.ACTIVE, ending_voltage))

        # it will decay again, and change state:
        ending_voltage -= constants.DEFAULT_DECAY
        self.assertEqual(n._FireOrDecay(), Activation(NeuronState.EXHAUSTED, ending_voltage))

    def testDecaysWhileExhausted(self):
        n = Neuron()
        n._state = NeuronState.EXHAUSTED

        starting_voltage = constants.DEFAULT_LOWER_THRESHOLD - 0.01
        n._voltage = starting_voltage
        ending_voltage = starting_voltage - constants.DEFAULT_DECAY

        # adds BUILDING state:
        self.assertEqual(n._FireOrDecay(), Activation(NeuronState.BUILDING, ending_voltage))

class TestNeuronGrowBasic(unittest.TestCase):
    def testSingle(self):
        n = Neuron()
        n._Maybe = MagicMock(return_value=True)

        gf = GrowthFactor(GrowthAction.SPAWN, 1)
        n.Grow(set(), gf)
        self.assertTrue(len(n._connections) > 0)

    def testFullMock(self):
        n = MockNeuron()
        gf = GrowthFactor(GrowthAction.SPAWN, 1)
        n.Grow(set(), gf)
        self.assertEqual(len(n._connections), 49)

class TestNeuronGrowPatched(unittest.TestCase):
    @patch.object(MockNeuron, '_CompareValueGenerator')
    def testCompareValueGenerator(self, mock_method):
        mock_method.return_value = 0.1
        n = MockNeuron()
        gf = GrowthFactor(GrowthAction.SPAWN, 1)
        n.Grow(set(), gf)
        # float values aren't going to be exact:
        self.assertTrue(len(n._connections) > 130)

        n = MockNeuron()
        mock_method.return_value = 0.01
        n.Grow(set(), gf)
        self.assertTrue(len(n._connections) > 140)

    @patch.object(MockNeuron, '_GrowthDecayGenerator')
    def testGrowthDecay(self, mock_method):
        mock_method.return_value = 0.001
        n = MockNeuron()
        gf = GrowthFactor(GrowthAction.SPAWN, 1)
        n.Grow(set(), gf)
        self.assertTrue(len(n._connections) > 600)

    @patch.object(MockNeuron, '_ChooseGrowthAction')
    def testChooseGrowthAction(self, mock_method):
        mock_method.return_value = random.choice([GrowthAction.SPAWN, GrowthAction.CLUSTER])
        n = MockNeuron()
        gf = GrowthFactor(GrowthAction.SPAWN, 1)
        n.Grow(set(), gf)
        self.assertTrue(len(n._connections) > 30)



if __name__ == "__main__":
    unittest.main()
