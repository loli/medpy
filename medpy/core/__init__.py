"""
=====================================================================
Core functionalities and shared exception objects (:mod:`medpy.core`)
=====================================================================
.. currentmodule:: medpy.core

This package collect the packages core functionalities, such as an
event Logger and shared exception classes. If you do not intend to
develop MedPy, you usually won't have to touch this.

Logger :mod:`medy.core.logger`
==============================

.. module:: medpy.core.logger
.. autosummary::
    :toctree: generated/

    Logger


Exceptions :mod:`medpy.core.exceptions`
=======================================

.. module:: medpy.core.exceptions
.. autosummary::
    :toctree: generated/

    ArgumentError
    FunctionError
    SubprocessError
    ImageLoadingError
    DependencyError
    ImageSavingError
    ImageTypeError
    MetaDataError

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

from .exceptions import ArgumentError as ArgumentError
from .exceptions import DependencyError as DependencyError
from .exceptions import FunctionError as FunctionError
from .exceptions import ImageLoadingError as ImageLoadingError
from .exceptions import ImageSavingError as ImageSavingError
from .exceptions import ImageTypeError as ImageTypeError
from .exceptions import MetaDataError as MetaDataError
from .exceptions import SubprocessError as SubprocessError
from .logger import Logger as Logger

__all__ = [
    "Logger",
    "ArgumentError",
    "FunctionError",
    "SubprocessError",
    "ImageLoadingError",
    "DependencyError",
    "ImageSavingError",
    "ImageTypeError",
    "MetaDataError",
]
