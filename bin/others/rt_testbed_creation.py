#!/usr/bin/python

"""Creates a testbed file for regional term testing."""

# build-in modules
import argparse
import logging
import random
import pickle
import sys
import os

# third-party modules
import scipy
from scipy.ndimage.measurements import find_objects
from scipy.ndimage.morphology import binary_erosion, binary_dilation
from nibabel.loadsave import load

# own modules
from medpy.core import Logger
import medpy.filter

# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2012-02-24"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Create a testbed for evaluating a regional term.
                  Creates a *.pickle file containing regions
                  1) to create a foreground-model from
                  2) to create a background-model from
                  3) to use for evaluating the regional term
                  4) which are true foreground
                  5) which are true background 
                  6) which were true-positive, fp, tn, and fn decided by the boundary term.
                  The function __load(pickle, original, label) in this file can be
                  exported to load the testbench into any other script.
                  """

# code
def main():
    # parse cmd arguments
    parser = getParser()
    parser.parse_args()
    args = getArguments(parser)
    
    # compose the target file name
    if sys.maxsize == args.evalmax and sys.maxsize == args.fgmax and sys.maxsize == args.bgmax:
        target = 'tstb_{}_unrestricted_{}.pickle'.format(args.mode, args.suffix)
    else:
        target = 'tstb_{}_restricted_{}.pickle'.format(args.mode, args.suffix)
    
    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # check if output file exists
    if not args.force:
        if os.path.exists(target):
            logger.warning('The output file {} already exists. Exiting.'.format(target))
            sys.exit(0)
    
    logger.info('Loading images...')
    if 'strict' == args.mode: label, mask, boundary, fg, bg = __load_images(args.label, args.mask, args.boundary, args.fgmask, args.bgmask)
    else: label, mask, boundary = __load_images(args.label, args.mask, args.boundary)
    
    logger.info('Extracting bounding boxes...')
    bounding_boxes = find_objects(label)
    
    
    logger.info('Determining ground truth...')
    truth_fg, truth_bg = __compute_affiliation(label, mask, bounding_boxes)
    
    # switch to the right mode for regional model creation
    if 'strict' == args.mode:
        logger.info('STRICT mode: Creating regional model from foreground and background markers only...')
        # check whether the fg markers mark any true background or if the bg markers mark any true foreground
        if (fg & ~mask).any():
            logger.warn('The foreground markers denote some true background.')
        if (bg & mask).any():
            logger.warn('The background markers denote some true foreground.')
    else: # loose mode
        logger.info('LOOSE mode: Creating regional model from all regions except in a narrow band around the ground truth...')
        # obtain narrow band
        fg = binary_erosion(mask, iterations=args.iterations)
        bg = ~binary_dilation(mask, iterations=args.iterations)
        if len((mask & fg).nonzero()[0]) != len((boundary & fg).nonzero()[0]):
            logger.warning('The narrow band was not chosen wide enough to include all wrongly classified regions of the boundary term only run. Please increase the iterations. Missed voxels: {}'.format(abs(len((mask & fg).nonzero()[0]) - len((boundary & fg).nonzero()[0]))))
        
    # perform test on the fg and bg markers
    if (fg & bg).any():
        logger.warn('Foreground and background markers intersect.')
        
    logger.info('Determining regions used for building the regional term models...')
    model_fg_ids = scipy.unique(label[fg])
    model_bg_ids = scipy.unique(label[bg])
    
    logger.info('Determining regions used evaluation (the inverse of bg | fg)...')
    eval_ids = scipy.unique(label[~(fg | bg)])
    eval_ids = list(set(eval_ids) - set(model_fg_ids) - set(model_bg_ids))

    logger.debug('Maximal region term model will be created with {} fg, {} bg and evaluated against {} regions.'.format(len(model_fg_ids),
                                                                                                                len(model_bg_ids),
                                                                                                                len(eval_ids)))
    logger.info('Applying restriction settings...')
    model_fg_ids = random.sample(model_fg_ids, min(args.fgmax, len(model_fg_ids)))
    model_bg_ids = random.sample(model_bg_ids, min(args.bgmax, len(model_bg_ids)))
    eval_ids = random.sample(eval_ids, min(args.evalmax, len(eval_ids)))
    
    logger.debug('Real region term model will be created with {} fg, {} bg and evaluated against {} regions.'.format(len(model_fg_ids),
                                                                                                                len(model_bg_ids),
                                                                                                                len(eval_ids)))
    
    logger.info('Extracting boundary term results...')
    bdr_fg, bdr_bg = __compute_affiliation(label, boundary, bounding_boxes)
    
    logger.info('Restrict boundary term results and ground truth to relevant evaluation regions...')
    bdr_fg = list(set(bdr_fg) & set(eval_ids))
    bdr_bg = list(set(bdr_bg) & set(eval_ids))
    truth_fg = list(set(truth_fg) & set(eval_ids))
    truth_bg = list(set(truth_bg) & set(eval_ids))
    
    if len(eval_ids) != len(set(bdr_fg).union(bdr_bg)):
        raise Exception('Boundary results are not equal to evaluation relevant regions.')
    if len(eval_ids) != len(set(truth_fg).union(truth_bg)):
        raise Exception('Ground truth is not equal to evaluation relevant regions.')
    
    logger.info('Pickle obtained results results to testbed file {}...'.format(target))
    with open(target, 'w') as f:
        pickle.dump(model_fg_ids, f)
        pickle.dump(model_bg_ids, f)
        pickle.dump(eval_ids, f)
        pickle.dump(truth_fg, f)
        pickle.dump(truth_bg, f)
        pickle.dump(bdr_fg, f)
        pickle.dump(bdr_bg, f)
    
    logger.info('Successfully terminated.')
        
def __compute_affiliation(label_image, mask_image, bounding_boxes):
    """
    Computes which regions of the supplied label_image belong to the mask_image's foreground
    respectively background. When a region belongs to both, it is assigned to the foreground
    if more voxels belong to the foreground than in the background and vice-versa.
    In the case of equal affiliation, the region is assigned to the background.
    @return fg_ids, bg_ids
    """
    # simple extraction
    fg_ids = list(scipy.unique(label_image[mask_image]))
    bg_ids = list(scipy.unique(label_image[~mask_image]))
    # decide for overlapping regions whether they are 50 or more in fg or in bg
    for rid in set(fg_ids) & set(bg_ids):
        relevant_region_label_image = label_image[bounding_boxes[rid - 1]]
        relevant_region_mask_image = mask_image[bounding_boxes[rid - 1]]
        fg_part = 0
        bg_part = 0
        for affiliation, rid2 in zip(relevant_region_mask_image.ravel(), relevant_region_label_image.ravel()):
            if rid2 == rid:
                if affiliation: fg_part += 1
                else: bg_part += 1
        #fg_part = relevant_region_label_image[relevant_region_mask_image]
        #bg_part = relevant_region_label_image[~relevant_region_mask_image]
        if fg_part > bg_part: # if more voxels of region rid in fg than in bg
            bg_ids.remove(rid)
        else:
            fg_ids.remove(rid)
    # debug line, can be removed if the above code is final
    if 0 != len(set(fg_ids) & set(bg_ids)): raise Exception('Error making fg and bg ground truth distinct.') 
    return fg_ids, bg_ids
        
        
def __load_images(label_image_n, mask_image_n, boundary_image_n, fg_image_n = False, bg_image_n = False):
    """
    Load and return all image data in preprocessed ndarrays.
    The label image will be relabeled to start from 1.
    @return label, ground-truth-mask, boundary-result-mask[, fg-markers, bg-markers]
    """
    # load images
    label_image = load(label_image_n)
    mask_image = load(mask_image_n)
    boundary_image = load(boundary_image_n)
    if fg_image_n: fg_image = load(fg_image_n)
    if bg_image_n: bg_image = load(bg_image_n)
    
    # extract image data
    label_image_d = scipy.squeeze(label_image.get_data())
    mask_image_d = scipy.squeeze(mask_image.get_data()).astype(scipy.bool_)
    boundary_image_d = scipy.squeeze(boundary_image.get_data()).astype(scipy.bool_)
    if fg_image_n: fg_image_d = scipy.squeeze(fg_image.get_data()).astype(scipy.bool_)
    if bg_image_n: bg_image_d = scipy.squeeze(bg_image.get_data()).astype(scipy.bool_)
    
    # check if images are of same dimensionality
    if label_image_d.shape != mask_image_d.shape: raise argparse.ArgumentError('The mask image {} must be of the same dimensionality as the label image {}.'.format(mask_image_d.shape, label_image_d.shape))
    if label_image_d.shape != boundary_image_d.shape: raise argparse.ArgumentError('The boundary term image {} must be of the same dimensionality as the label image {}.'.format(boundary_image_d.shape, label_image_d.shape))
    if fg_image_n:
        if label_image_d.shape != fg_image_d.shape: raise argparse.ArgumentError('The foreground markers image {} must be of the same dimensionality as the label image {}.'.format(fg_image_d.shape, label_image_d.shape))
    if bg_image_n:
        if label_image_d.shape != bg_image_d.shape: raise argparse.ArgumentError('The background markers image {} must be of the same dimensionality as the label image {}.'.format(bg_image_d.shape, label_image_d.shape))
    
    # relabel the label image to start from 1
    label_image_d = medpy.filter.relabel(label_image_d, 1)
    
    if fg_image_n:
        return label_image_d, mask_image_d, boundary_image_d, fg_image_d, bg_image_d
    else:
        return label_image_d, mask_image_d, boundary_image_d
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    
    if 'strict' == args.mode:
        if None == args.fgmask: parser.error('In \'strict\' mode an image with foreground markers must be supplied.')
        if None == args.bgmask: parser.error('In \'strict\' mode an image with background markers must be supplied.')
    else: # loose mode
        if args.iterations <= 0: parser.error('The supplied iterations value must be strictly positive.')
    if args.evalmax <= 0: parser.error('The supplied evalmax value must be strictly positive.')
    if args.fgmax <= 0: parser.error('The supplied fgmax value must be strictly positive.')
    if args.bgmax <= 0: parser.error('The supplied bgmax value must be strictly positive.')
    
    return args

def getParser():
    "Creates and returns the argparse parser object."
    epilog = '''The testbed can be constructed in two modes: 'strict' and 'loose'.
                In 'strict'-mode the supplied foreground- and background-marker-images
                are used to extract the regions which the test can use to construct the
                foreground resp. background models. This means that, depending on the
                markers size, the models have only few regions for training. This
                corresponds to the normal GraphCut case.
                In 'loose' mode, no foreground or background-marker-image has to be
                supplied. Instead the ground-truth of the liver-mask is used to determine
                the foreground and background regions suitable for model creation. A
                narrow band along the surface of the liver-mask of a width determined by
                the supplied 'iterations' parameter is created. All regions inside this
                band are taken for evaluation, all outside for background-model- and all
                inside for foreground-model-creation. 
                Note that this second approach uses the supplied ground-truth and can
                therefore not be considered the normal case. But is is suitable 1) to
                get a rough estimation of a regional terms performance that is
                independent from the foreground- and background-markers and 2) as
                realistic cases for 2-run GraphCut algorithms.
                It is recommended to inspect the created testbench with the visualization
                script.'''
    parser = argparse.ArgumentParser(description=__description__, epilog=epilog)


    parser.add_argument('mode', choices={'strict', 'loose'}, default='loose', help='The strictness of the model extraction. See epilog for more details.')
    parser.add_argument('label', help='The watershed label image.')
    parser.add_argument('mask', help='The ground-truth liver-mask.')
    parser.add_argument('boundary', help='The boundary term created liver-mask.')
    parser.add_argument('--eval-max', dest='evalmax', type=int, default=sys.maxsize, help='Restrict the number of regions designated for evaluation. They will be picked randomly.')
    parser.add_argument('--fg-max', dest='fgmax', type=int, default=sys.maxsize, help='Restrict the number of regions designated to create the foreground model. They will be picked randomly.')
    parser.add_argument('--bg-max', dest='bgmax', type=int, default=sys.maxsize, help='Restrict the number of regions designated to create the background model. They will be picked randomly.')
    parser.add_argument('--suffix', help='A suffix for the created testbed pickle file.')
    group_strict = parser.add_argument_group('strict mode only')
    group_strict.add_argument('--fg-mask', dest='fgmask', help='Mask image containg the foureground markers.')
    group_strict.add_argument('--bg-mask', dest='bgmask', help='Mask image containg the foureground markers.')
    group_loose = parser.add_argument_group('loose mode only')
    group_loose.add_argument('--iterations', type=int, default=9, help='Determines the width of the narrow band. Warnings are signaled, if this values is set to low.')
    group_others = parser.add_argument_group('others')
    group_others.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    group_others.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    group_others.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser

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
        bdr_fg: subset of regions from the eval_ids that are foreground according to the boundary term segmentation
        bdr_bg: subset of regions from the eval_ids that are background according to the boundary term segmentation
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
        model_bg_ids = pickle.load(f)
        eval_ids = pickle.load(f)
        truth_fg = pickle.load(f)
        truth_bg = pickle.load(f)
        bdr_fg = pickle.load(f)
        bdr_bg = pickle.load(f)
            
    return original_image_d, label_image_d, bounding_boxes, model_fg_ids, model_bg_ids, eval_ids, truth_fg, truth_bg, bdr_fg, bdr_bg
    
if __name__ == "__main__":
    main()           