#!/usr/bin/python

# build-in modules
import os
import sys
import logging
import math
import argparse
import pickle

# third-party modules
from nibabel.loadsave import load
from scipy.ndimage.measurements import find_objects
import scipy.ndimage

# path changes

# own modules
from medpy.core import Logger
import medpy.filter

# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2012-02-24"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Test mean, entropy and uniformity extract from a Laplacian of Gaussian
                  (LoG) processed image as a possible region term texture feature.
                  The result is a number of gnuplot data files to be plotted as
                  candlesticks. 
                  """

# constants
__FEATURE_MAP = {0: 'mean', 1: 'entropy', 2: 'uniformity'}

# code
def main(): 
    # parse cmd arguments
    parser = getParser()
    args = getArguments(parser)
    
    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)

    logger.info('Loading testbench and preparing images...')
    original, label, bounding_boxes, model_fg_ids, eval_ids, truth_fg, truth_bg = __load(args.testbench, args.original, args.label)
            
    logger.debug('Of the {} eval regions, {} are fg and {} bg.'.format(len(eval_ids), len(truth_fg), len(truth_bg))) 
    
    for coarseness in args.coarseness:
        logger.info('Filtering image with coarseness (sigma) of {}...'.format(coarseness))
        liver_img_filtered = scipy.zeros(original.shape, dtype=scipy.float32)
        scipy.ndimage.filters.gaussian_laplace(original, coarseness, liver_img_filtered)
        
        logger.info('Extract foreground (liver) features...')
        features_liver = __create_liver_model(model_fg_ids, bounding_boxes, label, original)
        
        logger.info('Collect features extracted from the foreground regions...')
        features_fg = [[] for _ in range(3)] # three features
        for rid in truth_fg:
            features_region = __create_region_model(rid, bounding_boxes, label, original)
            for fid in range(len(features_region)):
                features_fg[fid].append(features_region[fid])
                
        logger.info('Collect features extracted from the background regions...')
        features_bg = [[] for _ in range(len(features_liver))]
        for rid in truth_bg:
            features_region = __create_region_model(rid, bounding_boxes, label, original)
            for fid in range(len(features_region)):
                features_bg[fid].append(features_region[fid])

        logger.info('Write results to files (~log_coarseness_{}_feature_?.dat)...'.format(coarseness))
        for fid in range(len(features_liver)):
            filename = 'log_coarseness_{}_feature_{}.dat'.format(coarseness, __FEATURE_MAP[fid])
            # check if output file exists
            if not args.force:
                if os.path.exists(filename):
                    logger.warning('The output file {} already exists. Exiting.'.format(filename))
                    sys.exit(0)
            # create file
            with open(filename, 'w') as f:
                f.write('# Coarseness {}, Feature {}\n'.format(coarseness, __FEATURE_MAP[fid]))
                f.write('# First row is liver, then foreground and then background.\n')
                f.write('# The columns are: x, mean, lower qaurtile, upper quartile, min, max\n')
                f.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(1, *(5*[features_liver[fid]]))) # five time the same
                f.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(2, *__get_features_stats(features_fg[fid])))
                f.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(3, *__get_features_stats(features_bg[fid])))
    
    logger.info('Successfully terminated.')
    
def __get_features_stats(features):
    """
    Compute some statistics of a discrete collection of feature values.
    """
    mean = sum(features)/float(len(features))
    lower_quartile = sorted(features)[int(round(0.25*(len(features) +1)))]
    upper_quartile = sorted(features)[int(round(0.75*(len(features) +1)))]
    minimum = min(features)
    maximum = max(features)
    return mean, lower_quartile, upper_quartile, minimum, maximum

def __distance(model1, model2):
    """
    Return a numeric value of the distance between two models.
    The further apart the models, the higher its value.
    """
    return tuple(scipy.asarray(model1) - scipy.asarray(model2))
    
def __create_liver_model(rids, bounding_boxes, label_image, original_image):
    """
    Extract features from the regions of the filtered image that are covered by the
    supplied rids.
    """
    # create a mask to extract all relevant pixels from the filtered liver image
    liver_img_mask = scipy.zeros(original_image.shape, dtype=scipy.bool_)
    for rid in rids: liver_img_mask[label_image[bounding_boxes[rid -1]] == rid] = True
    
    # extract features from the liver image
    return __features(original_image[liver_img_mask])
    
def __create_region_model(rid, bounding_boxes, label_image, original_image):
    """
    Extract features from a region designated by the supplied rid.
    """
    # create views on images
    original = original_image[bounding_boxes[rid - 1]]
    label = label_image[bounding_boxes[rid - 1]]
    
    # create a mask to extract all relevant pixels from the filtered liver image
    mask = label == rid
    
    # extract features from the liver region
    return __features(original[mask])

def __features(voxels): # 100^3 in 60-100ms
    """
    Compute the mean, entropy and uniformity of the supplied image.
    @param image as an 1D array of voxels
    @returns mean, entropy, uniformity as tuple
    """
    mean = voxels.mean()
    voxels = scipy.digitize(voxels, scipy.unique(voxels)) # digitize (each grey value is mapped to an int); this is possible as the calculations below do not care about the actual grey values, but only their probabilities
    dist = scipy.bincount(voxels)/float(voxels.size) # compute probability histogram (work only for ints)
    entropy = 0
    uniformity = 0
    for grey_value in scipy.unique(voxels):
        entropy += dist[grey_value] * math.log(dist[grey_value], 2)
        uniformity += math.pow(dist[grey_value], 2)
    entropy *= -1
    return mean, entropy, uniformity
    
def  __load(picklefile, original, label):
    """
    Load a pickled testbed as well as the original and label image for further processing.
    The label image will be relabeled to start with region id 1.
    @param picklefile the testbed pickle file name
    @param original the original image file name
    @param label the label image file name
    @return a tuple containing:
        original: the original image data as ndarray
        label: the label image data as ndarray
        bounding_boxes: the bounding boxes around the label image regions (Note that the the bounding box of a region with id rid is accessed using bounding_boxes[rid - 1])
        model_fg_ids: the region ids of all regions to create the foreground model from
        model_bg_ids: the region ids of all regions to create the background model from
        eval_ids: the regions to evaluate the regions term on, represented by their ids
        truth_fg: subset of regions from the eval_ids that are foreground according to the ground-truth
        truth_bg:  subset of regions from the eval_ids that are background according to the ground-truth
    """
    # load and preprocess images
    original_image = load(original)
    label_image = load(label)
    
    original_image_d = scipy.squeeze(original_image.get_data())
    label_image_d = scipy.squeeze(label_image.get_data())
    
    # relabel the label image to start from 1
    label_image_d = medpy.filter.relabel(label_image_d, 1)
    
    # extracting bounding boxes
    bounding_boxes = find_objects(label_image_d)
    
    # load testbed
    with open(picklefile, 'r') as f:
        model_fg_ids = pickle.load(f)
        pickle.load(f) # model_bg_ids
        eval_ids = pickle.load(f)
        truth_fg = pickle.load(f)
        truth_bg = pickle.load(f)
            
    return original_image_d, label_image_d, bounding_boxes, model_fg_ids, eval_ids, truth_fg, truth_bg
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    args.coarseness = [float(x) for x in args.coarseness.split(',')]
    if 0 >= min(args.coarseness): parser.error('All coarseness values must be strictly greater than zero.')
    return args
   
def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('original', help='The original image.')
    parser.add_argument('label', help='The label image.')
    parser.add_argument('testbench', help='The testbench to test the regional term against.')
    parser.add_argument('coarseness', help='The coarseness of the texture (i.e. sigma of the LoG image filter). Number of colon separated floats.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()
