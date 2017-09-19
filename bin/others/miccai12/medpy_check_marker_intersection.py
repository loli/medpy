#!/usr/bin/python

"""
Checks whether the markers of a given marker volume and the original contours intersect.

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
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# build-in modules
import argparse
import logging

# third-party modules
import scipy

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load


# information
__author__ = "Oskar Maier"
__version__ = "d0.1.0, 2012-06-15"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  Checks whether the markers of a given marker volume and the original contours intersect.
                    
                  Takes the marker volume as first and the contour volume as second argument.
                    
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
    
    # constants
    colours = {'i': 10, 'o': 11}
    
    # load volumes
    marker_data, _ = load(args.marker)
    contour_data, _ = load(args.contour)
    
    # perform check
    contour_data = contour_data == colours[args.type]
    marker_data_fg = marker_data == 1
    marker_data_bg = marker_data == 2
    if scipy.logical_and(contour_data, marker_data_fg).any():
        logger.warning('Intersection between {} and {} (type {}) in foreground.'.format(args.marker, args.contour, args.type))
    elif scipy.logical_and(contour_data, marker_data_bg).any():
        logger.warning('Intersection between {} and {} (type {}) in background.'.format(args.marker, args.contour, args.type))
    else:
        print "No intersection."
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('marker', help='Marker volume.')
    parser.add_argument('contour', help='Contour volume.')
    parser.add_argument('type', choices=['i', 'o'], help='The type of the contour (inner or outer).')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main()     