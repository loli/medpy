"""
@package medpy.application.registration.geometry
Some geometrical function that are used in the registration routines.

@author Oskar Maier
@version d0.1.0
@since 2012-07-27
@status Development
"""

# build-in module

# third-party modules
import math

# own modules

# code
def rotate_vector(v, theta):
    """
    Rotates a vector by theta (in radians) around the origin.
    """
    cs = math.cos(theta);
    sn = math.sin(theta);
    
    x = v[0] * cs - v[1] * sn;
    y = v[0] * sn + v[1] * cs;

    return (x, y)

def shiftp(p, s):
    """
    Shift a point by shift.
    """ 
    return [x[0] + x[1] for x in zip(p, s)]

def angle_between_vectors(v1, v2):
    """
    Computes the angle between two vectors with the same base of 0/0/....
    Returns an angle between 0 and 2*pi (in radians).
    Note: 2D version.
    v.x*u.x + v.y*u.y = ||v||*||u|| * cos(theta)
    [ -dot product- ]   [ -length- ]      [ - angle between u and v- ]
    """
    v1 = normalize(v1)
    v2 = normalize(v2)
    angle = math.atan2(v2[1],v2[0]) - math.atan2(v1[1],v1[0])
    
    if angle < 0: return angle + 2 * math.pi # shift negative angle by 360
    else: return angle
    
def dotproduct(v1, v2):
    """
    Compute the dot-product of two vectors.
    """
    return float(sum([x[0] * x[1] for x in zip(v1, v2)]))

def normalize(v):
    """
    Normalize a vector.
    """
    l = length_of_vector(v)
    return [x/l for x in v]

def length_of_vector(v):
    """
    Returns the length of an vector.
    """
    return math.sqrt(dotproduct(v, v))

def angle_between_lines(line1, line2):
    """Compute the angle between two lines."""
        
    print('// {}, {}'.format(line2[0], line1[0]))
        
    if -1 == line1[0] * line2[0]: # special case: lines are perpendicular
        angle = math.radians(90)
    elif line1[0] == 0: # special case: one of the slopes is 0
        angle = math.atan(line2[0])
    elif line2[0] == 0: # special case: one of the slopes is 0
        angle = math.atan(line2[1])   
    else: # normal case
        angle = math.atan((line2[0] - line1[0]) / (1. + line1[0] * line2[0]))
    
    if math.degrees(angle) < 0: return math.radians(180. + math.degrees(angle))
    else: return angle

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

    