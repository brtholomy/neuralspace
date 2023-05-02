from functools import reduce
import numpy as np
import matplotlib.pyplot as plt

# import scipy
from scipy.stats import semicircular

field = zip(
    np.random.normal(0, 1, 100),
    np.random.normal(0, 1, 100),
)


def PlotShow(plot=None):
    # special magic for avoiding a blocking call
    if plot:
        plt.show(plot, block=False)
    else:
        plt.show(block=False)
    # Pause to allow the input call to run:
    plt.pause(0.001)
    input("hit [enter] to end.")
    plt.close("all")


plt.scatter(
    np.random.normal(0, 0.1, size=500),
    np.random.normal(0, 1, size=500),
)


# fig, ax = plt.subplots(1, 1)
# # mean, var, skew, kurt = semicircular.stats(moments='mvsk')

# # Display the probability density function (pdf):
# x = np.linspace(semicircular.ppf(0.01),
#                 semicircular.ppf(0.99), 100)
# ax.plot(x, semicircular.pdf(x),
#        'r-', lw=5, alpha=0.6, label='semicircular pdf')

from scipy.integrate import odeint
from scipy.misc import derivative


def system(vect, t):
    x, y = vect
    return [x - y - x * (x**2 + 5 * y**2), x + y - y * (x**2 + y**2)]


vect0 = [(-2 + 4 * np.random.random(), -2 + 4 * np.random.random()) for i in range(5)]
t = np.linspace(0, 100, 1000)

color = ["red", "green", "blue", "yellow", "magenta"]

plot = plt.figure()

for i, v in enumerate(vect0):
    sol = odeint(system, v, t)
    plt.quiver(
        sol[:-1, 0],
        sol[:-1, 1],
        sol[1:, 0] - sol[:-1, 0],
        sol[1:, 1] - sol[:-1, 1],
        scale_units="xy",
        angles="xy",
        scale=1,
        color=color[i],
    )

PlotShow()
