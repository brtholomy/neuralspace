import constants as c

class Bias(object):
    def __init__(
        self,
        input_bias: float = c.DEFAULT_INPUT_BIAS,
        output_bias: float = c.DEFAULT_OUTPUT_BIAS,
        bidirectional_bias: float = c.DEFAULT_BIDIRECTIONAL_BIAS,
    ):
        self.input_bias = input_bias
        self.output_bias = output_bias
        self.bidirectional_bias = bidirectional_bias
