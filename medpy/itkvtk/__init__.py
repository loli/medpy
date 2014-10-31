"""
========================================================================
Functionalities and filters connected with ITK/VTK (:mod:`medpy.itkvtk`)
========================================================================
.. currentmodule:: medpy.itkvtk

The methods in this module require the `WrapITK <https://code.google.com/p/wrapitk/>`_ Python bindings for OTK/VTK.
They largely exist to ease the usage of these bindings, which have their flaws and oddities.

Please access sub-packages directly to avoid dependency clashes for if only ITK or only VTK bindings are available.

Image filter :mod:`medy.itkvtk.filter`
======================================
These methods wrap ITK filter such that they can be applied to images represented as numpy arrays.
Feel free to take a look at the code when you plan to write your own wrappers for ITK image filters.

.. module:: medpy.itkvtk.filter.image
.. autosummary::
    :toctree: generated/
    
    gradient_magnitude
    watershed
    
 
ITK utilities :mod:`medpy.itkvtk.utilities.itku`
================================================

.. module:: medpy.itkvtk.utilities.itku
.. autosummary::
    :toctree: generated/
    
    getInformation
    getInformationWithScalarRange
    saveImageMetaIO
    saveImage
    getImageFromArray
    getArrayFromImage
    getImageType
    getImageTypeFromArray
    getImageTypeFromFile

VTK utilities :mod:`medpy.itkvtk.utilities.vtku`
================================================

.. module:: medpy.itkvtk.utilities.vtku
.. autosummary::
    :toctree: generated/
    
    getInformation
    getImageTypeFromVtk
    saveImageMetaIO
    
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

# import all functions/methods/classes into the module
import filter
import utilities
                        
# import all sub-modules in the __all__ variable
__all__ = [s for s in dir() if not s.startswith('_')]