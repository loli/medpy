#!/usr/bin/python

"""Creates visualization of a testbed."""

# build-in modules
import argparse
import logging
import pickle
import sys
import os

# third-party modules
import scipy
from scipy.ndimage.measurements import find_objects
from nibabel.loadsave import load, save

# own modules
import medpy.filter
from medpy.core import Logger
from medpy.utilities.nibabel import image_like

# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2012-02-24"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Script for visual testbench inspection.
                  Takes a testbench and creates a image from it by setting all foreground
                  resp. background regions of the evaluation region set to 1 resp. 2.
                  Furthermore all regions used for foreground resp. background model
                  creation are set to 3 resp. 4.
                  """

# code
def main():
    # parse cmd arguments
    parser = getParser()
    parser.parse_args()
    args = getArguments(parser)
    
    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # check if output file exists
    if not args.force:
        if os.path.exists(args.image):
            logger.warning('The output file {} already exists. Exiting.'.format(args.image))
            sys.exit(0)
    
    logger.info('Unpickle testbench and loading label image...')
    label, label_img, bounding_boxes, model_fg_ids, model_bg_ids, truth_fg, truth_bg = __load(args.testbench, args.label)
    
    logger.info('Composing image image...')
    image = scipy.zeros(label.shape, dtype=scipy.int8)
    # set foreground ids
    for rid in truth_fg:
        image[bounding_boxes[rid - 1]][label[bounding_boxes[rid - 1]] == rid] = 1
    # set background ids
    for rid in truth_bg:
        image[bounding_boxes[rid - 1]][label[bounding_boxes[rid - 1]] == rid] = 2
    # set foreground model ids
    for rid in model_fg_ids:
        image[bounding_boxes[rid - 1]][label[bounding_boxes[rid - 1]] == rid] = 3
    # set background model ids
    for rid in model_bg_ids:
        image[bounding_boxes[rid - 1]][label[bounding_boxes[rid - 1]] == rid] = 4
    
    logger.info('Saving image as {} with data-type int8...'.format(args.image))
    image_img = image_like(image, label_img)
    image_img.get_header().set_data_dtype(scipy.int8)
    save(image_img, args.image)
    
    logger.info('Successfully terminated.')
   
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    args.image = '{}.nii'.format(args.image)
    return args
   
def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('label', help='The label image.')
    parser.add_argument('testbench', help='The testbench to create the image from.')
    parser.add_argument('image', help='The name of the image to save (\wo suffix).')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser

def  __load(picklefile, label):
    """
    Load a pickled testbed as well as the original and label image for further processing.
    The label image will be relabeled to start with region id 1.
    @param picklefile the testbed pickle file name
    @param label the label image file name
    @return a tuple containing:
        label: the label image data as ndarray
        bounding_boxes: the bounding boxes around the label image regions (Note that the the bounding box of a region with id rid is accessed using bounding_boxes[rid - 1])
        model_fg_ids: the region ids of all regions to create the foreground model from
        model_bg_ids: the region ids of all regions to create the background model from
        eval_ids: the regions to evaluate the regions term on, represented by their ids
        truth_fg: subset of regions from the eval_ids that are foreground according to the ground-truth
        truth_bg:  subset of regions from the eval_ids that are background according to the ground-truth
    """
    # load and preprocess images
    label_image = load(label)
    
    label_image_d = scipy.squeeze(label_image.get_data())
    
    # relabel the label image to start from 1
    label_image_d = medpy.filter.relabel(label_image_d, 1)
    
    # extracting bounding boxes
    bounding_boxes = find_objects(label_image_d)
    
    # load testbed
    with open(picklefile, 'r') as f:
        model_fg_ids = pickle.load(f)
        model_bg_ids = pickle.load(f)
        pickle.load(f) # eval ids
        truth_fg = pickle.load(f)
        truth_bg = pickle.load(f)
            
    return label_image_d, label_image, bounding_boxes, model_fg_ids, model_bg_ids, truth_fg, truth_bg
    
if __name__ == "__main__":
    main()           