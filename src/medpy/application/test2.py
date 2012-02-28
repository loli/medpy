#!/usr/bin/python

#
# COMPUTE MEAN; ENTROPY AND UNIFORMITY
#

# build-in modules

# third-party modules
import scipy
import scipy.stats
import math
from scipy.ndimage.filters import gaussian_laplace, convolve

# path changes

# own modules

# code
def main():
    # set parameters
    img = scipy.asarray([[[1,2,3],
                          [1,2,3],
                          [1,2,3]],
                         [[1,2,3],
                          [1,2,3],
                          [1,2,3]]])
    img = scipy.asarray([[[1,2,3,4],
                          [1,2,3,-6],
                          [1,2,3,4]],
                         [[1,2,3,3],
                          [1,2,3,-9],
                          [1,2,3,2]]])
    mean_exp = 6*6/18.
    entropy_exp = -3 * 1./3 * math.log(1./3, 2)
    uniformity_exp = 3 * math.pow(1./3, 2)
        
    print mean_exp, entropy_exp, uniformity_exp
    print features(img)
    print features2(img.ravel())
    
#    points = [(x, y) for x in range(-4, 5) for y in range(-4, 5)]
#    scipy.set_printoptions(precision=4)
#    scipy.set_printoptions(suppress=True)
#    for sigma in [x/10. + 0.1 for x in range(0, 10)]:
#        res = []
#        for p in points:
#            res.append(LoG2d(p[0], p[1], sigma))
#        res = (scipy.asarray(res)).reshape(9,9)
#        print "SIGMA", sigma
#        print res
    
    img =  [[1,1,1,1,1,1,1],
            [1,2,2,2,2,2,1],
            [1,2,3,3,3,2,1],
            [1,2,3,4,3,2,1],
            [1,2,3,3,3,2,1],
            [1,2,2,2,2,2,1],
            [1,1,1,1,1,1,1]]
    scipy.set_printoptions(precision=4)
    img = scipy.asarray(img)
    points = [(x, y) for x in range(-10, 11) for y in range(-10, 11)]
    res = []
    for p in points:
        res.append(LoG2d(p[0], p[1], 0.5))
    res = (scipy.asarray(res)).reshape(21,21)
    
    img_con = scipy.zeros(img.shape, dtype=scipy.float_)
    convolve(img, res, img_con)
    
    img_log = scipy.zeros(img.shape, dtype=scipy.float_)
    gaussian_laplace(img, 0.5, output=img_log)
    
    print img_con
    print features2(img_con.ravel())
    print img_log
    print features2(img_log.ravel())
    
    
    points = [(x, y) for x in range(-10, 11) for y in range(-10, 11)]
    res = []
    for p in points:
        res.append(LoG2d(p[0], p[1], 1.5))
    res = (scipy.asarray(res)).reshape(21,21)
    
    img_con = scipy.zeros(img.shape, dtype=scipy.float_)
    convolve(img, res, img_con)
    
    img_log = scipy.zeros(img.shape, dtype=scipy.float_)
    gaussian_laplace(img, 1.5, output=img_log)
    
    print img_con
    print features2(img_con.ravel())
    print img_log
    print features2(img_log.ravel())    
    
    
    
    print "All done."
    
def gauss(x, y, sigma):
    return math.exp(-1 * (math.pow(x, 2) + math.pow(x, 2)) / 2 * math.pi * math.pow(sigma, 2))

def laplace(x, y, sigma):
    a = -1. / (math.pi * math.pow(sigma, 4))
    b = 1 - (math.pow(x, 2) + math.pow(y, 2)) / (2 * math.pow(sigma, 2))
    return a * b * gauss(x, y, sigma)

def LoG2d(x, y, sigma):
    xysqr = math.pow(x, 2) + math.pow(y, 2)
    ssqrdbl = -2 * math.pow(sigma, 2)
    term = xysqr/ssqrdbl
    return -1. / (math.pi * math.pow(sigma, 4)) * (1 + term) * math.exp(term)
    
def features(image): # 100^3 in 60-100ms
    """
    Compute the mean, entropy and uniformity of the supplied image.
    @param image an image of integers
    @returns mean, entropy, uniformity as tuple
    """
    mean = image.mean()
    img = image - image.min() # remove eventual negative values
    dist = scipy.bincount(img.ravel())/float(img.size) # compute probability histogram (work only for ints)
    entropy = 0
    uniformity = 0
    for grey_value in scipy.unique(img):
        entropy += dist[grey_value] * math.log(dist[grey_value], 2)
        uniformity += math.pow(dist[grey_value], 2)
    entropy *= -1
    return mean, entropy, uniformity

def features2(voxels): # 100^3 in 60-100ms
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

def features3(voxels): # 100^3 in 60-100ms
    """
    Compute the mean, entropy and uniformity of the supplied image.
    @param image as an 1D array of voxels
    @returns mean, entropy, uniformity as tuple
    """
    mean = voxels.mean()
    grey_values = scipy.unique(voxels)
    voxels = voxels.tolist()
    l = float(len(voxels))
    entropy = 0
    uniformity = 0
    for grey_value in grey_values:
        p = voxels.count(grey_value) / l
        entropy += p * math.log(p, 2)
        uniformity += math.pow(p, 2)
    entropy *= -1
    return mean, entropy, uniformity
    
if __name__ == "__main__":
    main()     
    
    