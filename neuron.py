from dataclasses import dataclass
from enum import Enum, auto
import random

import constants as c
from bias import Bias


class NeuronState(Enum):
    ACTIVE = 1
    BUILDING = auto()
    EXHAUSTED = auto()


@dataclass
class Activation:
    state: NeuronState
    voltage: float


class GrowthAction(Enum):
    SPAWN = auto()
    CLUSTER = auto()
    BRANCH = auto()


@dataclass
class GrowthFactor:
    action: GrowthAction
    p: float


class Neuron:
    def __init__(
        self,
        state: NeuronState = NeuronState.BUILDING,
        voltage: float = c.DEFAULT_VOLTAGE,
        decay: float = c.DEFAULT_DECAY,
        lower_threshold: float = c.DEFAULT_LOWER_THRESHOLD,
        upper_threshold: float = c.DEFAULT_UPPER_THRESHOLD,
        bias: Bias = Bias(),
        connections=set(),
    ):
        self._state = state
        self._voltage = voltage
        self._decay = decay
        self._lower_threshold = lower_threshold
        self._upper_threshold = upper_threshold
        self._bias = bias
        self._connections = connections

    def __repr__(self):
        return "<{name} {attrs}>".format(
            name=self.__class__.__name__,
            attrs=",".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    def _IsActive(self):
        return self._state is NeuronState.ACTIVE

    def _IsBuilding(self):
        return self._state is NeuronState.BUILDING

    def _VoltageNormalizer(self, v):
        # ensure [0,1] condition
        return max(0, min(v, 1))

    def _VoltageTrigger(self):
        return self._voltage > self._upper_threshold

    def _CanFire(self):
        return self._IsBuilding() and not self._IsActive() and self._VoltageTrigger()

    def _Fire(self):
        self._state = NeuronState.ACTIVE
        self._voltage = self._VoltageNormalizer(1)

    def _Decay(self):
        """
        Decays voltage by decay rate, and resets state if necessary.
        """

        self._voltage = self._VoltageNormalizer(self._voltage - self._decay)

        if self._IsActive() and self._voltage < self._upper_threshold:
            self._state = NeuronState.EXHAUSTED

        if self._voltage < self._lower_threshold:
            self._state = NeuronState.BUILDING

    def _FireOrDecay(self):
        """
        Returns an Activation indicating which action was taken.
        """
        if self._CanFire():
            self._Fire()
        else:
            self._Decay()
        return Activation(self._state, self._voltage)

    def _AcceptVoltage(self, incoming: float):
        """
        Accepts incoming voltage, potentially changes state, and runs _FireOrDecay.

        Returns an Activation indicating which action was taken.
        """

        self._voltage = self._VoltageNormalizer(self._voltage + incoming)

        if self._voltage > self._upper_threshold:
            self._state = NeuronState.READY

        return self._FireOrDecay()

    def Propagate(self, incoming: float):
        """
        Accepts incoming voltage, potentially changes state, and recurses among its connections.
        """
        activation = self._AcceptVoltage(incoming)
        if activation.state is NeuronState.ACTIVE:
            for con in self._connections:
                yield con.Propagate(activation.voltage)

    def _GrowthDecayGenerator(self):
        # FIXME: use proper ln() distribution
        return random.random()

    def _ChooseGrowthAction(self):
        return random.choice([*GrowthAction])

    def _CompareValueGenerator(self):
        return random.random()

    def _Maybe(self, gf):
        return gf.p > self._CompareValueGenerator()

    def _DecayGrowthFactor(self, gf: GrowthFactor):
        # FIXME: use proper ln() distribution
        gf.action = self._ChooseGrowthAction()
        gf.p = max(gf.p - self._GrowthDecayGenerator(), 0)
        return gf

    def _AddConnection(self, other):
        self._connections.add(other)

    def _NeuronGenerator(self):
        return Neuron()

    def Grow(self, others: set, gf: GrowthFactor):
        others.add(self)
        gf = self._DecayGrowthFactor(gf)

        if gf.action is GrowthAction.SPAWN:
            if self._Maybe(gf):
                new = self._NeuronGenerator()
                self._AddConnection(new)
                new.Grow(others, gf)

        elif gf.action is GrowthAction.CLUSTER:
            others_static = others.copy()
            for o in others_static:
                if o is not self and self._Maybe(gf):
                    self._AddConnection(o)
                    o.Grow(others, gf)

        elif gf.action is GrowthAction.BRANCH:
            if self._Maybe(gf):
                new = self._NeuronGenerator()
                self._AddConnection(new)
                others = set([self])
                new.Grow(others, gf)
