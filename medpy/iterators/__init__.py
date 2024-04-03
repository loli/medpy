"""
========================================
Image iterators (:mod:`medpy.iterators`)
========================================
.. currentmodule:: medpy.iterators

This package contains iterators for images.

Patch-wise :mod:`medpy.iterators.patchwise`
===========================================
Iterators to extract patches from images.

.. module:: medpy.iterators.patchwise
.. autosummary::
    :toctree: generated/

    SlidingWindowIterator
    CentredPatchIterator
    CentredPatchIteratorOverlapping


"""

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

from .patchwise import CentredPatchIterator as CentredPatchIterator
from .patchwise import (
    CentredPatchIteratorOverlapping as CentredPatchIteratorOverlapping,
)
from .patchwise import SlidingWindowIterator as SlidingWindowIterator

__all__ = [
    "CentredPatchIterator",
    "CentredPatchIteratorOverlapping",
    "SlidingWindowIterator",
]
