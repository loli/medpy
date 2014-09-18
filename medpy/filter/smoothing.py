#!/usr/bin/python

"""Image smoothing filter."""

# build-in modules

# third-party modules
import numpy
from scipy.ndimage.filters import gaussian_filter

# path changes

# own modules
from medpy.filter.utilities import xminus1d


# information
__author__ = "Oskar Maier and others (see below)"
__version__ = "r0.3, 2013-08-23"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = "Image smoothing filters."

# code

def gauss_xminus1d(img, sigma, dim=2):
    """
    Applies a X-1D gauss to a copy of a XD image, slicing it along dim.
    
    Essentially uses scipy.ndimage.filters.gaussian_filter, but applies it to a dimension
    less than the image has.
    
    @param img the image to smooth
    @type img ndarray
    @param sigma the sigma i.e. gaussian kernel size in pixel
    @type sigma int
    @param dim the dimension to ignore
    @type dim int
    """
    img = numpy.array(img, copy=False)
    return xminus1d(img, gaussian_filter, dim, sigma=sigma)

def anisotropic_diffusion(img, niter=1, kappa=50, gamma=0.1, voxelspacing=None, option=1):
    """
    XD Anisotropic diffusion.

    Usage:
    out = anisodiff(img, niter, kappa, gamma, voxelspacing, option)

    Arguments:
            img          - input image (will be cast to numpy.float)
            niter        - number of iterations
            kappa        - conduction coefficient 20-100 ?
            gamma        - max value of .25 for stability
            voxelspacing - tuple, the distance between adjacent pixels in all img.ndim directions
            option       - 1 Perona Malik diffusion equation No 1
                           2 Perona Malik diffusion equation No 2

    Returns:
            out          - diffused image.

    kappa controls conduction as a function of gradient.  If kappa is low
    small intensity gradients are able to block conduction and hence diffusion
    across step edges.  A large value reduces the influence of intensity
    gradients on conduction.

    gamma controls speed of diffusion (you usually want it at a maximum of
    0.25)

    step is used to scale the gradients in case the spacing between adjacent
    pixels differs in the x,y and/or z axes

    Diffusion equation 1 favours high contrast edges over low contrast ones.
    Diffusion equation 2 favours wide regions over smaller ones.

    Reference: 
    P. Perona and J. Malik. 
    Scale-space and edge detection using ansotropic diffusion.
    IEEE Transactions on Pattern Analysis and Machine Intelligence, 
    12(7):629-639, July 1990.

    Original MATLAB code by Peter Kovesi  
    School of Computer Science & Software Engineering
    The University of Western Australia
    pk @ csse uwa edu au
    <http://www.csse.uwa.edu.au>

    Translated to Python and optimised by Alistair Muldal
    Department of Pharmacology
    University of Oxford
    <alistair.muldal@pharm.ox.ac.uk>
    
    Adapted to arbitrary dimensionality and added to the MedPy library Oskar Maier
    Institute for Medical Informatics
    Universitaet Luebeck
    <oskar.maier@googlemail.com>

    June 2000  original version.       
    March 2002 corrected diffusion eqn No 2.
    July 2012 translated to Python
    August 2013 incorporated into MedPy, arbitrary dimensionality
    """
    # define conduction gradients functions
    if option == 1:
        def condgradient(delta, spacing):
            return numpy.exp(-(delta/kappa)**2.)/float(spacing)
    elif option == 2:
        def condgradient(delta, spacing):
            return 1./(1.+(delta/kappa)**2.)/float(spacing)

    # initialize output array
    out = numpy.array(img, dtype=numpy.float32, copy=True)
    
    # set default voxel spacong if not suppliec
    if None == voxelspacing:
        voxelspacing = tuple([1.] * img.ndim)

    # initialize some internal variables
    deltas = [numpy.zeros_like(out) for _ in xrange(out.ndim)]

    for _ in xrange(niter):

        # calculate the diffs
        for i in xrange(out.ndim):
            slicer = [slice(None, -1) if j == i else slice(None) for j in xrange(out.ndim)]
            deltas[i][slicer] = numpy.diff(out, axis=i)
        
        # update matrices
        matrices = [condgradient(delta, spacing) * delta for delta, spacing in zip(deltas, voxelspacing)]

        # subtract a copy that has been shifted ('Up/North/West' in 3D case) by one
        # pixel. Don't as questions. just do it. trust me.
        for i in xrange(out.ndim):
            slicer = [slice(1, None) if j == i else slice(None) for j in xrange(out.ndim)]
            matrices[i][slicer] = numpy.diff(matrices[i], axis=i)

        # update the image
        out += gamma * (numpy.sum(matrices, axis=0))

    return out
