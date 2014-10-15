#!/usr/bin/python

"""
Takes a brain TOF-MRA and looks for occlusions of vessels
"""

#sys.exit([arg])

# build-in modules
import argparse
import logging
import sys

# third-party modules
import numpy as np
from scipy.ndimage import label, binary_dilation, gaussian_filter, generate_binary_structure

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save, header
from medpy.utilities.argparseu import sequenceOfIntegersGe
from numpy.lib.format import dtype_to_descr
from numpy.numarray.numerictypes import UInt16

# information
__author__ = ""
__version__ = ""
__email__ = ""
__status__ = ""
__description__ = """
                  
                  """

# code
def main():
    parser = getParser()
    args = getArguments(parser)

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)

    # load input images
    logger.info('Loading images and preparing data.')
    mra, mra_h = load(args.mra)
    
    if args.dtype: 
        mra = np.asarray(mra, dtype = np.uint16)
        save(mra, args.output, mra_h, args.force)
        sys.exit()
    
    
    print 'hal'
        
    
    
    
    #folgende 5 Zeilen optinal mit vorheriger if Abfrage
    #msk, msk_h = load(args.mask)
    #scl, scl_h = load(args.skeleton)
    #prepare input images
    #scl = scl.astype(numpy.bool)
    #msk = msk.astype(numpy.bool)
    
    
    #branchp = tuple(args.branchp)
    #logger.debug('Seed point identifying the branch to remove is {}.'.format(branchp))

    # check the supplied parameters
    
    #if not (header.get_pixel_spacing(mra_h) == header.get_pixel_spacing(scl_h) == header.get_pixel_spacing(msk_h)):
    #    parser.error('The voxel spacing of the supplied images is not consistent.')
    #if not (mra.shape == scl.shape == msk.shape):
    #    parser.error('The shapes of the supplied images is not consistent.')
    #if not len(branchp) == mra.ndim:
    #    parser.error('The dimensionality of the supplied branch point is not consistent with the dimensionality of the images.')
    #if not numpy.all(map(lambda (x, y): x < y, zip(branchp, mra.shape))):
    #   parser.error('The branch identifiying point lies outside of the images.')
    #if not scl[branchp]:
    #    parser.error('The branch identifying point does not point to a voxel of the skeleton, but the background.')
        
    # detect branch to eliminate
    '''
    logger.info('Identifying the branch to eliminate.')
    nbhs = get_neighbours(scl, branchp)
    logger.debug('Neighbouring points found in skeleton are {}.'.format(nbhs))
    if not len(nbhs) == 2:
        raise Exception('Invalid number of neighbours around branch point: should be 2 but is {}.'.format(len(nbhs)))
    scl[branchp] = False
    labels, x = label(scl, generate_binary_structure(scl.ndim, 3))
    branch_selector = nbhs[0] if args.reverse else nbhs[1]
    logger.debug('Selected neighbour is {}.'.format(branch_selector))
    branch_label = labels[branch_selector]
    branch = branch_label == labels
    logger.debug('Identified branch has total length of {}.'.format(numpy.count_nonzero(branch)))
    
    if args.debug:
        save(branch, "branch.nii.gz", mra_h)
    '''
    # create patch to cover the branch to eliminate

    '''
    # save 
    logger.info('Successfully terminated.')
    save(mra, args.output, mra_h, args.force)
    '''    
    
    
def get_neighbours(image, point):
    """
    Returns a list of all binary neighbour point indices in the image around the supplied
    point (but not the point itself).
    """
    '''
    # extract direct (d^3) neighbourhood
    slicers = []
    for i in point:
        slicers.append(slice(i-1, i+2))
    patch = image[slicers]
    # determine non-zero positions
    positions = numpy.argwhere(patch)
    # correct and collect neighbour positions
    neighbours = []
    for p in positions:
        neighbour = tuple()
        for i, j in zip(p, point):
	        neighbour += (j+i-1,)
        neighbours.append(neighbour)
	# remove the central point itself if present
    if point in neighbours:
        neighbours.remove(point)
        
    return neighbours
	'''        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('mra', help='The original tof-mra image.')
    #parser.add_argument('mask', help='The brain mask.')
    #parser.add_argument('skeleton', help='The thinned/centreline vessel tree.')
    #parser.add_argument('branchp', type=sequenceOfIntegersGe, help='The skeleton point identifying the branch to eliminate, supplied as comma-separated coordinates e.g. x,y,z.')
    #parser.add_argument('radius', type=int, help='The estimated mean radius of the vessel branch to remove.')
    parser.add_argument('output', help='The target file for the created output.')
    parser.add_argument('-d', dest='dtype', action='store_true', help='Control of data type - uint16')
    #parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    #parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    #parser.add_argument('-f', dest='force', action='store_true', help='Overide existing ouput images.')
    return parser    

if __name__ == "__main__":
    main()

