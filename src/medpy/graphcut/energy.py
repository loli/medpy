"""
@package medpy.graphcut.energy
Run-time optimized energy functions for graph-cut.

Provides a number of standard energy functions for both, boundary and regional terms,
that follow the signature required for building graphs using the graph module of this
package. Additionally a number of convenience functions for re-occurring data processing
are given.

Functions:
    - def boundary_stawiaski(label_image, (gradient_image)): boundary term implementation in (1)

(1) Stawiaski J., Decenciere E., Bidlaut F. / "Interactive Liver Tumor Segmentation
Using Graph-cuts and watershed" / MICCAI 2008 participation

@author Oskar Maier
@version d0.1.0
@since 2012-01-18
@status Development
"""

# build-in module
import math

# third-party modules
import scipy

# own modules

# code


def boundary_stawiaski(label_image, (gradient_image)):
    """
    An implementation of the boundary term in (1), suitable to be used with the
    @link graph_from_labels() function.
    
    Determines for each two supplied regions the voxels forming their border assuming
    ndim*2-connectedness (e.g. 3*2=6 for 3D). From the gradient magnitude values of each
    end-point voxel the border-voxel pairs, the highest one is selected and passed to a
    strictly positive and decreasing function g, which is defined as:
    \f[
        g(x) = \left(\frac{1}{1+|x|}\right)^k
    \f]
    ,where \f$k=2\f$. The final weight \f$w_{i,j}\f$ between two regions \f$r_i\f$ and
    \f$r_j\f$ is then determined by the sum of all these neighbour values:
    \f[
        w = \sum_{e_{m,n}|inF_{(r_i,r_j)}}g(\max(|I(m)|,|I(n)|))
    \f]
    , where \f$F_{(r_i,r_j)}\f$ is the set of border voxel-pairs \f$e_{m,n}\f$ between
    the regions \f$r_i\f$ and \f$r_j\f$ and \f$|I(p)|\f$ the absolute of the gradient
    magnitude at the voxel \f$p\f$
    
    This boundary_function works as an edge indicator in the original image. In simpler
    words the weight (and therefore the energy) is obtained by summing the local contrast
    along the boundaries between two regions.
    
    @note This function requires the gradient magnitude image of the original image to
    be passed along. That means that @link graph_from_labels() has to be called with
    boundary_term_args set to the gradient image. 
    
    @param label_image the label image
    @type label_image numpy.ndarray
    @param gradient_image The gradient magnitude image of the original image.
    @type gradient_image numpy.ndarray
    
    @return a dictionary with the edges as keys and the respective weight tuples as
            values
    @rtype dict
    """
    if label_image.flags['F_CONTIGUOUS']: # strangely one this one is required to be ctype ordering
        label_image = scipy.ascontiguousarray(label_image)        
    
    def addition(key1, key2, v1, v2, dic):
        "Takes a key defined by two uints, two voxel intensities and a dict to which it adds g(v1, v2)."
        if not key1 == key2:
            key = (min(key1, key2), max(key1, key2))
            # The function used to compute the weight contribution of each voxel pair
            dic[key] = dic.get(key, 0) + math.pow(1./(1. + max(abs(v1), abs(v2))), 2)
                                                  
    # vectorize the function to achieve a speedup
    vaddition = scipy.vectorize(addition)
    
    # iterate over each dimension
    dic = {}
    for dim in range(label_image.ndim):
        slices_x = []
        slices_y = []
        for di in range(label_image.ndim):
            slices_x.append(slice(None, -1 if di == dim else None))
            slices_y.append(slice(1 if di == dim else None, None))
        vaddition(label_image[slices_x].flat,
                  label_image[slices_y].flat,
                  gradient_image[slices_x].flat,
                  gradient_image[slices_y].flat,
                  dic)
    
    # modify the dict to contain tuples (undirected graph)
    for key, value in dic.iteritems():
        dic[key] = (value, value)

    return dic
