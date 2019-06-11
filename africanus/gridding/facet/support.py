# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np


def delta_uvw_delta_time(time, antenna1, antenna2, uvw):
    """
    Calculates dUVW / dTIME

    Parameters
    ----------
    time : :class:`numpy.ndarray`
        time in MJD seconds of shape :code:`(row,)`
    antenna1 : :class:`numpy.ndarray`
        antenna1 of shape :code:`(row,)`
    antenna2 : :class:`numpy.ndarray`
        antenna2 of shape :code;`(row,)`
    uvw : :class:`numpy.ndarray`
        uvw coordinates of shape :code:`(row, 3)`

    Returns
    -------
    duvw_dt : :class:`numpy.ndarray`
        change in uvw coordinates with respect to time
        of shape :code:`(row, 3)`.

    Notes
    -----

    1. Probably assumes monotically increasing time
    2. Takes a diff along UVW and TIME, for each baseline.
    3. Last row of the diff is replicated for the last input row.
       Does this have unintended side-effects?
    4. Baselines are grouped together with their mirrors
       for the purposes of this calculation.
    """

    # Copy antenna1 and antenna2, flipping mirror baselines
    # so that they're considered with their canonical brother.
    if not np.all(np.diff(time) >= 0.0):
        raise ValueError("time is not monotically increasing")

    ant1 = antenna1.copy()
    ant2 = antenna2.copy()

    mirror_bl = antenna2 < antenna1
    ant1[mirror_bl] = antenna2[mirror_bl]
    ant2[mirror_bl] = antenna1[mirror_bl]

    baselines = np.stack([antenna1, antenna2], axis=1)
    ubl, inv = np.unique(baselines, return_inverse=True, axis=0)

    # Generate a mask for each row containing the unique baseline
    bl_mask = np.arange(ubl.shape[0])[:, None] == inv[None, :]

    duvw_dt = np.zeros_like(uvw)

    # Handle each baseline
    for mask in bl_mask:
        time_sel = time[mask]
        uvw_sel = uvw[mask]

        uvw_diff = np.diff(uvw_sel, axis=0)
        time_diff = np.diff(time_sel)[:, None]

        # Divide change in uvw by change in time
        res = uvw_diff / time_diff
        # Assign the result, duplicating the last row's value
        duvw_dt[mask] = np.concatenate([res, res[-2:-1, :]])

    return duvw_dt
