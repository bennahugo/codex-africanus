# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import pytest

from africanus.constants import c
from africanus.filters.kaiser_bessel_filter import kaiser_bessel_with_sinc
from africanus.gridding.simple.gridding import _ARCSEC2RAD


@pytest.mark.parametrize("exact_u", [np.array([1.9])])
@pytest.mark.parametrize("full_support, oversampling, beta", [[7, 7, 2.4]])
@pytest.mark.parametrize("ref_wave", [c / (0.5*(.856e9 + 2*.856e9))])
@pytest.mark.parametrize("nx", [16])
@pytest.mark.parametrize("cell_size", [2.0])
@pytest.mark.parametrize("plot", [False])
def test_oversampling(exact_u, full_support,
                      oversampling, beta,
                      ref_wave, nx,
                      cell_size, plot):
    W = full_support*oversampling
    half_support = full_support // 2
    half_x = nx // 2

    exact_u += half_x
    disc_u = np.round(exact_u).astype(np.int32)

    if np.any(disc_u <= 0) or np.any(disc_u > nx):
        raise ValueError("Pick values inside the grid [%s-%s]\n%s"
                         % (0, nx, disc_u))

    conv_filter = kaiser_bessel_with_sinc(full_support,
                                          oversampling,
                                          beta=beta)

    # The following illustrates a filter with a support of 4
    # and oversampling by a factor of 4. + indicates filter index
    # whereas | indicates oversampling index
    #
    #   0            1             2             3
    #   0   1 2 3    0    1 2 3    0    1 2 3    0    1 2 3
    #   +   | | |    +    | | |    +    | | |    +    | | |

    # We snap to the oversampling index base on the fractional
    # value of the u and v coordinate
    # if disc_u > exact_u:
    #     base_frac_u = exact_u - disc_u + 1.0
    # else:
    #     base_frac_u = exact_u - disc_u

    base_frac_u = exact_u - np.floor(exact_u)

    # Calculate oversampling index and normalise it
    base_os_u = np.round(base_frac_u*oversampling).astype(np.int32)
    base_os_u %= oversampling

    print(exact_u, disc_u, base_frac_u, base_os_u)

    if plot:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            pass
        else:
            x = np.arange(0, nx)
            f, axes = plt.subplots(2, 1)
            f.set_figwidth(80)
            f.set_figheight(60)
            axes[0].scatter(exact_u, np.ones_like(exact_u)*0.25, color='blue')
            axes[0].scatter(disc_u, np.ones_like(exact_u)*0.1, color='red')
            axes[0].set_xticks(x)
            axes[0].set_ylim(0, 0.5)
            axes[0].set_xlabel("grid position")

            x = np.linspace(0, full_support, conv_filter.size)
            vl = np.linspace(0, full_support, conv_filter.size // oversampling)
            # pts = (vl + disc_u - exact_u)[:-1]
            # axes[1, 0].scatter(pts, np.ones_like(pts)*0)

            pts = (base_frac_u + vl[:-1])
            axes[1].plot(x, conv_filter)
            axes[1].vlines(vl, ymin=conv_filter.min(),
                           ymax=0.1 * conv_filter.max())
            axes[1].scatter(pts, np.ones_like(pts)*0, color='blue')
            axes[1].set_xlabel("filter position")

            pts = (base_os_u/oversampling + vl)[:-1]
            axes[1].scatter(pts, np.ones_like(pts)*0, color='red')

            plt.show()
