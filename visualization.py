import math

import matplotlib.animation as manimation
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from tqdm import tqdm


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


def PlotPositions(positions):
    X = positions[:, [0]]
    Y = positions[:, [1]]
    I = range(len(positions))

    plt.scatter(X, Y, c=I)
    plt.colorbar(label="number of jumps")
    plt.axis("equal")
    PlotShow()


def PlotField(f: object, xymax: tuple, granularity: int):
    xmax, ymax = xymax
    coords = []
    for x in np.linspace(-xmax, xmax, granularity):
        for y in np.linspace(-ymax, ymax, granularity):
            res = f.ResistanceAt((x, y))
            coords.append((x, y, res))
    coords = np.array(coords)

    X = coords[:, [0]]
    Y = coords[:, [1]]
    Z = coords[:, [2]]

    plt.scatter(X, Y, c=Z)
    plt.colorbar(label="firing path resistance")
    plt.axis("equal")
    PlotShow()


def Record(positions, frames_per_sec=1):
    FFMpegWriter = manimation.writers["ffmpeg"]
    writer = FFMpegWriter(fps=frames_per_sec)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim([-5, 5])
    ax.set_ylim([-5, 5])
    ax.grid(True)
    cnorm = colors.Normalize(vmin=0, vmax=math.pi * 2)

    with writer.saving(fig, "neural_statespace.mp4", dpi=100):
        for pos in tqdm(positions):
            plt.scatter(pos[0], pos[1], c=pos[2], norm=cnorm)
            writer.grab_frame()

    plt.close("all")
