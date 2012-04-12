#!/usr/bin/python

# build-in modules
import logging

# third-party modules
import scipy
import numpy
from medpy import filter
from nibabel.loadsave import load
from medpy.core import Logger
from scipy.ndimage.measurements import find_objects
import random
from scipy.ndimage.morphology import binary_dilation, binary_erosion
import math
import cPickle as pickle

# path changes

# own modules

# constants
# If set to True, only the foreground and background markers are used to build the region term models
# If set to False, the complete foreground and background area exempt a narrow band around the ground truth mask is used to build the region term models
__STRICT = False

# Determines the width of the narrow band. If you get warnings about the narrow band being to narrow, increase this values.
# In practice this value determines the number of iterations used for dilation and erosion to obtain a narrow band. 
__ITERATIONS = 9

# Determine the histogram size (#bins) for histogram based regions terms
__H_SIZE = 100

# Load settings from pickle file instead of extracting from images
__PICKLE_LOAD = False
# Save extract settings into pickle file (this setting is ignored if __PICKLE_LOAD is set to True)
__PICKLE_SAVE = True
# The name of the testbench to load
__PICKLE_NAME = 'eval_viscous2.pickle'

# Restrictive settings
# Determines the maximum number of (randomly chosen) regions over which to perform the evaluation
__EVAL_MAX = 1000000000000
# Determines the maximum number of (randomly chosen) foreground regions used to build the regional term model from
__FG_MAX = 100000000000
# Determines the maximum number of (randomly chosen) background regions used to build the regional term model from
__BG_MAX = 1000000000000

# code
def main(): 
    # prepare logger
    logger = Logger.getInstance()
    logger.setLevel(logging.DEBUG)
    

    logger.info('Loading and preparing images...')
    original, label, mask, boundary, fg, bg = __get_images() #@return: original, label, ground-truth-mask, boundary-result-mask, fg-markers, bg-markers
    
    logger.info('Extracting bounding boxes...')
    bounding_boxes = find_objects(label)
    
    if not __PICKLE_LOAD:
        logger.info('Determining ground truth...')
        truth_fg, truth_bg = __compute_affiliation(label, mask, bounding_boxes)
        
        # switch to the right mode for regional model creation
        if __STRICT:
            logger.info('STRICT mode: Creating regional model from foreground and background markers only...')
            # check whether the fg markers mark any true background or if the bg markers mark any true foreground
            if (fg & ~mask).any():
                logger.warn('The foreground markers denote some true background.')
            if (bg & mask).any():
                logger.warn('The background markers denote some true foreground.')
        else:
            logger.info('LOOSE mode: Creating regional model from all regions except in a narrow band around the ground truth...')
            # obtain narrow band
            fg = binary_erosion(mask, iterations=__ITERATIONS)
            bg = ~binary_dilation(mask, iterations=__ITERATIONS)
            if len((mask & fg).nonzero()[0]) != len((boundary & fg).nonzero()[0]):
                logger.warning('The narrow band was not chosen wide enough to include all wrongly classified regions of the boundary term only run. Missed voxels: {}'.format(abs(len((mask & fg).nonzero()[0]) - len((boundary & fg).nonzero()[0]))))
            
        # perform test on the fg and bg markers
        if (fg & bg).any():
            logger.warn('Foreground and background markers intersect.')
            
        logger.info('Determining regions used for building the regional term models...')
        model_fg_ids = scipy.unique(label[fg])
        model_bg_ids = scipy.unique(label[bg])
        
        logger.info('Determining regions used evaluation (the inverse of bg | fg)...')
        eval_ids = scipy.unique(label[~(fg | bg)])
        eval_ids = list(set(eval_ids) - set(model_fg_ids) - set(model_bg_ids))

        logger.debug('Region term model will be created with {} fg, {} bg and evaluated against {} regions.'.format(len(model_fg_ids),
                                                                                                                    len(model_bg_ids),
                                                                                                                    len(eval_ids)))
        
        logger.info('Applying restriction settings...')
        model_fg_ids = random.sample(model_fg_ids, min(__FG_MAX, len(model_fg_ids)))
        model_bg_ids = random.sample(model_bg_ids, min(__BG_MAX, len(model_bg_ids)))
        eval_ids = random.sample(eval_ids, min(__EVAL_MAX, len(eval_ids)))
        
        logger.debug('Region term model will be created with {} fg, {} bg and evaluated against {} regions.'.format(len(model_fg_ids),
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
        
        if __PICKLE_SAVE:
            logger.info('Pickle obtained results results...')
            with open(__PICKLE_NAME, 'w') as f:
                pickle.dump(model_fg_ids, f)
                pickle.dump(model_bg_ids, f)
                pickle.dump(eval_ids, f)
                pickle.dump(truth_fg, f)
                pickle.dump(truth_bg, f)
                pickle.dump(bdr_fg, f)
                pickle.dump(bdr_bg, f)
        return
    
    else: # __PICKLE_LOAD is True
        logger.info('Unpickle obtained results...')
        with open(__PICKLE_NAME, 'r') as f:
            model_fg_ids = pickle.load(f)
            model_bg_ids = pickle.load(f)
            eval_ids = pickle.load(f)
            truth_fg = pickle.load(f)
            truth_bg = pickle.load(f)
            bdr_fg = pickle.load(f)
            bdr_bg = pickle.load(f)
            
            logger.debug('Region term model will be created with {} fg, {} bg and evaluated against {} regions.'.format(len(model_fg_ids),
                                                                                                                        len(model_bg_ids),
                                                                                                                        len(eval_ids)))
            
    logger.debug('Of the {} eval regions, {} are fg and {} bg.'.format(len(eval_ids), len(truth_fg), len(truth_bg))) 
    
    rang = (original.min(), original.max()) # 176ms !!!
    
    logger.info('Create foreground model...')
    model_fg = __create_model(model_fg_ids, bounding_boxes, label, original, rang)
    
    logger.info('Create background model...')
    model_bg = __create_model(model_bg_ids, bounding_boxes, label, original, rang)
    
    logger.info('Using models to decide affiliation of evaluation regions...')
    reg_fg = []
    reg_bg = []
    for rid in eval_ids: 
        model_region = __create_model([rid], bounding_boxes, label, original, rang) # 124us  / ~2min for 1 million runs
        if __distance(model_fg, model_region) > __distance(model_bg, model_region): # 3.71us
            reg_bg.append(rid) # 79.7 ns
        else:
            reg_fg.append(rid) # 79.7 ns
    
    logger.info('Determining best possible mixture between boundary and regional term...')
    # Regions for which both, regional and boundary term, decided that they belong to the fg resp. bg are kept.
    # Regions for which they classification differs are determined in the best possible way (i.e. classifying them right) 
    _fg_intersection = set(reg_fg) & set(bdr_fg) # intersection (these regions will always be assigned to fg)
    _fg_nintersection = (set(reg_fg) - set(bdr_fg)) | (set(bdr_fg) - set(reg_fg)) # non-interscting part, the one we can decide on
    _fg_best = _fg_nintersection & set(truth_fg) | _fg_intersection # assuming best possible decision
    _bg_intersection = set(reg_bg) & set(bdr_bg) # intersection (these regions will always be assigned to fg)
    _bg_nintersection = (set(reg_bg) - set(bdr_bg)) | (set(bdr_bg) - set(reg_bg)) # non-intersecting part, the one we can decide on
    _bg_best = _bg_nintersection & set(truth_bg) | _bg_intersection # assuming best possible decision
    
    best_fg = _fg_best | (_bg_nintersection - set(truth_bg)) # add wrongly classified form bg set
    best_bg = _bg_best | (_fg_nintersection - set(truth_fg)) # add wrongly classified form fg set
            
    logger.info('Determining regional term statistics...')
    reg_tp, reg_fp, reg_tn, reg_fn = __compute_statistics(reg_fg, reg_bg, truth_fg, truth_bg)
    
    logger.info('Determining boundary term statistics...')
    bdr_tp, bdr_fp, bdr_tn, bdr_fn = __compute_statistics(bdr_fg, bdr_bg, truth_fg, truth_bg)
    
    logger.info('Determining best mixture statistics...')
    print len(best_fg), len(best_bg), len(truth_fg), len(truth_bg)
    best_tp, best_fp, best_tn, best_fn = __compute_statistics(best_fg, best_bg, truth_fg, truth_bg)
    print best_tp, best_fp, best_tn, best_fn
    
    
    print 'RESULTS:'
    print '(Problem defined as binary classification if fg or not.)'
    print '(Precision is the fraction of retrieved instances that are relevant, while recall is the fraction of relevant instances that are retrieved.)'
    print 'Performance of region term only:'
    __print_rating(reg_tp, reg_fp, reg_tn, reg_fn)
    
    print 'Performance of boundary term only:'
    __print_rating(bdr_tp, bdr_fp, bdr_tn, bdr_fn)
    
    print 'Performance of best possible mixture:'
    __print_rating(best_tp, best_fp, best_tn, best_fn)
    
    
    bsl_fg = list(set(truth_fg).union(truth_bg)) if truth_fg > truth_bg else []
    bsl_bg = list(set(truth_fg).union(truth_bg)) if truth_bg >= truth_fg else []
    print 'Performance statistical baseline:'
    __print_rating(*__compute_statistics(bsl_fg, bsl_bg, truth_fg, truth_bg))
    
    logger.info('Successfully terminated.')
    
    
   
###
# Histogram distance measures
###

def d_euclidean(h1, h2): # 31.7 us
    return math.sqrt(scipy.sum(scipy.power(scipy.absolute(h1 - h2), 2)))

def d_histogramintersection(h1, h2): # 4.37 us
    """@note not a distance, but a similarity mesure."""
    return -1 * scipy.sum(scipy.minimum(h1, h2))

def d_cosine(h1, h2): # 65.7 us
    """@note not a distance, but a similarity mesure."""
    return -1 * float(scipy.sum(h1 * h2)) / (scipy.sum(scipy.power(h1, 2)) * scipy.sum(scipy.power(h2, 2)))

def d_correlate(h1, h2): # 1.13 us
    """@note not a distance, but a similarity mesure."""
    return -1 * scipy.correlate(h1, h2)[0]

def d_minowski(h1, h2, p = 2): # 33 us
    return math.pow(scipy.sum(scipy.power(abs(h1 - h2), p)), 1./p)

def d_taxicab(h1, h2):
    """@note also known as rectilinear distance, L1 distance or L1 norm , city block distance, Manhattan distance, or Manhattan length"""
    return scipy.sum(abs(h1 - h2))
    
         
    


def __print_rating(tp, fp, tn, fn):
    tp = float(tp)
    fp = float(fp)
    tn = float(tn)
    fn = float(fn)
    print '\t#errors: fg tp/fp={}/{} | bg tn/fn={}/{}'.format(tp, fp, tn, fn)
    p = tp / (tp + fp)
    r = tp / (tp + fn)
    print '\tprecision={} / recall={} / f-score={}'.format(p, r, 2 * (p * r)/(p + r))
    print '\tspecificity={} / accuracy = {}'.format(tn / (tn + fp),
                                                           (tp + tn) / (tp + tn + fp + fn))
def __distance(model1, model2):
    """
    Return a numeric value of the distance between two models.
    The further apart the models, the higher its value.
    """
    return __distance_histogram(model1, model2)

def __distance_histogram(h1, h2):
    """
    Returns the distance between two histograms.
    """
    return d_taxicab(h1, h2)
    
def __create_model(rids, bounding_boxes, label_image, original_image, rang):
    """
    Creates a regional term model.
    """
    return __create_model_histogram(rids, bounding_boxes, label_image, original_image, rang)
    
def __create_model_histogram(rids, bounding_boxes, label_image, original_image, rang): # 121us with one len(rids) = 1
    """
    Creates a histogram from the voxels of all regions joined together.
    """
    voxels = []
    for rid in rids:
        region_voxels = original_image[bounding_boxes[rid - 1]][label_image[bounding_boxes[rid - 1]] == rid] # 25.8us
        if 0 == len(region_voxels): raise Exception("(__create_model_histogram) failed on region {}".format(rid))
        voxels.extend(region_voxels)
    return numpy.histogram(voxels, bins=__H_SIZE, range=rang, normed=True)[0] # 81.4ms
    
    
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
    # debug line, can be removes
    if 0 != len(set(fg_ids) & set(bg_ids)): raise Exception('Error making fg and bg ground truth distinct.') 
    return fg_ids, bg_ids
    
def __get_images():
    """
    Return all images as pre-processed numpy.ndarrays.
    The label image will be relabeled to start from 1.
    @return original, label, ground-truth-mask, boundary-result-mask, fg-markers, bg-markers
    """
    # images locations
    original_image_n = 'images/original.nii'
    #label_image_n = 'images/label_full.nii' # label image full
    label_image_n = 'images/label_viscous.nii' # label image viscous
    mask_image_n = 'images/mask.nii'
    boundary_result_image_n = 'images/boundary.nii'
    fg_image_n = 'images/fg_markers.nii'
    bg_image_n = 'images/bg_markers.nii'
    
    # load images
    original_image = load(original_image_n)
    label_image = load(label_image_n)
    mask_image = load(mask_image_n)
    boundary_result_image = load(boundary_result_image_n)
    fg_image = load(fg_image_n)
    bg_image = load(bg_image_n)
    
    # extract image data
    original_image_d = scipy.squeeze(original_image.get_data())
    label_image_d = scipy.squeeze(label_image.get_data())
    mask_image_d = scipy.squeeze(mask_image.get_data()).astype(scipy.bool_)
    boundary_result_image_d = scipy.squeeze(boundary_result_image.get_data()).astype(scipy.bool_)
    fg_image_d = scipy.squeeze(fg_image.get_data()).astype(scipy.bool_)
    bg_image_d = scipy.squeeze(bg_image.get_data()).astype(scipy.bool_)
    
    # relabel the label image to start from 1
    label_image_d = filter.relabel(label_image_d, 1)
    
    return original_image_d, label_image_d, mask_image_d, boundary_result_image_d, fg_image_d, bg_image_d


if __name__ == "__main__":
    main()
    
def lS(a, b):
    for y in range(a.shape[1]):
        for x in range(a.shape[0]):
            if x < 1: links = 0
            else: links = b[x-1,y]
    
            if y < 1: oben = 0
            else: oben = b[x,y-1]
      
            if y < 1 or x < 1: obenlinks = 0
            else: obenlinks = b[x-1,y-1]
      
            b[x,y] = a[x,y] + links + oben - obenlinks
