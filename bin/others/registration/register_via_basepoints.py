#!/usr/bin/python

"Register two binary 3D RV volumes via there base-points."

# build-in modules
import argparse
import logging

# third-party modules
import scipy
from scipy.ndimage.morphology import binary_erosion
from scipy.spatial.distance import pdist, squareform

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, header
from medpy.core.exceptions import ArgumentError
from geometry import line_from_points,\
    split_line_to_sections, perpendicular_line, find_nearest, distance,\
    shiftp, angle_between_vectors
import math


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-07-27"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Register two binary 3D RV volumes via there base-points.
                  
                  Prints a 'elastix'/'transformix'-ready transformation to the stdout.
                  
                  Returned transformation is from moving to fixed image.
                  """

# SOME NOTES ON 'ELASTIX'
# 1. 'elastix' performs shifting before rotation!
# 2. 'elastix' works on the real world coordinates (i.e. with voxel spacing of 0)
# 3. for the angle calculation, the voxel spacing is not relevant

# code
def main():
    args = getArguments(getParser())
    
    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # load input images
    data_fixed, header_fixed = load(args.fixed)
    data_moving, header_moving = load(args.moving)
    
    # convert to binary arrays
    data_fixed = data_fixed.astype(scipy.bool_)
    data_moving = data_moving.astype(scipy.bool_)
    
    # check that they are 3D volumes and contain an object
    if not 3 == data_fixed.ndim: raise ArgumentError('The fixed image has {} instead of the expected 3 dimensions.'.format(data_fixed.ndim))
    if not 3 == data_moving.ndim: raise ArgumentError('The moving image has {} instead of the expected 3 dimensions.'.format(data_moving.ndim))
    if not scipy.any(data_fixed): raise ArgumentError('The fixed image contains no binary object.')
    if not scipy.any(data_moving): raise ArgumentError('The moving image contains no binary object.')
    
    # get voxel spacing of fixed image
    fixed_spacing = header.get_pixel_spacing(header_fixed)
    
    # extract the first basal slices form both RV objects
    basal_fixed, basal_fixed_spacing = extract_basal_slice(data_fixed, header_fixed)
    basal_moving, basal_moving_spacing = extract_basal_slice(data_moving, header_moving)
    logger.debug('Extracted basal slices fixed: {} and moving: {} with voxel spacing {} resp. {}.'.format(basal_fixed.shape, basal_moving.shape, basal_fixed_spacing, basal_moving_spacing))
    
    # get points of interest
    fixed_basep, fixed_otherp = get_points_of_interest(basal_fixed)
    moving_basep, moving_otherp = get_points_of_interest(basal_moving)
    logger.debug('Points of interest found are fixed: {} / {} and moving: {} / {}.'.format(fixed_basep, fixed_otherp, moving_basep, moving_otherp))
    
    # translate all points of interest to physical coordinate system
    fixed_basep = [x * y for x, y in zip(fixed_basep, basal_fixed_spacing)]
    fixed_otherp = [x * y for x, y in zip(fixed_otherp, basal_fixed_spacing)]
    moving_basep = [x * y for x, y in zip(moving_basep, basal_moving_spacing)]
    moving_otherp = [x * y for x, y in zip(moving_otherp, basal_moving_spacing)]
    logger.debug('Points of interest translated to real-world coordinates are fixed: {} / {} and moving: {} / {}.'.format(fixed_basep, fixed_otherp, moving_basep, moving_otherp))
    
    # determine shift to unite the two base-points
    shift = (fixed_basep[0] - moving_basep[0], fixed_basep[1] - moving_basep[1])
    logger.debug('Shift to unite base-point is {}.'.format(shift))
    
    # shift the vector end-point of the moving object's vector so that it shares the
    # same base as the fixed vector
    moving_otherp = shiftp(moving_otherp, shift)
    logger.debug('Shifted vector end-point of moving image is {}.'.format(moving_otherp))
    
    # assure correctness of shift
    if not scipy.all([x == y for x, y in zip(fixed_basep, shiftp(moving_basep, shift))]):
        raise ArgumentError('Aligning base-point through shifting failed due to unknown reason: {} does not equal {}.'.format(shiftp(moving_basep, shift), fixed_basep))
    
    # shift both vector end-points to origin base
    fixed_otherp = shiftp(fixed_otherp, [-1. * x for x in fixed_basep])
    moving_otherp = shiftp(moving_otherp, [-1. * x for x in fixed_basep])
    
    # determine angle
    angle = angle_between_vectors(fixed_otherp, moving_otherp)
    logger.debug('Angle set to {} degree in radians.'.format(math.degrees(angle)))
    
    # determine angle turn point
    turn_point = fixed_basep
    logger.debug('Turn point set to {} in real-world coordinates.'.format(turn_point))
    
    # reverse shift to fit into the 'elastix' view
    shift = [-1. * x for x in shift]
    
    # print results
    print('// {}'.format(math.degrees(angle)))
    print("""
//# SOME NOTES ON 'ELASTIX'
//# 1. 'elastix' performs shifting before rotation!
//# 2. 'elastix' works on the real world coordinates (i.e. with voxel spacing of 0)
""")
    print(transform_string(data_fixed.shape,
                           fixed_spacing,
                           [0] + list(shift),
                           [angle, 0, 0],
                           [0] + list(turn_point)))
    
    logger.info("Successfully terminated.")
    
def get_points_of_interest(arr):
    """
    Expects a binary object in the array.
    FInds the two contour points that are the farthest apart, then determines which of
    them is the base point of the RV and returns this first and the other as second
    return value.
    """
    #########
    # 1: Find points in objects contour with the largest distance between them.
    #########
    # extract only outer contour
    arr = arr - binary_erosion(arr)
    
    # extract all positions of the objects contour
    points = scipy.asarray(arr.nonzero()).T
    
    # compute pairwise distances
    distances = squareform(pdist(points, 'euclidean'))
    
    # get positon of largest distance
    position = scipy.unravel_index(scipy.argmax(distances), (len(points), len(points)))
    
    # recompute between which points the largest distance was found
    first = points[position[0]]
    second = points[position[1]]
    
    #logger.debug('Longest distance found between {} and {}.'.format(first, second))
    
    #########
    # 2: Determine which of these is the base point
    #########
    # go along perpendicular lines, find intersections with contours and keep longest only
    intersection = False
    longest_length = 0
    longest_line = line_from_points(first, second)
    segment_points = split_line_to_sections(5, first, second)
    for sp in segment_points:
        sline = perpendicular_line(longest_line, sp)
        nearest = find_nearest(sline, points, 10)
        if distance(nearest[0], nearest[1]) > longest_length:
            longest_length = distance(nearest[0], nearest[1])
            intersection = sp
    
    # determine which of the first two points are nearest to the longest line and return them
    if distance(intersection, first) < distance(intersection, second):
        return (first, second)
    else:
        return (second, first)
    
def extract_basal_slice(arr, head):
    """
    Takes a 3D array, iterates over the first dimension and returns the first 2D plane
    which contains any non-zero values as we as its voxel spacing.
    """
    for plane in arr:
        if scipy.any(plane):
            # get voxel spacing
            spacing = list(header.get_pixel_spacing(head))
            spacing = spacing[1:3]
            # return plane and spacing
            return (plane, spacing)
        
    raise ArgumentError('The supplied array does not contain any object.')
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('fixed', help='The fixed image.')
    parser.add_argument('moving', help='The moving image.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    return parser    

def transform_string(shape, spacing, shift, angles, turn_point):
    """Returns a finished transformation file string."""
    # NOTE:
    # - the transformation file requires real-world coordinates, the points and shifts have therefore to be multiplied with the voxel spacing
    base = """
(Transform "EulerTransform")
(NumberOfParameters 6)
(TransformParameters {xangle:.10f} {yangle:.10f} {zangle:.10f} {xshift:.10f} {yshift:.10f} {zshift:.10f})

(InitialTransformParametersFileName "NoInitialTransform")
(HowToCombineTransforms "Compose")

// Image specific
(FixedImageDimension 3)
(MovingImageDimension 3)
(FixedInternalImagePixelType "float")
(MovingInternalImagePixelType "float")
(Size {xsize:d} {ysize:d} {zsize:d})
(Index 0 0 0)
(Spacing {xspacing:.10f} {yspacing:.10f} {zspacing:.10f})
(Origin 0.0000000000 0.0000000000 0.0000000000)
//(Direction 1.0000000000 0.0000000000 0.0000000000 0.0000000000 1.0000000000 0.0000000000 0.0000000000 0.0000000000 1.0000000000) // !TODO: Compute/read this!
(UseDirectionCosines "true")

// EulerTransform specific
(CenterOfRotationPoint {xturn_point} {yturn_point} {zturn_point})
(ComputeZYX "false")

// ResampleInterpolator specific
(ResampleInterpolator "FinalBSplineInterpolator")
(FinalBSplineInterpolationOrder 0)

// Resampler specific
(Resampler "DefaultResampler")
(DefaultPixelValue 0.000000)
(ResultImageFormat "nii")
(ResultImagePixelType "short")
(CompressResultImage "false")
"""
    shape = list(map(int, shape))
    spacing = list(map(float, spacing))
    angles = list(map(float, angles))
    turn_point = list(map(float, turn_point))
    return base.format(xsize=shape[0], ysize=shape[1], zsize=shape[2],
                       xspacing=spacing[0], yspacing=spacing[1], zspacing=spacing[2],
                       xangle=angles[0], yangle=angles[1], zangle=angles[2],
                       xshift=shift[0], yshift=shift[1], zshift=shift[2],
                       xturn_point=turn_point[0], yturn_point=turn_point[1], zturn_point=turn_point[2])

if __name__ == "__main__":
    main()
