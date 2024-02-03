"""
===========================================
Image I/O functionalities (:mod:`medpy.io`)
===========================================
.. currentmodule:: medpy.io

This package provides functionalities for loading and saving images,
as well as the handling of image metadata.

Loading an image
================

.. module:: medpy.io.load
.. autosummary::
    :toctree: generated/

    load

Saving an image
===============

.. module:: medpy.io.save
.. autosummary::
    :toctree: generated/

    save

Reading / writing metadata (:mod:`medpy.io.header`)
===================================================

.. module:: medpy.io.header
.. autosummary::
    :toctree: generated/

    Header

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


from .header import Header as Header
from .header import copy_meta_data as copy_meta_data
from .header import get_offset as get_offset
from .header import get_pixel_spacing as get_pixel_spacing
from .header import get_voxel_spacing as get_voxel_spacing
from .header import set_offset as set_offset
from .header import set_pixel_spacing as set_pixel_spacing
from .header import set_voxel_spacing as set_voxel_spacing
from .load import load as load
from .save import save as save

__all__ = [
    "load",
    "save",
    "Header",
    "get_voxel_spacing",
    "get_pixel_spacing",
    "get_offset",
    "set_voxel_spacing",
    "set_pixel_spacing",
    "set_offset",
    "copy_meta_data",
]
