import random
from enum import Flag, IntFlag, IntEnum, auto

import constants as c
from bias import Bias


class NeuronState(IntFlag):
    ACTIVE = 1
    READY = auto()
    BUILDING = auto()
    DECAYING = auto()

VALID_NEURON_STATES = [
    # It just fired:
    NeuronState.ACTIVE | NeuronState.DECAYING,
    # It's below the upper_threshold and still falling:
    NeuronState.DECAYING,
    # It fell below the lower_threshold and now accepts input:
    NeuronState.BUILDING | NeuronState.DECAYING,
    # It's above the upper_threshold but hasn't fired:
    NeuronState.READY | NeuronState.BUILDING | NeuronState.DECAYING,
]


class Neuron(object):
    def __init__(
        self,
        state: NeuronState = NeuronState.BUILDING | NeuronState.DECAYING,
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

    def ValidateState(self):
        if not self._state in VALID_NEURON_STATES:
            raise ValueError("Neuron is in an unsupported state:", self._state)

    def IsActive(self):
        return NeuronState.ACTIVE in self._state

    def IsReady(self):
        return NeuronState.READY in self._state

    def IsBuilding(self):
        return NeuronState.BUILDING in self._state

    def VoltageNormalizer(self, v):
        # ensure [0,1] condition
        return max(0, min(v, 1))

    def VoltageTrigger(self):
        return self._voltage > self._upper_threshold

    def CanFire(self):
        return self.IsReady() and not IsActive() and self.VoltageTrigger()

    def Fire(self):
        self._state = self.ACTIVE | self.DECAYING
        self._voltage = VoltageNormalizer(1)

    def FireBuildOrDecay(self):
        """
        Returns an enum indicating which action was taken.
        """

        self.ValidateState()

        if self.IsBuilding():
            if self.CanFire():
                self.Fire()
                # should I just return the current _state?
                return NeuronState.ACTIVE

            # gather afference : do this outside this interface
            else:
                # We decay even while building
                self.Decay()
                return NeuronState.BUILDING

        # this will catch state == ACTIVE also
        else:
            self.Decay()
            return NeuronState.DECAYING

    def Decay(self):
        self.ValidateState()

        self._voltage = self.VoltageNormalizer(self._voltage - self._decay)

        if self._voltage < self._upper_threshold:
            # be sure to clear the flag, not just toggle it:
            self._state = self._state & ~NeuronState.ACTIVE

        if self._voltage < self._lower_threshold:
            self._state = self._state | NeuronState.BUILDING

    def IncrementVoltage(self, incoming):
        self.ValidateState()

        self._voltage = self.VoltageNormalizer(self._voltage + incoming)

        if self._voltage > self._upper_threshold:
            self._state = self._state | NeuronState.READY
