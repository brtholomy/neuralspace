from test_neuron import MockNeuron
from neuron import Neuron, NeuronState, Activation, GrowthAction, GrowthFactor


def PrintNetwork(n, seen):
    for con in n._connections:
        if con not in seen:
            print(len(con._connections))
            seen.add(con)
            PrintNetwork(con, seen)


n = MockNeuron()
gf = GrowthFactor(GrowthAction.SPAWN, 1)
n.Grow(set(), gf)
PrintNetwork(n, set())
