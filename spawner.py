from unittest.mock import Mock, MagicMock

import constants
import neuron
from neuron import NeuronState, Activation, GrowthAction, GrowthFactor


def PrintNetwork(n, seen):
    for con in n._connections:
        if con not in seen:
            print(len(con._connections))
            seen.add(con)
            PrintNetwork(con, seen)

def MakeMockNeuron():
    n = neuron.Neuron()
    m = MagicMock(wraps=n)
    m._Maybe = MagicMock(return_value=True)
    m._GrowthDecayGenerator = MagicMock(return_value=0.05)
    m._ChooseGrowthAction = MagicMock(return_value=GrowthAction.SPAWN)
    m._NeuronGenerator = MagicMock(return_value=MakeMockNeuron)
    return m

n = neuron.Neuron()
n._Maybe = MagicMock(return_value=True)
n._GrowthDecayGenerator = MagicMock(return_value=0.05)
n._ChooseGrowthAction = MagicMock(return_value=GrowthAction.SPAWN)
n._NeuronGenerator = MagicMock(return_value=MakeMockNeuron())

gf = GrowthFactor(GrowthAction.SPAWN, 1)

n.Grow(set(), gf)
PrintNetwork(n, set())
