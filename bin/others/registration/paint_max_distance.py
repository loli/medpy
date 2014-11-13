#!/usr/bin/python

"Computes max distance and paints it into the basal slice."

# build-in modules
import argparse
import logging

# third-party modules
import scipy

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, header
from scipy.ndimage.morphology import binary_erosion
from scipy.spatial.distance import pdist, squareform
import math


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-05-25"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Computes max distance and paints it into the basal slice.
                  
                  Returned transformation is from moving to fixed image.
                  """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # load input images
    data_fixed, header_fixed = load(args.fixed)
    data_moving, _ = load(args.moving)
    
    # get points of interest
    fixed_basep, fixed_otherp = get_points_of_interest(data_fixed)
    moving_basep, moving_otherp = get_points_of_interest(data_moving)
    
    # get voxel spacing
    spacing = header.get_pixel_spacing(header_fixed)
    
    # determine shift
    shift = (moving_basep[0] - fixed_basep[0], moving_basep[1] - fixed_basep[1])
    shift = (shift[0] * spacing[0], shift[1] * spacing[1])
    
    # determine angle
    angle = angle_between_lines(line_from_points(fixed_basep, fixed_otherp),
                                line_from_points(moving_basep, moving_otherp))
    
    # determine angle turn point
    turn_point = fixed_basep
    turn_point = (turn_point[0] * spacing[0], turn_point[1] * spacing[1])
    
    # print results
    print('//angle: {}'.format(math.degrees(angle)))
    print(transform_string(shift, angle, turn_point))
    
    # paint in the points and other stuff
    #data_input[tuple(fixed_basep)] = 2
    #data_input[tuple(fixed_otherp)] = 3
    
    # save image
    #save(data_input, args.output, header_input, args.force)
    
    logger.info("Successfully terminated.")

def get_points_of_interest(arr):
    """Returns the base and the reverse points of the shape in arr in that order."""
    arr = arr.copy()
    
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
    

def angle_between_lines(line1, line2):
    """Compute the angle between two lines."""
    if line2[0] > line1[0]: obtuse = False
    else:
        obtuse = True
        tmp = line2
        line2 = line1
        line1 = tmp
        
    if -1 == line1[0] * line2[0]: # special case: lines are perpendicular
        angle = math.radians(90)
    elif line1[0] == 0: # special case: one of the slopes is 0
        angle = math.atan(math.fabs(line2[0]))
    elif line2[0] == 0: # special case: one of the slopes is 0
        angle = math.atan(math.fabs(line2[1]))    
    else: # normal case
        angle = math.atan(math.fabs((line2[0] - line1[0]) / (1. + line1[0] * line2[0])))
    
    if obtuse: return math.radians(180.) - angle
    else: return angle

def paint_line_2d(arr, _from, _to, colour):
    arr[tuple(_from)] = colour
    arr[tuple(_to)] = colour
    coords = __get_hole_coordinates(_from[0], _from[1], _to[0], _to[1])
    for coord in coords:
        arr[coord] = colour
        
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

def find_nearest(line, points, mindist):
    """Finds the two points in points nearest to line which have a minimal distance of mindist to each other."""
    # first turn -> find nearest point
    nearest_dist = 100000000000
    nearest = False
    for point in points:
        pline = perpendicular_line(line, point)
        intersection = line_intersection(line, pline)
        dist = distance(intersection, point)
        if dist < nearest_dist:
            nearest_dist = dist
            nearest = point
            
    # second turn -> find nearest with minbimal distance of mindist to first
    nearest2_dist = 1000000000000
    nearest2 = False
    for point in points:
        pline = perpendicular_line(line, point)
        intersection = line_intersection(line, pline)
        dist = distance(intersection, point)
        if dist < nearest2_dist and distance(point, nearest) >= mindist:
            nearest2_dist = dist
            nearest2 = point
        
    return (nearest, nearest2)
        
def line_intersection(line1, line2):
    """Computes the intersection point between two lines."""
    x = (line2[1] - line1[1])/float(line1[0] - line2[0])
    y = line1[0] * x + line1[1]
    return (x, y)
    
    
def split_line_to_sections(dist, start, stop):
    """Splits line between start and stop into parts of distance dist and returns their points."""
    # !Note: Very rough and unreliable
    line = line_from_points(start, stop)
    line_length = distance(start, stop)
    segments = int(line_length / dist)
    
    points = [start]
    x_step = (stop[0] - start[0]) / float(segments)
    for i in range(segments - 1):
        x = start[0] + x_step * (i + 1)
        y = line[0] * x + line[1]
        points.append((x, y))
        
    points.append(stop)
    
    return points
    
def distance(p1, p2):
    """Euclidean distance between two points."""
    return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))
    
def perpendicular_line(inline, p):
    """Computes the line perpendicular to inline going through point p."""
    m = -1 * 1./inline[0]
    b = p[1] - p[0] * m
    return (m, b)
    
def line_from_points(p1, p2):
    """Compute the the line going through two points."""
    m = (p2[1] - p1[1]) / float(p2[0]- p1[0])
    b = p1[1] - p1[0] * m
    return (m, b)

def transform_string(shift, angle, turn_point):
    """Returns a finished transformation file string."""
    # NOTE:
    # - the transformation file requires real-world coordinates, the points and shifts have therefore to be multiplied with the voxel spacing
    base = """
(Transform "EulerTransform")
(NumberOfParameters 6)
(TransformParameters {xangle} 0 0 0 {yshift} {zshift}) // xangle, yangle, zangle, xshift, yshift, zshift
//(TransformParameters {xangle} 0 0 -1 0 0) // xangle, yangle, zangle, xshift, yshift, zshift

(InitialTransformParametersFileName "NoInitialTransform")
(HowToCombineTransforms "Compose")

// Image specific
(FixedImageDimension 3)
(MovingImageDimension 3)
(FixedInternalImagePixelType "float")
(MovingInternalImagePixelType "float")
(Size 14 216 256) // !TODO: Compute/read this!
(Index 0 0 0)
(Spacing 7.0000000000 0.9111617208 0.9111617208) // !TODO: Compute/read this!
(Origin 0.0000000000 0.0000000000 0.0000000000) // !TODO: Compute/read this!
(Direction 1.0000000000 0.0000000000 0.0000000000 0.0000000000 1.0000000000 0.0000000000 0.0000000000 0.0000000000 1.0000000000) // !TODO: Compute/read this!
(UseDirectionCosines "true")

// EulerTransform specific
//(CenterOfRotationPoint 45.5000000000 114.0474351984 130.5224840241)
(CenterOfRotationPoint 0.0 {yturn_point} {zturn_point}) // x y z
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
    
    return base.format(xangle=angle, yshift=shift[0], zshift=shift[1], yturn_point=turn_point[0], zturn_point=turn_point[1])
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('fixed')
    parser.add_argument('moving')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser    

if __name__ == "__main__":
    main()
       