# Copyright (C) 2013 Oskar Maier
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Oskar Maier
# version r0.1.0
# since 2014-10-15
# status Release

# build-in modules
import warnings
from itertools import combinations

# third-party modules
import numpy
from scipy.sparse.csr import csr_matrix

# own modules

# constants


# code
def mkneighbors_graph(
    observations, n_neighbours, metric, mode="connectivity", metric_params=None
):
    """
    Computes the (weighted) graph of mutual k-Neighbors for observations.

    Notes
    -----
    The distance between an observation and itself is never computed and instead set to
    ``numpy.inf``. I.e. only in the case of k>=n_observations or when the ``metric``
    returns ``numpy.inf``, the returned graph can contain loops.

    Parameters
    ----------
    observations : sequence
        Sequence of observations.
    n_neighbours : int
        Maximum number of neighbours for each sample.
    metric : function
        The distance metric taking two observations and returning a numeric value > 0.
    mode : {'connectivity', 'distance', 'both'}, optional
        Type of returned matrix: 'connectivity' will return the connectivity matrix with
        ones and zeros, in 'distance' the edges are distances between points, while
        'both' returns a (connectivity, distance) tuple.
    metric_params : dict, optional  (default = None)
            Additional keyword arguments for the metric function.

    Returns
    -------
    mkneighbors_graph : ndarray
        Sparse matrix in CSR format, shape = [n_observations, n_observations].
        mkneighbors_graph[i, j] is assigned the weight of edge that connects i to j.
        Might contain ``numpy.inf`` values.

    """
    # compute their pairwise-distances
    pdists = pdist(observations, metric)

    # get the k nearest neighbours for each patch
    k_nearest_nbhs = numpy.argsort(pdists)[:, :n_neighbours]

    # create a mask denoting the k nearest neighbours in image_pdist
    k_nearest_mutual_nbhs_mask = numpy.zeros(pdists.shape, numpy.bool_)
    for _mask_row, _nbhs_row in zip(k_nearest_mutual_nbhs_mask, k_nearest_nbhs):
        _mask_row[_nbhs_row] = True

    # and with transposed to remove non-mutual nearest neighbours
    k_nearest_mutual_nbhs_mask &= k_nearest_mutual_nbhs_mask.T

    # set distance not in the mutual k nearest neighbour set to zero
    pdists[~k_nearest_mutual_nbhs_mask] = 0

    # check for edges with zero-weight
    if numpy.any(pdists[k_nearest_mutual_nbhs_mask] == 0):
        warnings.warn('The graph contains at least one edge with a weight of "0".')

    if "connectivity" == mode:
        return csr_matrix(k_nearest_mutual_nbhs_mask)
    elif "distance" == mode:
        return csr_matrix(pdists)
    else:
        return csr_matrix(k_nearest_mutual_nbhs_mask), csr_matrix(pdists)


def pdist(objects, dmeasure, diagval=numpy.inf):
    """
    Compute the pair-wise distances between arbitrary objects.

    Notes
    -----
    ``dmeasure`` is assumed to be *symmetry* i.e. between object *a* and object *b* the
    function will be called only ones.

    Parameters
    ----------
    objects : sequence
        A sequence of objects of length *n*.
    dmeasure : function
        A callable function that takes two objects as input at returns a number.
    diagval : number
        The diagonal values of the resulting array.

    Returns
    -------
    pdists : ndarray
        An *nxn* symmetric float array containing the pair-wise distances.
    """
    out = numpy.zeros([len(objects)] * 2, float)
    numpy.fill_diagonal(out, diagval)
    for idx1, idx2 in combinations(list(range(len(objects))), 2):
        out[idx1, idx2] = dmeasure(objects[idx1], objects[idx2])
    return out + out.T
