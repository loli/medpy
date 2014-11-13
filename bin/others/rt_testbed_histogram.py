#!/usr/bin/python

"""Uses a testbed to test some histogram regional terms."""

# build-in modules
import logging
import pickle
import argparse

# third-party modules
import numpy
from nibabel.loadsave import load
from scipy.ndimage.measurements import find_objects

# path changes

# own modules
from medpy.core import Logger
import medpy.filter
from medpy.metric.histogram import *
from medpy.features.histogram import fuzzy_histogram

# information
__author__ = "Oskar Maier"
__version__ = "r0.3, 2012-02-24"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Test a number of histogram region terms against a testbench.
                  """

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
    original, label, bounding_boxes, model_fg_ids, model_bg_ids, eval_ids, truth_fg, truth_bg, bdr_fg, bdr_bg = __load(args.testbench, args.original, args.label)
            
    logger.debug('Region term model will be created with {} fg, {} bg and evaluated against {} regions.'.format(len(model_fg_ids),
                                                                                                                len(model_bg_ids),
                                                                                                                len(eval_ids)))
            
    logger.debug('Of the {} eval regions, {} are fg and {} bg.'.format(len(eval_ids), len(truth_fg), len(truth_bg))) 
    
    rang = (original.min(), original.max()) # 176ms !!!
    
    logger.info('Create foreground model...')
    model_fg = __create_histogram(model_fg_ids, bounding_boxes, label, original, rang, args.hsize, __HISTOGRAMS[args.histogram])
    
    logger.info('Create background model...')
    model_bg = __create_histogram(model_bg_ids, bounding_boxes, label, original, rang, args.hsize,  __HISTOGRAMS[args.histogram])
    
    logger.info('Using models to decide affiliation of evaluation regions...')
    reg_fg = []
    reg_bg = []
    for rid in eval_ids: 
        model_region = __create_histogram([rid], bounding_boxes, label, original, rang, args.hsize,  __HISTOGRAMS[args.histogram]) # 124us  / ~2min for 1 million runs
        if __DISTANCES[args.distance](model_fg, model_region) > __DISTANCES[args.distance](model_bg, model_region): # 3.71us
            reg_bg.append(rid) # 79.7 ns
        else:
            reg_fg.append(rid) # 79.7 ns
    
    logger.info('Determining best possible mixture between boundary and regional term...')
    # Regions for which both, regional and boundary term, decided that they belong to the fg resp. bg are kept.
    # Regions for which they classification differs are determined in the best possible way (i.e. classifying them right)
    # ! This evaluation is not too reliable, due to the high over-segmentation of the boundary term 
    _fg_intersection = set(reg_fg) & set(bdr_fg) # intersection (these regions will always be assigned to fg)
    _bg_intersection = set(reg_bg) & set(bdr_bg) # intersection (these regions will always be assigned to bg)
    _nintersection = (set(reg_fg) ^ set(bdr_fg)) | (set(reg_bg) ^ set(bdr_bg)) # non-intersecting part, the one we can decide on
    best_fg = _nintersection & set(truth_fg) | _fg_intersection# classify perfectly
    best_bg = _nintersection & set(truth_bg) | _bg_intersection# classify perfectly
    
    logger.info('Determining medium mixture model between boundary and regional term...')
    # All disputed regions are divides into two equal sets, of which one contains 50% fg
    # and 50% bg regions (as far as possible). These regions are assigned wrongly. All
    # regions in the other set are assigned rightly.
    _one_fourth = int(len(_nintersection) / 4.) # roughly one fourth of the disputed regions
    _disputed_fg = _nintersection & set(truth_fg)
    _disputed_bg = _nintersection & set(truth_bg)
    # determine the number of elements to take from each disputed set
    if len(_disputed_fg) < _one_fourth:
        _fg_part = len(_disputed_fg)
        _bg_part = _one_fourth + _one_fourth - len(_disputed_fg)
        logger.warning('Could not create ideal 50/50 medium mixture model.')
    elif len(_disputed_bg) < _one_fourth:
        _bg_part = len(_disputed_bg)
        _fg_part = _one_fourth + _one_fourth - len(_disputed_bg)
        logger.warning('Could not create ideal 50/50 medium mixture model.')
    else:
        _fg_part = _one_fourth
        _bg_part = _one_fourth
    # split disputed sets to for medium mixture model
    medium_bg = list(_disputed_fg)[:_fg_part]
    medium_fg = list(_disputed_fg)[_fg_part:]
    medium_fg.extend(list(_disputed_bg)[:_bg_part])
    medium_bg.extend(list(_disputed_bg)[_bg_part:])
    medium_fg.extend(_fg_intersection)
    medium_bg.extend(_bg_intersection)
    
    logger.info('Determining werst mixture model between boundary and regional term...')
    worst_fg = best_bg # assuming worst possible decision
    worst_bg = best_fg # assuming worst possible decision
    
            
    logger.info('Determining regional term statistics...')
    reg_tp, reg_fp, reg_tn, reg_fn = __compute_statistics(reg_fg, reg_bg, truth_fg, truth_bg)
    
    logger.info('Determining boundary term statistics...')
    bdr_tp, bdr_fp, bdr_tn, bdr_fn = __compute_statistics(bdr_fg, bdr_bg, truth_fg, truth_bg)
    
    logger.info('Determining best mixture statistics...')
    best_tp, best_fp, best_tn, best_fn = __compute_statistics(best_fg, best_bg, truth_fg, truth_bg)
    
    logger.info('Determining normal mixture statistics...')
    medium_tp, medium_fp, medium_tn, medium_fn = __compute_statistics(medium_fg, medium_bg, truth_fg, truth_bg)
    
    logger.info('Determining worst mixture statistics...')
    worst_tp, worst_fp, worst_tn, worst_fn = __compute_statistics(worst_fg, worst_bg, truth_fg, truth_bg)
    
    __print_result_headline()
        
    print('{:<30}'.format('regional_term'), end=' ')
    __print_rating(reg_tp, reg_fp, reg_tn, reg_fn)
    
    print('{:<30}'.format('boundary_term'), end=' ')
    __print_rating(bdr_tp, bdr_fp, bdr_tn, bdr_fn)
    
    print('{:<30}'.format('best_mixture'), end=' ')
    __print_rating(best_tp, best_fp, best_tn, best_fn)
    
    print('{:<30}'.format('medium_mixture'), end=' ')
    __print_rating(medium_tp, medium_fp, medium_tn, medium_fn)
    
    print('{:<30}'.format('worst_mixture'), end=' ')
    __print_rating(worst_tp, worst_fp, worst_tn, worst_fn)
    
    if len(truth_fg) > len(truth_bg): bsl_fg, bsl_bg = eval_ids, []
    else: bsl_fg, bsl_bg = [], eval_ids
    print('{:<30}'.format('statistical_baseline'), end=' ')
    __print_rating(*__compute_statistics(bsl_fg, bsl_bg, truth_fg, truth_bg))
    
    best_mix_fscore, best_mix_accuracy = __calculate_rating(best_tp, best_fp, best_tn, best_fn)
    print('{:<30}'.format('best_mix_against_stat_bsl'), end=' ')
    bsl_fscore, bsl_accuracy = __calculate_rating(*__compute_statistics(bsl_fg, bsl_bg, truth_fg, truth_bg))
    print('{:>+15.4f}{:>+15.4f}'.format(best_mix_accuracy - bsl_accuracy, best_mix_fscore - bsl_fscore))
    
    print('{:<30}'.format('best_mix_against_bnd_term'), end=' ')
    bdr_fscore, bdr_accuracy = __calculate_rating(bdr_tp, bdr_fp, bdr_tn, bdr_fn)
    print('{:>+15.4f}{:>+15.4f}'.format(best_mix_accuracy - bdr_accuracy, best_mix_fscore - bdr_fscore))
    
    medium_mix_fscore, medium_mix_accuracy = __calculate_rating(medium_tp, medium_fp, medium_tn, medium_fn)
    print('{:<30}'.format('medium_mix_against_bnd_term'), end=' ')
    print('{:>+15.4f}{:>+15.4f}'.format(medium_mix_accuracy - bdr_accuracy, medium_mix_fscore - bdr_fscore))
    
    worst_mix_fscore, worst_mix_accuracy = __calculate_rating(worst_tp, worst_fp, worst_tn, worst_fn)
    print('{:<30}'.format('worst_mix_against_bnd_term'), end=' ')
    print('{:>+15.4f}{:>+15.4f}'.format(worst_mix_accuracy - bdr_accuracy, worst_mix_fscore - bdr_fscore))
    
    logger.info('Successfully terminated.')

###
# Histogram creations methods
###
__HISTOGRAMS = {'standard': numpy.histogram,
                'triangular': lambda *args, **kwargs: fuzzy_histogram(*args, membership='triangular', **kwargs),
                'trapezoid': lambda *args, **kwargs: fuzzy_histogram(*args, membership='trapezoid', **kwargs),
                'gaussian': lambda *args, **kwargs: fuzzy_histogram(*args, membership='gaussian', **kwargs),
                'sigmoid': lambda *args, **kwargs: fuzzy_histogram(*args, membership='sigmoid', **kwargs)}

###
# Histogram distance measures
###
# available distance measures and their mapping to the respective functions
__DISTANCES = {'chebyshev': chebyshev,
               'chebyshev_neg': chebyshev_neg,
               'chi_square': chi_square,               
               'correlate': correlate_1,
               'cosine_1': cosine_1,
               'cosine_2': cosine_2,
               'cosine_alt': cosine_alt,
               'euclidean': euclidean,
               'histogram_intersection': histogram_intersection_1,
               'jensen_shannon': jensen_shannon,
               'kullback_leibler': kullback_leibler,
               'manhattan': manhattan,
               'minowski_p3': lambda x,y: minowski(x, y, 3),
               'minowski_p5': lambda x,y: minowski(x, y, 5),
               'minowski_p10': lambda x,y: minowski(x, y, 10),
               'minowski_pm1': lambda x,y: minowski(x, y, -1),
               'minowski_pm2': lambda x,y: minowski(x, y, -2),
               'noelle_1': noelle_1,
               'noelle_2': noelle_2,
               'noelle_3': noelle_3,
               'noelle_4': noelle_4,
               'noelle_5': noelle_5,
               'relative_bin_deviation': relative_bin_deviation,
               'relative_deviation': relative_deviation}
# chebyshev chebyshev_neg chi_square correlate cosine_1 cosine_2 cosine_alt euclidean histogram_intersection jensen_shannon kullback_leibler manhattan minowski_p3 minowski_p5 minowski_p10 minowski_pm1 minowski_pm2 noelle_1 noelle_2 noelle_3 noelle_4 noelle_5 relative_bin_deviation relative_deviation

###
# Convenience functions
###

def __print_result_headline():
    """Print the headline of the results printed with @link __print_rating()."""
    print('# RESULTS:')
    print('# (Problem defined as binary classification if fg or not.)')
    print('# (Precision is the fraction of retrieved instances that are relevant, while recall is the fraction of relevant instances that are retrieved.)')
    print('# (Every dataline denotes the performance of the designated model.)')
    print('#')
    print('#{:<31}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}{:^15}'.format('Model', 'Accuracy', 'F-score', 'Specificity', 'Precision', 'Recall', 'true-positive', 'false-positive', 'true-negative', 'false-negative')) 

def __print_rating(tp, fp, tn, fn):
    tp = float(tp)
    fp = float(fp)
    tn = float(tn)
    fn = float(fn)
    p = 0 if 0 == (tp + fp) else tp / (tp + fp)
    r = 0 if 0 == (tp + fn) else tp / (tp + fn)
    s = '{:>+15.4f}{:>+15.4f}{:>+15.4f}{:>+15.4f}{:>+15.4f}{:>+15,}{:>+15,}{:>+15,}{:>+15,}'
    print(s.format(0 if 0 == (tp + tn + fp + fn) else (tp + tn) / (tp + tn + fp + fn), # accuracy
                   0 if 0 == (p + r) else 2 * (p * r)/(p + r), #f-score
                   0 if 0 == (tn + fp) else tn / (tn + fp), # specificity
                   p, # precision
                   r, # recall,
                   tp, fp, tn, fn))
    
def __calculate_rating(tp, fp, tn, fn):
    """
    @return fscore, accuracy
    """
    tp = float(tp)
    fp = float(fp)
    tn = float(tn)
    fn = float(fn)
    p = 0 if 0 == (tp + fp) else tp / (tp + fp)
    r = 0 if 0 == (tp + fn) else tp / (tp + fn)
    return 0 if 0 == (p + r) else 2 * (p * r)/(p + r), 0 if 0 == (tp + tn + fp + fn) else (tp + tn) / (tp + tn + fp + fn)

def __create_histogram(rids, bounding_boxes, label_image, original_image, rang, hsize, histogram): # 121us with one len(rids) = 1
    """
    Creates a histogram from the voxels of all regions joined together.
    """
    voxels = []
    for rid in rids:
        region_voxels = original_image[bounding_boxes[rid - 1]][label_image[bounding_boxes[rid - 1]] == rid] # 25.8us
        if 0 == len(region_voxels): raise Exception("(__create_model_histogram) failed on region {}".format(rid))
        voxels.extend(region_voxels)
    return histogram(voxels, bins=hsize, range=rang, normed=True)[0] # 81.4ms
    
    
def __compute_statistics(fg_is, bg_is, fg_should, bg_should):
    """
    Takes a number of is and shoulds and return the number of true-positives,
    false-positives, true-negatives and false-negatives (assuming that fg is
    the binary True and bg the binary False)
    @return tp, fp, tn, fn
    """
    if len(fg_is) + len(bg_is) != len(fg_should) + len(bg_should):
        raise Exception('Discreptance between classified regions and regions to classify ({} to {}).'.format(len(fg_is) + len(bg_is),
                                                                                                             len(fg_should) + len(bg_should)))
    tp = list(set(fg_is) & set(fg_should))
    fp = list(set(fg_is) - set(fg_should))
    tn = list(set(bg_is) & set(bg_should))
    fn = list(set(bg_is) - set(bg_should))
    return len(tp), len(fp), len(tn), len(fn)

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
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()
   
def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('original', help='The original image.')
    parser.add_argument('label', help='The label image.')
    parser.add_argument('testbench', help='The testbench to test the regional term agains.')
    parser.add_argument('distance', default='cosine', choices=list(__DISTANCES.keys()), help='The distance measure to use.')
    parser.add_argument('--histogram', dest='histogram', default='standard', choices=list(__HISTOGRAMS.keys()), help='The type of histogram to use (all except standard are fuzzy).')
    parser.add_argument('--hsize', dest='hsize', type=int, default=100, help='The size of the histogram to use.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    return parser    
    
if __name__ == "__main__":
    main()
