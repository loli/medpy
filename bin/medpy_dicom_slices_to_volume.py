#!/usr/bin/python

"""
Converts a collection of DICOM slices into a proper image volume.

Copyright (C) 2013 Oskar Maier

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""

# build-in modules
import argparse
import logging

# third-party modules
from dicom.contrib import pydicom_series

# path changes

# own modules
from medpy.core import Logger
from medpy.io import save


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.1, 2012-06-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Converts a collection of DICOM slices (a DICOM series) into a proper
                  image volume. Note that this operation does not preserve the voxel
                  spacing (or any other header information, come to that).
                  
                  Copyright (C) 2013 Oskar Maier
                  This program comes with ABSOLUTELY NO WARRANTY; This is free software,
                  and you are welcome to redistribute it under certain conditions; see
                  the LICENSE file or <http://www.gnu.org/licenses/> for details.   
                  """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # load input slices
    [series] = pydicom_series.read_files(args.input, False, True) # second to not show progress bar, third to retrieve data
    data_input = series.get_pixel_array()
    
    if args.spacing:
        print '{} {}'.format(*series.info.PixelSpacing)
        return 0
    
    logger.debug('Resulting shape is {}.'.format(data_input.shape))

    # save resulting volume
    save(data_input, args.output, False, args.force)
    
    logger.info("Successfully terminated.")    
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('input', help='Source folder.')
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('-s', dest='spacing', action='store_true', help='Just print spacing and exit.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser    

if __name__ == "__main__":
    main()        