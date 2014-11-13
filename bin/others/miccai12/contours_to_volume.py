#!/usr/bin/python

"""Takes a number of contour text files and converts them into an image volume with markers."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import scipy

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save
from medpy.core.exceptions import ArgumentError


# information
__author__ = "Oskar Maier"
__version__ = "d0.1.0, 2012-06-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  Takes a number of contour text files and converts them into an image volume with markers.
                  The markers are guaranteed to be at least diagonally connected. If two
                  contour points are further apart, the intermediate points are
                  interpolated using linear interpolation.
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
    
    # prepare parameters
    image_directory = False
    contour_directory = False
    for item in os.listdir(args.input):
        if not os.path.isdir('{}/{}'.format(args.input, item)): continue
        if 'dicom' in item:
            image_directory = '{}/{}'.format(args.input, item)
        elif 'contours-manual' in item:
            contour_directory = '{}/{}'.format(args.input, item)
    
    if not (image_directory and contour_directory):
        raise ArgumentError('The supplied source directory {} is invalid.'.format(args.input))

    # count total number of slices via counting the dicom files
    slice_number = len([name for name in os.listdir(image_directory) if os.path.isfile('{}/{}'.format(image_directory, name))])
    
    # extract other dimensionalities from first dicom image
    dicom_files = ['{}/{}'.format(image_directory, name) for name in os.listdir(image_directory) if os.path.isfile('{}/{}'.format(image_directory, name)) and '.dcm' in name]
    example_data, _ = load(dicom_files[0])
    
    # create target image
    result_data = scipy.zeros(tuple([slice_number]) + example_data.shape, dtype=scipy.uint8)
    
    # iterate over contour files
    for contour_file in os.listdir(contour_directory):
        logger.info('Parsing contour file {}...'.format(contour_file))
        
        # determine type of contour by filename
        _, slice_number, contour_type, _ = contour_file.split('-')
        slice_number = int(slice_number)
        contour_type = contour_type[0]
        
        # select "colour"
        colour = colours[contour_type]
        
        last_x = False
        last_y = False
        
        # iterate over file content
        with open('{}/{}'.format(contour_directory, contour_file), 'r') as f:
            for line in f.readlines():
                # clean and test line
                line = line.strip()
                if 0 == len(line) or '#' == line[0]: continue
                # extract contour coordinates and round to full number
                x, y = list(map(int, list(map(round, list(map(float, line.split(' ')))))))
                # paint contours
                result_data[slice_number, x, y] = colour
                # paint additional contours if jump was to large
                if last_x and last_y:
                    for _x, _y in __get_hole_coordinates(last_x, last_y, x, y):
                        result_data[slice_number, _x, _y] = colour
                # set current coordinates as last
                last_x = x
                last_y = y
                
    # save result contour volume
    save(result_data, args.output, False, args.force)

    logger.info("Successfully terminated.")

def __get_hole_coordinates(src_x, src_y, trg_x, trg_y):
    """
    Returns coordinates to fill wholes between two distant pixels completely.
    Uses linear interpolation.
    """
    delta_x = trg_x - src_x
    delta_y = trg_y - src_y
    
    holes = []
    
    if abs(delta_x) > 1 or abs(delta_y) > 1: # means that a hole exists
        steps = max(abs(delta_x), abs(delta_y))
        step_x = float(delta_x)/steps
        step_y = float(delta_y)/steps
        pos_x = src_x
        pos_y = src_y
        
        for _ in range(0, steps):
            pos_x += step_x
            pos_y += step_y
            holes.append((int(round(pos_x)), int(round(pos_y))))
                
    return holes

def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input', help='Source directory (like "patient01", must include contour and dicom folder).')
    parser.add_argument('output', help='Target volume.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser

if __name__ == "__main__":
    main() 