"""
@package medpy.features.texture
Run-time optimized features extraction on images.

Functions:
    - def boundary_stawiaski(label_image, (gradient_image)): boundary term implementation in (1)


@author Oskar Maier
@version d0.1.0
@since 2012-02-16
@status Development
"""

# build-in module

# third-party modules
import math
import scipy
from scipy.ndimage.filters import generic_filter
import time
import itertools

# own modules

# code
def tamura(img, k, features = (True, True, True)):
    coa = coarseness(img, k) if features[0] else False
    con = contrast(img) if features[1] else False
    dir = directionality(img) if features[2] else False
    return coa, con, dir

def coarseness(img, k):
    # compute average over all 0,..,k-1 regions of side-length 2^k-1
    A = __coarsness_average(img, k)

    # compute differences between pairs of non-overlapping neighbourhoods
    E = scipy.zeros([img.ndim] + list(A.shape), dtype=scipy.float_) # matrix holding computed differences in all directions

    for dim in range(img.ndim):
        for nbh in range(k):
            shape = img.ndim * [1]
            shape[dim] = 2 * int(math.pow(2, nbh)) + 1
            footprint = scipy.zeros(shape, dtype=scipy.bool_)
            idx = img.ndim * [0]
            footprint[tuple(idx)] = 1
            idx[dim] = -1
            footprint[tuple(idx)] = 1
            generic_filter(A[nbh], lambda x: abs(x[0]- x[1]), output=E[dim][nbh], footprint=footprint, mode='mirror')
            
    # compute for each voxel the k value, that lead to the highest E (regardless in which direction)
    S = scipy.zeros_like(img)

    for x in range(S.shape[0]):
        for y in range(S.shape[1]):
            for z in range(S.shape[2]):
                maxv = 0 
                maxk = 0
                for dim in range(img.ndim):
                    for nbh in range(k):
                        if E[dim][nbh][x,y,z] > maxv:
                            maxv = E[dim][nbh][x,y,z]
                            maxk = nbh
                S[x,y,z] = maxk
    
    return S

def __coarsness_average(img, k):
    if any([dim < math.pow(2, k - 1) for dim in img.shape]): raise ValueError('k value to big for image size')
    rt = running_total3d(img)
    A = scipy.zeros([k] + list(img.shape), dtype=scipy.float_) # matrix holding computed averages
    for k in range(1, k + 1):
        offset = int(math.pow(2, k - 1) / 2)
        s0 = 0 if 2 > k else offset
        s1 = 0 if 2 > k else offset - 1
        for x in range(img.shape[0])[s0:None if 0 == s1 else -s1]:
            for y in range(img.shape[1])[s0:None if 0 == s1 else -s1]:
                for z in range(img.shape[2])[s0:None if 0 == s1 else -s1]:
                    A[k-1][x,y,z] = efficient_local_avg3d(rt, ((x-s0, y-s0, z-s0), (x+s1, y+s1, z+s1)))
                    #print ((x-s0, y-s0, z-s0), (x+s1, y+s1, z+s1)), A[k-1][x,y,z]

    return A

def contrast(img):
    return False

def directionality(img):
    return False

def efficient_local_avg(rt, (p_min, p_max), divider = False):
    """
    Compute the average intensity over an arbitrary rectangular region of an image from
    its running total image (generated with @see running_total()).
    
    Together with @see running_total this functions provides a very efficient way to
    compute many average intensities over nD images.
    
    @param rt The running total image created by @see running_total().
    @type rt numpy.ndarray
    @param p_min The 'lower left' (included) corner of the rectangular region over which
                 to compute the average intensity.
    @param p_min sequence
    @param p_max The 'upper right' (included) corner of the rectangular region over which
                 to compute the average intensity.
    @param p_max sequence
    @param divider If a divider is provide, this is used instead of the regions size to
                   divide the intensity sum over the region. Use this if you process 
                   irregular image that have been zero-padded.
    @type divider float 
    
    @return The average intensity over the region.
    @rtype float
    
    Theoretical background of extracting the mean value:
    """
    # prepare and check parameters
    try:
        p_min = scipy.array(p_min)
        p_max = scipy.array(p_max)
    except Exception: raise TypeError('p_min and p_max must be valid sequences')
    if not rt.ndim == len(p_min): raise ValueError('p_min entries must equal the dimensionality of rt')
    if not rt.ndim == len(p_max): raise ValueError('p_max entries must equal the dimensionality of rt')
    if not all([dim >= 3 for dim in rt.shape]): raise ValueError('all dimensions of rt must be >= 3')
    if not divider:
        divider = float(scipy.prod(p_max + 1 - p_min))
    else:
        try: divider = float(divider)
        except Exception: raise TypeError('divider must be a float')
    if any([idx >= dim for idx, dim in zip(p_min, rt.shape)]): raise ValueError('p_min point out of rt')
    if any([idx >= dim for idx, dim in zip(p_max, rt.shape)]): raise ValueError('p_max point out of rt')
    

    # compute and return average 2^ndim accesses to rt 
    avgsum = 0
    for comb in itertools.product([True, False], repeat=rt.ndim):
        idx = [p_min[dim] - 1 if comb[dim] else p_max[dim] for dim in range(len(comb))]
        if sorted(idx)[0] < 0: continue
        #print idx, "+ if " if 0 == comb.count(True) % 2 else "-"
        if 0 == comb.count(True) % 2: # even
            avgsum += rt[tuple(idx)]
        else: # odd
            avgsum -= rt[tuple(idx)] 

    return avgsum / divider

def efficient_local_avg3d(rt, (p_min, p_max), divider = False):
    """
    Faster version of efficient_local_avg for 3d only.
    """
    # prepare parameters
    p_min = list(p_min)
    p_max = list(p_max)
    if not divider: divider = float(scipy.prod([x + 1 - y for x, y in zip(p_max, p_min)]))

    # compute and return average 2^ndim accesses to rt 
    o = rt[tuple(p_max)]
    m0 = rt[p_min[0] - 1, p_max[1], p_max[2]] if p_min[0] != 0 else 0
    m1 = rt[p_max[0], p_min[1] - 1, p_max[2]] if p_min[1] != 0 else 0
    m2 = rt[p_max[0], p_max[1], p_min[2] - 1] if p_min[2] != 0 else 0
    m3 = rt[p_min[0] - 1, p_min[1] - 1, p_min[2] - 1] if p_min[0] != 0 and p_min[1] != 0 and p_min[2] != 0 else 0
    p0 = rt[p_min[0] - 1, p_min[1] - 1, p_max[2]] if p_min[0] != 0 and p_min[1] != 0 else 0
    p1 = rt[p_min[0] - 1, p_max[1], p_min[2] - 1] if p_min[0] != 0 and p_min[2] != 0 else 0
    p2 = rt[p_max[0], p_min[1] - 1, p_min[2] - 1] if p_min[1] != 0 and p_min[2] != 0 else 0
    
    return (o + p0 + p1 + p2 - m0 - m1 - m2 - m3) / divider

def running_total(image): # 2.5s for 50^3 image
    """
    Compute the running total of an nD image.
    
    The running total of an images intensity values can, in conjunction with the
    @see efficient_local_avg() be used to efficiently compute the average intensity
    values of many image regions.
    
    @param image the image over which to compute the running sum
    @type image numpy.ndarray 
    @return an image containing the running sum at each voxel
    @rtype numpy.ndarray
    
    After computing the running total of an image, computing the average intensity value
    of any arbitrary rectangular regions of the nD image can be computed with only 2^D
    calls to the running total image.
    
    Computing the running total is performed over a 2^D neighbourhood and has to be
    executed only once. Hence using the running total saves significant computation
    times when the average intensity value has to be computed over many and especially
    large regions.
    
    @note if you want to apply the running total to a non-rectangular image, simply padd
    all free voxels with zeros.
    
    Theoretical background of computing the running total:  
    """
    # prepare and check parameters
    try: rt = scipy.asarray(image).copy()
    except Exception: raise TypeError('image must be an array_like object')
    if not all([dim >= 3 for dim in rt.shape]): raise ValueError('all dimensions of image must be >= 3')
    
    #footprint = scipy.ones(image.ndim * [2])
    for point in itertools.product(*[range(dim) for dim in rt.shape], repeat=1):
        total = 0
        #print "Point", point
        for comb in itertools.product([True, False], repeat=rt.ndim):
            
            idx = [point[dim] - 1 if comb[dim] else point[dim] for dim in range(len(comb))]
            if sorted(idx)[0] < 0: continue
            #print "Comb", comb, "-" if 0 == comb.count(True) % 2 and any(comb) else "+", "idx", idx, "=", rt[tuple(idx)]
            if 0 == comb.count(True) % 2 and any(comb): # even and any True (second condition since point itself (x,y,...) must be added, not substracted)
                total -= rt[tuple(idx)]
            else: # odd
                total += rt[tuple(idx)]
        #print "Setting", point, "to", total
        rt[point] = total
             
    return rt

def running_total3d(image): # 3.42s for 100^3 image
    """
    Faster version of @see running_total() for 3D images only.
    """
    # prepare and check parameters
    try: rt = scipy.asarray(image).copy()
    except Exception: raise TypeError('image must be an array_like object')
    if not all([dim >= 3 for dim in rt.shape]): raise ValueError('all dimensions of image must be >= 3')
    
    for x in range(image.shape[0]):
        for y in range(image.shape[1]):
            for z in range(image.shape[2]):
                p0 = rt[x-1,y,z] if x > 0 else 0
                p1 = rt[x,y-1,z] if y > 0 else 0
                p2 = rt[x,y,z-1] if z > 0 else 0
                p3 = rt[x-1,y-1,z-1] if x > 0 and y > 0 and z > 0 else 0
                m1 = rt[x-1,y-1,z] if x > 0 and y > 0 else 0
                m2 = rt[x-1,y,z-1] if x > 0 and z > 0 else 0
                m3 = rt[x,y-1,z-1] if y > 0 and z > 0 else 0
                rt[x,y,z] += p0 + p1 + p2 + p3 - m1 - m2 - m3
    return rt

#def running_total3d2(image):
#    rt = scipy.asarray(image).copy()
#    
#    ip0 = scipy.concatenate((scipy.zeros(rt[0:1].shape), rt[:-1]), axis=0)
#    ip1 = scipy.concatenate((scipy.zeros(rt[:,0:1].shape), rt[:,:-1]), axis=1)
#    ip2 = scipy.concatenate((scipy.zeros(rt[:,:,0:1].shape), rt[:,:,:-1]), axis=2)
#    
#    ip3 = scipy.concatenate((scipy.zeros(rt[0:1].shape), rt[:-1]), axis=0)
#    ip3 = scipy.concatenate((scipy.zeros(ip3[:,0:1].shape), ip3[:,:-1]), axis=1)
#    ip3 = scipy.concatenate((scipy.zeros(ip3[:,:,0:1].shape), ip3[:,:,:-1]), axis=2)
#    
#    im1 = scipy.concatenate((scipy.zeros(rt[0:1].shape), rt[:-1]), axis=0)
#    im1 = scipy.concatenate((scipy.zeros(im1[:,0:1].shape), im1[:,:-1]), axis=1)
#    
#    im2 = scipy.concatenate((scipy.zeros(rt[0:1].shape), rt[:-1]), axis=0)
#    im2 = scipy.concatenate((scipy.zeros(im2[:,:,0:1].shape), im2[:,:,:-1]), axis=2)
#    
#    im3 = scipy.concatenate((scipy.zeros(rt[:,0:1].shape), rt[:,:-1]), axis=1)
#    im3 = scipy.concatenate((scipy.zeros(im3[:,:,0:1].shape), im3[:,:,:-1]), axis=2)
#
#    rtr = rt.ravel()
#    for oidx, p0, p1, p2, p3, m1, m2, m3 in zip(range(len(rtr)), ip0.flat, ip1.flat, ip2.flat, ip3.flat, im1.flat, im2.flat, im3.flat):
#        rtr[oidx] += p0 + p1 + p2 + p3 - m1 - m2 - m3
#        
#    return rt

# input array
[[[2, 1, 1],
  [3, 2, 1],
  [1, 1, 2]],
 [[2, 3, 2],
  [1, 2, 3],
  [2, 1, 2]],
 [[3, 2, 1],
  [1, 2, 2],
  [3, 2, 1]]]
