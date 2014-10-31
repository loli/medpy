# Copyright (C) 2013 Oskar Maier
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Oskar Maier, Alexander Ruesch (in internship)
# version r0.3.3
# since 2013-08-24
# status Release

# build-in modules

# third-party modules
import numpy
from scipy.ndimage.filters import uniform_filter, sobel, maximum_filter, minimum_filter, gaussian_filter
from scipy import stats
from math import factorial
import unittest

# own modules

# constants

def coarseness(image, voxelspacing = None, mask = slice(None)):
    r"""
    Takes a simple or multi-spectral image and returns the coarseness of the texture.
    
    Step1:  At each pixel, compute six averages for the windows of size 2**k x 2**k,
            k=0,1,...,5, around the pixel. 
    Step2:  At each pixel, compute absolute differences E between the pairs of non 
            overlapping averages in every directions.
    step3:  At each pixel, find the value of k that maximises the difference Ek in either 
            direction and set the best size Sbest=2**k
    step4:  Compute the coarseness feature Fcrs by averaging Sbest over the entire image.

    Parameters
    ----------
    image : array_like or list/tuple of array_like 
        A single image or a list/tuple of images (for multi-spectral case).
    voxelspacing : sequence of floats
        The side-length of each voxel.
    mask : array_like
        A binary mask for the image or a slice object

    Returns
    -------
    coarseness : float
        The size of coarseness of the given texture. It is basically the size of
        repeating elements in the image. 
        
    See Also
    --------
    
    
    """
    # Step1:  At each pixel (x,y), compute six averages for the windows
    # of size 2**k x 2**k, k=0,1,...,5, around the pixel.

    image = numpy.asarray(image, dtype=numpy.float32)
   
  
    # set default mask or apply given mask
    if not type(mask) is slice:
        mask = numpy.array(mask, copy=False, dtype = numpy.bool)
    image = image[mask]
      
    # set default voxel spacing if not suppliec
    if None == voxelspacing:
        voxelspacing = tuple([1.] * image.ndim)
    
    # set padding for image border control

    padSize = tuple((numpy.rint((2**5.0) * voxelspacing[jj]),0) for jj in xrange(image.ndim))        
    Apad = numpy.pad(image,pad_width=padSize, mode='reflect') # +1 to append 32 not 31. 

    # Allocate memory
    E = numpy.empty((6,image.ndim)+image.shape)

    # prepare some slicer 
    rawSlicer           = [slice(None)] * image.ndim
    slicerForImageInPad = [slice(padSize[d][0],None)for d in xrange(image.ndim)]

    for k in xrange(6):

        size_vs = tuple(numpy.rint((2**k) * voxelspacing[jj]) for jj in xrange(image.ndim))
        A = uniform_filter(Apad, size = size_vs, mode = 'mirror')

        # Step2: At each pixel, compute absolute differences E(x,y) between 
        # the pairs of non overlapping averages in the horizontal and vertical directions.
        for d in xrange(image.ndim):
            borders = numpy.rint((2**k) * voxelspacing[d])
            
            slicerPad_k_d   = slicerForImageInPad[:]
            slicerPad_k_d[d]= slice((padSize[d][0]-borders if borders < padSize[d][0] else 0),None)
            A_k_d           = A[slicerPad_k_d]

            AslicerL        = rawSlicer[:]
            AslicerL[d]     = slice(0, -borders)
            
            AslicerR        = rawSlicer[:]
            AslicerR[d]     = slice(borders, None)

            E[k,d,...] = numpy.abs(A_k_d[AslicerL] - A_k_d[AslicerR])

    # step3: At each pixel, find the value of k that maximises the difference Ek(x,y)
    # in either direction and set the best size Sbest(x,y)=2**k
    
    k_max = E.max(1).argmax(0)
    dim = E.argmax(1)
    dim_vox_space = numpy.asarray([voxelspacing[dim[k_max.flat[i]].flat[i]] for i in xrange(k_max.size)]).reshape(k_max.shape) 
    S = (2**k_max) * dim_vox_space

    # step4: Compute the coarseness feature Fcrs by averaging Sbest(x,y) over the entire image.
    return S.mean()

def contrast(image, mask = slice(None)):
    r"""
    Takes a simple or multi-spectral image and returns the contrast of the texture.
    
    Fcon = standard_deviation(gray_value) / (kurtosis(gray_value)**0.25)
    

    Parameters
    ----------
    image : array_like or list/tuple of array_like 
        A single image or a list/tuple of images (for multi-spectral case).
    mask : array_like
        A binary mask for the image or a slice object
    Returns
    -------
    contrast : float
        High differences in gray value distribution is represented in a high contrast value. 
        
    See Also
    --------
    
    
    """
    image = numpy.asarray(image)
    
    # set default mask or apply given mask
    if not type(mask) is slice:
        mask = numpy.array(mask, copy=False, dtype = numpy.bool)
    image = image[mask]
    
    standard_deviation = numpy.std(image)
    kurtosis = stats.kurtosis(image, axis=None, bias=True, fisher=False)
    n = 0.25 # The value n=0.25 is recommended as the best for discriminating the textures.  
    
    Fcon = standard_deviation / (kurtosis**n) 
    
    return Fcon

def directionality(image, voxelspacing = None, mask = slice(None),min_distance = 4):
    r"""
    
    

    Parameters
    ----------
    image : array_like or list/tuple of array_like 
        A single image or a list/tuple of images (for multi-spectral case).
    voxelspacing : sequence of floats
        The side-length of each voxel.
    mask : array_like
        A binary mask for the image or a slice object
    min_distance : int
        minimal Distance between 2 local minima or maxima in the histogram

    Returns
    -------
    directionality : array
        Returns the directionality of an image in relation to one special image layer.
        The returned values are sorted like this. The axis are named v,w,x,y,z
        for a five dimensional image:
                                    w   x   y   z   v     x   y   z   v   w
        arctan(delta)| delta =    ---,---,---,---,---,  ---,---,---,---,---
                                    v   w   x   y   z     v   w   x   y   z
        There are always n choose k axis relations; n=image.ndim, k=2 (2 axis in every image layer).
        
    See Also
    --------
    
    
    """
    image = numpy.asarray(image)
    ndim = image.ndim
    # set default mask or apply given mask
    if not type(mask) is slice:
        mask = numpy.array(mask, copy=False, dtype = numpy.bool)
    image = image[mask]
   
    # Allocate memory, define constants
    E = numpy.empty((ndim,) + image.shape)
    
        
    # set default voxel spacing if not suppliec
    if None == voxelspacing:
        voxelspacing = tuple([1.] * ndim)
        

    
    for i in range(ndim):
        E[i,...] = numpy.abs(sobel(image,axis = i))
    # The edge strength e(x,y) is not used at all but nice to have
    # e = uniform_filter(E, size = 3)
    
    n = (factorial(ndim)/(2*factorial(ndim-2))) # number of combinations
    Fdir = numpy.empty(n)
    r=1.0 / (numpy.pi**2)
    
    for i in range(n):
        A = numpy.arctan((E[(i + (ndim+i)/ndim) % ndim,...]) / (E[i%ndim,...]+numpy.spacing(1)))#+numpy.pi/2.0
        
        # Calculate number of bins for the histogram. Watch out, this is just a work around! 
        # @TODO: Write a more stable code to prevent for minimum and maximum repetition when the same value in the Histogram appears multiple times in a row. Example: image = numpy.zeros([10,10]), image[:,::3] = 1
        bins = numpy.unique(A).size + min_distance
        
        
        H = numpy.histogram(A, bins = bins, density=True)[0];
        print H
        H_peaks, H_valleys, H_range = find_valley_range(H)
        summe = 0.0
        for idx_ap in range(len(H_peaks)):
            for range_idx in range( H_valleys[idx_ap], H_valleys[idx_ap]+H_range[idx_ap]):
                a=range_idx % len(H)
                summe += ((numpy.pi*a)/bins - (numpy.pi * H_peaks[idx_ap])/bins) **2 * H[a]
        Fdir[i] = r * summe
        
    return Fdir


def local_maxima(vector,min_distance = 4, mode = "wrap"):
    """
    Internal finder for local maxima .
    Returns UNSORTED indices of maxima in input vector.
    """
    #PROBLEM: detects the local minimum within a range of 4 elements-> vector.size/4 maxima even when there is'nt a maximum.
    fits        = gaussian_filter(numpy.asarray(vector,dtype=numpy.float32),1.0)
    maxfits     = maximum_filter(fits, size=min_distance, mode = mode)
    maxima_mask = fits == maxfits
    maximum     = numpy.transpose(maxima_mask.nonzero())
    return numpy.asarray(maximum)
#     tempMax  = 0
#     tempID = None
#     rangeObserver = 0
#     peak = []
#     vector[vector<1e-5] = 0
#     for i in xrange(len(vector)):
#         if vector[i] > tempMax:
#             tempMax = vector[i]
#             tempID = i
#             rangeObserver = 0
#         else:
#             rangeObserver +=1
#         if rangeObserver == min_distance:
#             peak += [tempID]
#             tempMax = 0
#      
#     return peak

def local_minima(vector,min_distance = 4, mode = "wrap"):
    """
    Internal finder for local minima .
    Returns UNSORTED indices of minima in input vector.
    """
    fits = gaussian_filter(numpy.asarray(vector,dtype=numpy.float32),1.0)
    minfits = minimum_filter(fits, size=min_distance, mode = mode)
    minima_mask = fits == minfits
    minima = numpy.transpose(minima_mask.nonzero())
    return numpy.asarray(minima)

def find_valley_range(vector, min_distance = 4):
    """
    Internal finder peaks and valley ranges.
    Returns UNSORTED indices of maxima in input vector.
    Returns range of valleys before and after maximum
    """
    
    # http://users.monash.edu.au/~dengs/resource/papers/icme08.pdf
    # find min and max with mode = wrap
    mode = "wrap"
    minima = local_minima(vector,min_distance,mode)
    maxima = local_maxima(vector,min_distance,mode)
    # make sure to have 2 valleys for every peak --> len(minima) = len(maxima)+1
    #     n = len(maxima) - len(minima) 
    #     if n == 1:
    #         minima = numpy.asarray([0]+list(minima)+[len(vector)])
    #     elif n == 0:
    #         if minima[0] < maxima[0]:
    #             minima = numpy.asarray(list(minima) + [len(vector)])
    #         else:
    #             minima = numpy.asarray([0] + list(minima))
    #     valley_range = numpy.asarray([minima[ii+1] - minima[ii] for ii in xrange(len(maxima))])
    
    if len(maxima)==len(minima):
        valley_range = numpy.asarray([minima[ii+1] - minima[ii] for ii in xrange(len(minima)-1)] + [len(vector)-minima[-1]+minima[0]])
        if minima[0] < maxima[0]:
            minima = numpy.asarray(list(minima) + [minima[0]])
        else:
            minima = numpy.asarray(list(minima) + [minima[-1]])
        # minima = numpy.asarray(list(minima)+ list(minima[-1]))
        # valley_range = valley_range + [len(vector)-minima[-1]+minima[0]])
    else:
        valley_range = numpy.asarray([minima[ii+1] - minima[ii] for ii in xrange(len(maxima))])
    return maxima, minima, valley_range

    
class TestSequenceFunctions(unittest.TestCase):
    
    def setUp(self):
        print "Run setup... ",
        self.d=numpy.zeros([100,100,100])
        self.d[:,:,::3] = 1
        self.voxelspacing = (1.0, 2.0, 2.0)
        
        print "done."
    
    def test_Coarseness(self):
        print "test_Coarseness()... "
        print "    Fcrs = " + str(coarseness(self.d))
        print "    Fcrs = " + str(coarseness(self.d, voxelspacing=self.voxelspacing))
        print "test_Coarseness()... done."
         
#     def test_Contrast(self):
#         print "test_Contrast()... "
#         print "    Fcon = " + str(contrast(self.d))
#         print "test_Contrast()... done."
#
#     def test_Directionality(self):
#         print "test_Directionality()... "
#         print "    Fdir = " + str(directionality(self.d)) 
#         
#         print "test_Directionality()... done... nothing"

    #def test_find_valley_range(self):
    
if __name__ == '__main__':
    unittest.main()
        
# 
# 
#     padSize = (2**(tuple(numpy.rint([ii * 5.0 + 1 for ii in voxelspacing])))[jj] for jj in xrange(image.ndim))
#     Apad = pad(image,size=padSize, mode=mode,cval=cval) # +1 to append 32 not 31. 
#     
#     for k in xrange(6):
#         #print "Step1"
#         k_vs = tuple(numpy.rint([ii * k for ii in voxelspacing]))
#         size_vs = (2**k_vs[ii] for ii in range(image.ndim))
#         A = uniform_filter(image, size = size_vs, mode = mode, cval = cval)
#         
#         # Step2: At each pixel, compute absolute differences E(x,y) between 
#         # the pairs of non overlapping averages in the horizontal and vertical directions.
#         #print "Step2"
#         for d in xrange(image.ndim):
#             borders = numpy.rint(2**(k * voxelspacing[d]))
#             print str(k) + "  " + str(d) +  "  "  +  str(borders)
#             
#             slicerPad_k_d   = [slice(2**5,None)]*image.ndim
#             slicerPad_k_d[d]= slice((2**5-borders if borders < 2**5 else 0),None)
#             Apad_k_d        = Apad[slicerPad_k_d]
# 
#             
#             AslicerL        = rawSlicer[:]
#             AslicerL[d]     = slice(0, -borders)
#             
#             AslicerR        = rawSlicer[:]
#             AslicerR[d]     = slice(borders, None)
#             
#             E[k,d,...] = numpy.abs(Apad_k_d[AslicerL] - Apad_k_d[AslicerR])
# 
#     
#     # step3: At each pixel, find the value of k that maximises the difference Ek(x,y)
#     # in either direction and set the best size Sbest(x,y)=2**k
#     #print "Step3"
#     S = 2.0**(E.max(1).argmax(0))
#     
#     #print "Step4"
#     # step4: Compute the coarseness feature Fcrs by averaging Sbest(x,y) over the entire image.
#     
#     return S.mean()