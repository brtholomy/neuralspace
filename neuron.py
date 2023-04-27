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


class Neuron(object):
    def __init__(
        self,
        state: NeuronState = NeuronState.BUILDING,
        voltage: float = c.DEFAULT_VOLTAGE,
        decay: float = c.DEFAULT_DECAY,
        lower_threshold: float = c.DEFAULT_LOWER_THRESHOLD,
        upper_threshold: float = c.DEFAULT_UPPER_THRESHOLD,
        bias: Bias = Bias(),
    ):
        self._state = state
        self._voltage = voltage
        self._decay = decay
        self._lower_threshold = lower_threshold
        self._upper_threshold = upper_threshold
        self._bias = bias

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

    def AcceptVoltage(self, incoming: float):
        """
        Accepts incoming voltage, potentially changes state, and runs _FireOrDecay.

        Returns an Activation indicating which action was taken.
        """

        self._voltage = self._VoltageNormalizer(self._voltage + incoming)

        if self._voltage > self._upper_threshold:
            self._state = NeuronState.READY

        return self._FireOrDecay()
