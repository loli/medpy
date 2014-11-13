#!/usr/bin/python

from medpy.core import Logger
import logging
import scipy
from nibabel.loadsave import load
from scipy import ndimage

def main():
    # prepare logger
    logger = Logger.getInstance()
    logger.setLevel(logging.DEBUG)
    
    # all rings are at slice z = 98
    ring_closed = scipy.squeeze(load('ring_closed.nii').get_data()).astype(scipy.bool_)[:,:,98]
    ring_closed_w1hole = scipy.squeeze(load('ring_closed_w1hole.nii').get_data()).astype(scipy.bool_)[:,:,98]
    ring_closed_wholes = scipy.squeeze(load('ring_closed_wholes.nii').get_data()).astype(scipy.bool_)[:,:,98]
    ring_open = scipy.squeeze(load('ring_open.nii').get_data()).astype(scipy.bool_)[:,:,98]
    ring_open_w1hole = scipy.squeeze(load('ring_open_w1hole.nii').get_data()).astype(scipy.bool_)[:,:,98]
    ring_open_wholes = scipy.squeeze(load('ring_open_wholes.nii').get_data()).astype(scipy.bool_)[:,:,98]
    ring_difficult = scipy.squeeze(load('ring_difficult.nii').get_data()).astype(scipy.bool_)[:,:,98]
    ring_difficult_w1hole = scipy.squeeze(load('ring_difficult_w1hole.nii').get_data()).astype(scipy.bool_)[:,:,98]
    
    # algorithm
    print('ring_closed', alg(ring_closed), alg2(ring_closed))
    print('ring_closed_w1hole', alg(ring_closed_w1hole), alg2(ring_closed_w1hole))
    print('ring_closed_wholes', alg(ring_closed_wholes), alg2(ring_closed_wholes))
    print('ring_open', alg(ring_open), alg2(ring_open))
    print('ring_open_w1hole', alg(ring_open_w1hole), alg2(ring_open_w1hole))
    print('ring_open_wholes', alg(ring_open_wholes), alg2(ring_open_wholes))
    print('ring_difficult', alg(ring_difficult), alg2(ring_difficult))
    print('ring_difficult_w1hole', alg(ring_difficult_w1hole), alg2(ring_difficult_w1hole))
    
def extract_holes(ring):
    """
    Check if an object in an image forms a ring with one single hole.
    
    @note if the number of holes equals 1, the supplied objects is either a ring (in 2D)
    or another shape with a single hole somewhere (low probability). If the number of 
    holes equals 0, the supplied object is of a shape containing no holes (e.g. an not
    completely closed ring). If the number is higher than 1, the object contains multiple
    holes. 
    
    @param ring a 2D array of type bool_ containing a single object 
    @type ring ndarray
    @return an 2D array containing all holes labeled consecutively from 1 as first and
            the number of found holes as second arguments 
    @rtype (ndarray, int)
    """
    # fill the holes in the binary array (using ndim*2 connectedness) and xor with original image
    holes = scipy.logical_xor(ring, ndimage.binary_fill_holes(ring))
    # find all objects (= holes in the original object) in the image
    return ndimage.measurements.label(holes)
    
# !!!!!!!!!! The above function is a combination of the following two !!!!!!!!!!
def alg(ring):
    # fill holes in binary objects and then see if anything got filled
    xor = scipy.logical_xor(ring, ndimage.binary_fill_holes(ring))
    if xor.any():
        return True
    else:
        return False
    
def alg2(ring):
    # fill holes in binary objects
    filled = ndimage.binary_fill_holes(ring)    
    # substract original image with object \w holes from the filled-holes image to obtain holes only
    holes = scipy.logical_xor(ring, filled)
    # label all objects in the image to obtain the number of holes
    _, hole_count = ndimage.measurements.label(holes)
    
    return hole_count
    
if __name__ == "__main__":
    main()