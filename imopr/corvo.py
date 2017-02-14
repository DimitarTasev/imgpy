from __future__ import (absolute_import, division, print_function)
from imopr.sinogram import make_sinogram
import numpy as np


def execute(sample, flat, dark, config, indices):
    from imopr import helper
    helper.print_start(
        "Running IMOPR with action COR using tomopy find_center_vo")

    from recon.tools import tool_importer
    tool = tool_importer.do_importing(config.func.tool)

    inc = float(config.func.max_angle) / sample.shape[0]
    proj_angles = np.arange(0, sample.shape[0] * inc, inc)
    proj_angles = np.radians(proj_angles)

    from imopr.sinogram import make_sinogram
    sample = make_sinogram(sample)

    i1, i2 = helper.handle_indices(indices)

    initial_guess = config.func.cor if config.func.cor is not None else None

    for i in range(i1, i2):
        cor = tool.find_center_vo(
            tomo=sample, ind=None, smin=-40, smax=40, srad=10, step=1, ratio=2.0, drop=20)
        print(cor)

    # stop python from exiting
    import matplotlib.pyplot as plt
    plt.show()

    return sample