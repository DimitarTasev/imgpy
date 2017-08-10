from __future__ import absolute_import, division, print_function

import numpy as np


def execute(data_length, slice_ids, cors_for_slices):
    """
    Interpolates the Centers of Rotation for the slices that are not provided.

    :param data_length: The length of the data along the axis we're traversing. E.g. the number of images

    :param slice_ids: The slice IDs for which we are passing the corresponding CORs

    :param cors_for_slices: The CORs for the slices

    :returns: A np.array with length equal to data_length containing the interpolated CORs.
    """
    assert cors_for_slices and all(
        isinstance(cor, float) for cor in cors_for_slices), "The centers of rotation MUST be floats"

    assert slice_ids and all(isinstance(slice, int) for slice in
                             slice_ids), "The slices associated with the centers of rotation MUST be ints"

    return np.interp(list(range(data_length)), slice_ids, cors_for_slices)