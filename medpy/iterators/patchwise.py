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
# since 2014-10-13
# status Release

# build-in modules
from itertools import product

# third-party modules
import numpy
import math

# own modules

# constants

# code
class CentredPatchIterator():
    r"""
    Iterated patch-wise over the array, where the central patch is centred on the
    image centre.
    """
    
    def __init__(self, array, psize, cval = 0):
        r"""
        Iterated patch-wise over the array, where the central patch is centred on the
        image centre.
        
        All yielded patches will be of size ``psize``. Areas outside of the array are
        filled with ``cval``. Besides the patch, a patch mask is returned, that denoted
        the outside values. Additionally, the n-dimensional grid id and a slicer object
        are returned.
        
        To extract the same patch from another array of the same size as ``array``, use
        the `applyslicer` method.
        
        Parameters
        ----------
        array : array_like
            A n-dimensional array.
        psize : int or sequence
            The patch size. If a single integer interpreted as hyper-cube.
        cval : number
            Value to fill undefined positions.
        """
        # process arguments
        self.array = numpy.asarray(array)
        if is_integer(psize):
            self.psize = [psize] * self.array.ndim
        else:
            self.psize = list(psize)
        self.cval = cval
        
        # determine array centre, central patch centre and the offset between them
        central_patch_idx = map(int, [math.ceil((s / 2. + ps / 2.) / ps) for s, ps in zip(self.array.shape, psize)])
        central_patch_centre = [cpi * ps - int(math.ceil(ps/2.)) for cpi, ps in zip(central_patch_idx, psize)]
        array_centre = [s/2 for s in self.array.shape]
        self.offset = [ic - cpc for ic, cpc in zip(array_centre, central_patch_centre)]
        
        # determine slice-points for each dimension and initialize internal slice-point iterator
        slicepoints = [range(self.offset[d], self.array.shape[d] - self.offset[d], psize[d]) for d in range(self.array.ndim)]
        self.__slicepointiter = product(*slicepoints)
        
        # initialize internal grid-id iterator
        self.__grididiter = product(*[range(len(sps)) for sps in slicepoints])
        
    def __iter__(self):
        return self
    
    def next(self):
        """
        Yields the next patch.
        
        Returns
        -------
        patch : ndarray
            The extracted patch as a view.
        pmask : ndarray
            Boolean array denoting the defined part of the patch.
        gridid : sequence
            N-dimensional grid id.
        slicer : list
            A list of `slice()` instances definind the patch.
        """ 
        # trigger internal iterators
        spointset = self.__slicepointiter.next() # will raise StopIteration when empty
        gridid = self.__grididiter.next()
        # compute slicer object and padder tuples
        slicer = []
        padder = []
        for dim, sp in enumerate(spointset):
            slicer.append( slice(max(0, sp),
                                 min(sp + self.psize[dim], self.array.shape[dim])) )
            padder.append( (max(0, -1 * sp), max(0, sp + self.psize[dim] - self.array.shape[dim])) )
        # create patch and patch mask
        patch = numpy.pad(self.array[slicer], padder, mode='constant', constant_values=self.cval)
        pmask = numpy.pad(numpy.ones(self.array[slicer].shape, dtype=numpy.bool), padder, mode='constant', constant_values=0)
        
        return patch, pmask, gridid, slicer
        
    @staticmethod
    def applyslicer(array, slicer, pmask):
        r"""
        Apply a slicer returned by the iterator to a new array of the same
        dimensionality as the one used to initialize the iterator.
        
        Notes
        -----
        If ``array`` has more dimensions than ``slicer`` and ``pmask``, the first ones
        are sliced.
        
        Parameters
        ----------
        array : array_like
            A n-dimensional array.
        slicer : list
            List if `slice()` instances as returned by `next()`.
        pmask : narray
            The array mask as returned by `next()`.
        """
        l = len(slicer)
        patch = numpy.zeros(list(pmask.shape[:l]) + list(array.shape[l:]), array.dtype)
        sliced = array[slicer]
        patch[pmask] = sliced.reshape([numpy.prod(sliced.shape[:l])] + list(sliced.shape[l:]))
        return patch
        
        
def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False
