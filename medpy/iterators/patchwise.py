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
from operator import itemgetter

# third-party modules
import numpy
from scipy.ndimage import find_objects

# own modules

# constants


# code
class SlidingWindowIterator:
    r"""
    Moves a sliding window over the array, where the first patch is places centered on
    the top-left voxel and outside-of-image values filled with `cval`. The returned
    patches are views if the array.

    All yielded patches will be of size ``psize``. Areas outside of the array are
    filled with ``cval``. Besides the patch, a patch mask is returned, that denoted
    the outside values.

    Central element for even patches:

        [[0, 0],
         [0, X]]

    Parameters
    ----------
    array : array_like
        A n-dimensional array.
    psize : int or sequence of ints
        The patch size. If a single integer interpreted as hyper-cube.
    cval : number
        Value to fill undefined positions.
    """

    def __init__(self, array, psize, cval=0):
        # process arguments
        self.array = numpy.asarray(array)
        if is_integer(psize):
            self.psize = [psize] * self.array.ndim
        else:
            self.psize = list(psize)
        self.cval = cval

        # validate
        if numpy.any([x <= 0 for x in self.psize]):
            raise ValueError("The patch size must be at least 1 in any dimension.")
        elif len(self.psize) != self.array.ndim:
            raise ValueError(
                "The patch dimensionality must equal the array dimensionality."
            )

        # compute required padding as pairs
        self.padding = [(p / 2, p / 2 - (p - 1) % 2) for p in self.psize]

        # pad array
        self.array = numpy.pad(
            self.array, self.padding, mode="constant", constant_values=self.cval
        )

        # initialize slicers
        slicepoints = [
            list(range(0, s - p + 1)) for s, p in zip(self.array.shape, self.psize)
        ]
        self.__slicepointiter = product(*slicepoints)

    def __iter__(self):
        return self

    def __next__(self):
        """
        Yields the next patch.

        Returns
        -------
        patch : ndarray
            The extracted patch as a view.
        pmask : ndarray
            Boolean array denoting the defined part of the patch.
        slicer : tuple
            Tuple of slicers to apply the same operation to another array (using applyslicer()).
        """
        # trigger internal iterators
        spointset = next(self.__slicepointiter)  # will raise StopIteration when empty
        # compute slicer object
        slicer = []
        padder = []
        for dim, sp in enumerate(spointset):
            slicer.append(slice(sp, sp + self.psize[dim]))
            padder.append(
                (
                    max(0, -1 * (sp - self.padding[dim][0])),
                    max(0, (sp + self.psize[dim]) - (self.array.shape[dim] - 1)),
                )
            )

        # create patch and patch mask
        def_slicer = [slice(x, None if 0 == y else -1 * y) for x, y in padder]
        patch = self.array[tuple(slicer)]
        patch = patch.reshape(self.psize)
        pmask = numpy.zeros(self.psize, numpy.bool_)
        pmask[tuple(def_slicer)] = True

        return patch, pmask, tuple(slicer)

    next = __next__

    def applyslicer(self, array, slicer, cval=None):
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
        slicer : tuple
            Tuple if `slice()` instances as returned by `next()`.
        cval : number
            Value to fill undefined positions. If None, the ``cval`` of the object is used.

        Returns
        -------
        patch: ndarray
            A patch from the input ``array``.
        """
        if cval is None:
            cval = self.cval
        _padding = self.padding + [(0, 0)] * (array.ndim - len(self.padding))
        array = numpy.pad(array, _padding, mode="constant", constant_values=cval)
        _psize = self.psize + list(array.shape[len(self.psize) :])
        return array[tuple(slicer)].reshape(_psize)


class CentredPatchIterator:
    r"""
    Iterated patch-wise over the array, where the central patch is centred on the
    image centre.

    All yielded patches will be of size ``psize``. Areas outside of the array are
    filled with ``cval``. Besides the patch, a patch mask is returned, that denoted
    the outside values. Additionally, the n-dimensional grid id and a slicer object
    are returned.

    To extract the same patch from another array of the same size as ``array``, use
    the `applyslicer` method.

    The following schematic overview explains the behaviour to expect for even and odd
    images respectively patches. All ``O`` denote image voxels, ``|`` the patch
    borders and ``#`` padded voxels.

    One-dimensional image of size 5 with patch sizes 1, 2, 3, 4 and 5::

        |O|O|O|O|O|

        |#O|OO|OO|

        |##O|OOO|O##|

        |OOOO|O###|

        |OOOOO|

    One-dimensional image of size 4 with patch sizes 1, 2, 3 and 4::

        |O|O|O|O|

        |#O|OO|O#|

        |OOO|O##|

        |OOOO|


    Parameters
    ----------
    array : array_like
        A n-dimensional array.
    psize : int or sequence
        The patch size. If a single integer interpreted as hyper-cube.
    cval : number
        Value to fill undefined positions.

    Examples
    --------
    >>> import numpy
    >>> from medpy.iterators import CentredPatchIterator
    >>> arr = numpy.arange(0, 25).reshape((5,5))
    >>> arr
    array([[ 0,  1,  2,  3,  4],
           [ 5,  6,  7,  8,  9],
           [10, 11, 12, 13, 14],
           [15, 16, 17, 18, 19],
           [20, 21, 22, 23, 24]])
    >>> patches, pmasks, gridids, slicers = zip(*CentredPatchIterator(arr, 3))
    Total number of patches:
    >>> len(patches)
    9
    Central patch:
    >>> patches[4]
    array([[ 6,  7,  8],
           [11, 12, 13],
           [16, 17, 18]])
    Bottom-right corner patch:
    >>> patches[-1]
    array([[24,  0,  0],
           [ 0,  0,  0],
           [ 0,  0,  0]])
    And its definition mask:
    >>> pmasks[-1]
    array([[ True, False, False],
           [False, False, False],
           [False, False, False]], dtype=bool)
    One dimensional behaviour examples:
    >>> arr = range(1, 5)
    >>> len(arr)
    4
    >>> patches, pmasks, _, _ = zip(*CentredPatchIterator(arr, 1))
    >>> arr, patches
    ([1, 2, 3, 4], (array([1]), array([2]), array([3]), array([4])))
    >>> patches, _, _, _ = zip(*CentredPatchIterator(arr, 2))
    >>> arr, patches
    ([1, 2, 3, 4], (array([0, 1]), array([2, 3]), array([4, 0])))
    >>> patches, _, _, _ = zip(*CentredPatchIterator(arr, 3))
    >>> arr, patches
    ([1, 2, 3, 4], (array([1, 2, 3]), array([4, 0, 0])))
    >>> patches, _, _, _ = zip(*CentredPatchIterator(arr, 4))
    >>> arr, patches
    ([1, 2, 3, 4], (array([1, 2, 3, 4]),))

    """

    def __init__(self, array, psize, cval=0):
        # process arguments
        self.array = numpy.asarray(array)
        if is_integer(psize):
            self.psize = [psize] * self.array.ndim
        else:
            self.psize = list(psize)
        self.cval = cval

        # validate
        if numpy.any([x <= 0 for x in self.psize]):
            raise ValueError("The patch size must be at least 1 in any dimension.")
        elif len(self.psize) != self.array.ndim:
            raise ValueError(
                "The patch dimensionality must equal the array dimensionality."
            )
        elif numpy.any([x > y for x, y in zip(self.psize, self.array.shape)]):
            raise ValueError(
                "The patch is not allowed to be larger than the array in any dimension."
            )

        # compute required padding
        even_even_correction = [
            (1 - s % 2) * (1 - ps % 2) for s, ps in zip(self.array.shape, self.psize)
        ]
        array_centre = [s / 2 - (1 - s % 2) for s in self.array.shape]
        remainder = [
            (c - ps / 2 + ee, s - c - (ps + 1) / 2 - ee)
            for c, s, ps, ee in zip(
                array_centre, self.array.shape, self.psize, even_even_correction
            )
        ]
        padding = [
            ((ps - l % ps) % ps, (ps - r % ps) % ps)
            for (l, r), ps in zip(remainder, self.psize)
        ]

        # determine slice-points for each dimension and initialize internal slice-point iterator
        slicepoints = [
            list(range(-l, s + r, ps))
            for s, ps, (l, r) in zip(self.array.shape, self.psize, padding)
        ]
        self.__slicepointiter = product(*slicepoints)

        # initialize internal grid-id iterator
        self.__grididiter = product(*[list(range(len(sps))) for sps in slicepoints])

    def __iter__(self):
        return self

    def __next__(self):
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
        slicer : tuple
            A tuple of `slice()` instances definind the patch.
        """
        # trigger internal iterators
        spointset = next(self.__slicepointiter)  # will raise StopIteration when empty
        gridid = next(self.__grididiter)
        # compute slicer object and padder tuples
        slicer = []
        padder = []
        for dim, sp in enumerate(spointset):
            slicer.append(
                slice(max(0, sp), min(sp + self.psize[dim], self.array.shape[dim]))
            )
            padder.append(
                (max(0, -1 * sp), max(0, sp + self.psize[dim] - self.array.shape[dim]))
            )
        # create patch and patch mask
        patch = numpy.pad(
            self.array[tuple(slicer)],
            padder,
            mode="constant",
            constant_values=self.cval,
        )
        pmask = numpy.pad(
            numpy.ones(self.array[tuple(slicer)].shape, dtype=numpy.bool_),
            padder,
            mode="constant",
            constant_values=0,
        )

        return patch, pmask, gridid, tuple(slicer)

    next = __next__

    @staticmethod
    def applyslicer(array, slicer, pmask, cval=0):
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
        slicer : tuple
            Tuple if `slice()` instances as returned by `next()`.
        pmask : narray
            The array mask as returned by `next()`.
        cval : number
            Value to fill undefined positions.

        Experiments
        -----------
        >>> import numpy
        >>> from medpy.iterators import CentredPatchIterator
        >>> arr = numpy.arange(0, 25).reshape((5,5))
        >>> for patch, pmask, _, slicer in CentredPatchIterator(arr, 3):
        >>>     new_patch = CentredPatchIterator.applyslicer(arr, slicer, pmask)
        >>>     print numpy.all(new_patch == patch)
        True
        ...

        """
        l = len(slicer)
        patch = numpy.zeros(list(pmask.shape[:l]) + list(array.shape[l:]), array.dtype)
        if not 0 == cval:
            patch.fill(cval)
        sliced = array[tuple(slicer)]
        patch[pmask] = sliced.reshape(
            [numpy.prod(sliced.shape[:l])] + list(sliced.shape[l:])
        )
        return patch

    @staticmethod
    def assembleimage(patches, pmasks, gridids):
        r"""
        Assemble an image from a number of patches, patch masks and their grid ids.

        Parameters
        ----------
        patches : sequence
            Sequence of patches.
        pmasks : sequence
            Sequence of associated patch masks.
        gridids
            Sequence of associated grid ids.

        Returns
        -------
        image : ndarray
            The patches assembled back into an image of the original proportions.

        Examples
        --------
        Two-dimensional example:
        >>> import numpy
        >>> from medpy.iterators import CentredPatchIterator
        >>> arr = numpy.arange(0, 25).reshape((5,5))
        >>> arr
        array([[ 0,  1,  2,  3,  4],
               [ 5,  6,  7,  8,  9],
               [10, 11, 12, 13, 14],
               [15, 16, 17, 18, 19],
               [20, 21, 22, 23, 24]])
        >>> patches, pmasks, gridids, _ = zip(*CentredPatchIterator(arr, 2))
        >>> result = CentredPatchIterator.assembleimage(patches, pmasks, gridids)
        >>> numpy.all(arr == result)
        True

        Five-dimensional example:
        >>> arr = numpy.random.randint(0, 10, range(5, 10))
        >>> patches, pmasks, gridids, _ = zip(*CentredPatchIterator(arr, range(2, 7)))
        >>> result = CentredPatchIterator.assembleimage(patches, pmasks, gridids)
        >>> numpy.all(arr == result)
        True
        """
        for d in range(patches[0].ndim):
            groups = {}
            for patch, pmask, gridid in zip(patches, pmasks, gridids):
                groupid = gridid[1:]
                if not groupid in groups:
                    groups[groupid] = []
                groups[groupid].append((patch, pmask, gridid[0]))
            patches = []
            gridids = []
            pmasks = []
            for groupid, group in list(groups.items()):
                patches.append(
                    numpy.concatenate(
                        [p for p, _, _ in sorted(group, key=itemgetter(2))], d
                    )
                )
                pmasks.append(
                    numpy.concatenate(
                        [m for _, m, _ in sorted(group, key=itemgetter(2))], d
                    )
                )
                gridids.append(groupid)
        objs = find_objects(pmasks[0])
        if not 1 == len(objs):
            raise ValueError(
                "The assembled patch masks contain more than one binary object."
            )
        return patches[0][objs[0]]


class CentredPatchIteratorOverlapping:
    r"""
    Iterated patch-wise over the array, where the central patch is centred on the
    image centre.

    All yielded patches will be of size ``psize``. Areas outside of the array are
    filled with ``cval``. Besides the patch, a patch mask is returned, that denoted
    the outside values. Additionally, the n-dimensional grid id and a slicer object
    are returned.

    To extract the same patch from another array of the same size as ``array``, use
    the `applyslicer` method.

    The following schematic overview explains the behaviour to expect for even and odd
    images respectively patches. All ``O`` denote image voxels, ``|`` the patch
    borders and ``#`` padded voxels.

    One-dimensional image of size 5 with patch sizes 1, 2, 3, 4 and 5::

        |O|O|O|O|O|

        |#O|OO|OO|

        |##O|OOO|O##|

        |OOOO|O###|

        |OOOOO|

    One-dimensional image of size 4 with patch sizes 1, 2, 3 and 4::

        |O|O|O|O|

        |#O|OO|O#|

        |OOO|O##|

        |OOOO|


    Parameters
    ----------
    array : array_like
        A n-dimensional array.
    psize : int or sequence of ints
        The patch size. If a single integer interpreted as hyper-cube.
    offset : None, int or sequence of ints
        The patch offset. If None interpreted as non-overlapping patches. If a single integer interpreted as hyper-cube.
    cval : number
        Value to fill undefined positions.

    Examples
    --------
    >>> import numpy
    >>> from medpy.iterators import CentredPatchIterator
    >>> arr = numpy.arange(0, 25).reshape((5,5))
    >>> arr
    array([[ 0,  1,  2,  3,  4],
           [ 5,  6,  7,  8,  9],
           [10, 11, 12, 13, 14],
           [15, 16, 17, 18, 19],
           [20, 21, 22, 23, 24]])
    >>> patches, pmasks, gridids, slicers = zip(*CentredPatchIterator(arr, 3))
    Total number of patches:
    >>> len(patches)
    9
    Central patch:
    >>> patches[4]
    array([[ 6,  7,  8],
           [11, 12, 13],
           [16, 17, 18]])
    Bottom-right corner patch:
    >>> patches[-1]
    array([[24,  0,  0],
           [ 0,  0,  0],
           [ 0,  0,  0]])
    And its definition mask:
    >>> pmasks[-1]
    array([[ True, False, False],
           [False, False, False],
           [False, False, False]], dtype=bool)
    One dimensional behaviour examples:
    >>> arr = range(1, 5)
    >>> len(arr)
    4
    >>> patches, pmasks, _, _ = zip(*CentredPatchIterator(arr, 1))
    >>> arr, patches
    ([1, 2, 3, 4], (array([1]), array([2]), array([3]), array([4])))
    >>> patches, _, _, _ = zip(*CentredPatchIterator(arr, 2))
    >>> arr, patches
    ([1, 2, 3, 4], (array([0, 1]), array([2, 3]), array([4, 0])))
    >>> patches, _, _, _ = zip(*CentredPatchIterator(arr, 3))
    >>> arr, patches
    ([1, 2, 3, 4], (array([1, 2, 3]), array([4, 0, 0])))
    >>> patches, _, _, _ = zip(*CentredPatchIterator(arr, 4))
    >>> arr, patches
    ([1, 2, 3, 4], (array([1, 2, 3, 4]),))

    """

    def __init__(self, array, psize, offset=None, cval=0):
        # process arguments
        self.array = numpy.asarray(array)
        if is_integer(psize):
            self.psize = [psize] * self.array.ndim
        else:
            self.psize = list(psize)
        if None == offset:
            offset = psize
        elif is_integer(psize):
            offset = [offset] * self.array.ndim
        else:
            offset = list(offset)
        self.cval = cval

        # validate
        if numpy.any([x <= 0 for x in self.psize]):
            raise ValueError("The patch size must be at least 1 in any dimension.")
        elif len(self.psize) != self.array.ndim:
            raise ValueError(
                "The patch dimensionality must equal the array dimensionality."
            )
        elif numpy.any([x > y for x, y in zip(self.psize, self.array.shape)]):
            raise ValueError(
                "The patch is not allowed to be larger than the array in any dimension."
            )

        # compute required padding
        even_even_correction = [
            (1 - s % 2) * (1 - ps % 2) for s, ps in zip(self.array.shape, self.psize)
        ]
        array_centre = [s / 2 - (1 - s % 2) for s in self.array.shape]
        remainder = [
            (c - ps / 2 + ee, s - c - (ps + 1) / 2 - ee)
            for c, s, ps, ee in zip(
                array_centre, self.array.shape, self.psize, even_even_correction
            )
        ]
        padding = [
            ((ps - l % ps) % ps, (ps - r % ps) % ps)
            for (l, r), ps in zip(remainder, self.psize)
        ]

        # determine slice-points for each dimension and initialize internal slice-point iterator
        slicepoints = [
            list(range(-l, s + r, os))
            for s, os, (l, r) in zip(self.array.shape, offset, padding)
        ]
        self.__slicepointiter = product(*slicepoints)

        # initialize internal grid-id iterator
        self.__grididiter = product(*[list(range(len(sps))) for sps in slicepoints])

    def __iter__(self):
        return self

    def __next__(self):
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
        slicer : tuple
            A tuple of `slice()` instances definind the patch.
        """
        # trigger internal iterators
        spointset = next(self.__slicepointiter)  # will raise StopIteration when empty
        gridid = next(self.__grididiter)
        # compute slicer object and padder tuples
        slicer = []
        padder = []
        for dim, sp in enumerate(spointset):
            slicer.append(
                slice(max(0, sp), min(sp + self.psize[dim], self.array.shape[dim]))
            )
            padder.append(
                (max(0, -1 * sp), max(0, sp + self.psize[dim] - self.array.shape[dim]))
            )
        # create patch and patch mask
        patch = numpy.pad(
            self.array[tuple(slicer)],
            padder,
            mode="constant",
            constant_values=self.cval,
        )
        pmask = numpy.pad(
            numpy.ones(self.array[tuple(slicer)].shape, dtype=numpy.bool_),
            padder,
            mode="constant",
            constant_values=0,
        )

        return patch, pmask, gridid, tuple(slicer)

    next = __next__

    @staticmethod
    def applyslicer(array, slicer, pmask, cval=0):
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
        slicer : tuple
            Tuple if `slice()` instances as returned by `next()`.
        pmask : narray
            The array mask as returned by `next()`.
        cval : number
            Value to fill undefined positions.

        Experiments
        -----------
        >>> import numpy
        >>> from medpy.iterators import CentredPatchIterator
        >>> arr = numpy.arange(0, 25).reshape((5,5))
        >>> for patch, pmask, _, slicer in CentredPatchIterator(arr, 3):
        >>>     new_patch = CentredPatchIterator.applyslicer(arr, slicer, pmask)
        >>>     print numpy.all(new_patch == patch)
        True
        ...

        """
        l = len(slicer)
        patch = numpy.zeros(list(pmask.shape[:l]) + list(array.shape[l:]), array.dtype)
        if not 0 == cval:
            patch.fill(cval)
        sliced = array[tuple(slicer)]
        patch[pmask] = sliced.reshape(
            [numpy.prod(sliced.shape[:l])] + list(sliced.shape[l:])
        )
        return patch

    @staticmethod
    def assembleimage(patches, pmasks, gridids):
        r"""
        Assemble an image from a number of patches, patch masks and their grid ids.

        Note
        ----
        Currently only applicable for non-overlapping patches.

        Parameters
        ----------
        patches : sequence
            Sequence of patches.
        pmasks : sequence
            Sequence of associated patch masks.
        gridids
            Sequence of associated grid ids.

        Returns
        -------
        image : ndarray
            The patches assembled back into an image of the original proportions.

        Examples
        --------
        Two-dimensional example:
        >>> import numpy
        >>> from medpy.iterators import CentredPatchIterator
        >>> arr = numpy.arange(0, 25).reshape((5,5))
        >>> arr
        array([[ 0,  1,  2,  3,  4],
               [ 5,  6,  7,  8,  9],
               [10, 11, 12, 13, 14],
               [15, 16, 17, 18, 19],
               [20, 21, 22, 23, 24]])
        >>> patches, pmasks, gridids, _ = zip(*CentredPatchIterator(arr, 2))
        >>> result = CentredPatchIterator.assembleimage(patches, pmasks, gridids)
        >>> numpy.all(arr == result)
        True

        Five-dimensional example:
        >>> arr = numpy.random.randint(0, 10, range(5, 10))
        >>> patches, pmasks, gridids, _ = zip(*CentredPatchIterator(arr, range(2, 7)))
        >>> result = CentredPatchIterator.assembleimage(patches, pmasks, gridids)
        >>> numpy.all(arr == result)
        True
        """
        for d in range(patches[0].ndim):
            groups = {}
            for patch, pmask, gridid in zip(patches, pmasks, gridids):
                groupid = gridid[1:]
                if not groupid in groups:
                    groups[groupid] = []
                groups[groupid].append((patch, pmask, gridid[0]))
            patches = []
            gridids = []
            pmasks = []
            for groupid, group in list(groups.items()):
                patches.append(
                    numpy.concatenate(
                        [p for p, _, _ in sorted(group, key=itemgetter(2))], d
                    )
                )
                pmasks.append(
                    numpy.concatenate(
                        [m for _, m, _ in sorted(group, key=itemgetter(2))], d
                    )
                )
                gridids.append(groupid)
        objs = find_objects(pmasks[0])
        if not 1 == len(objs):
            raise ValueError(
                "The assembled patch masks contain more than one binary object."
            )
        return patches[0][objs[0]]


def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False
