"""
@package medpy.graphcut.energy_label
Run-time optimized energy functions for graph-cut on label images.

Provides a number of standard energy functions for both, boundary and regional terms,
that follow the signature required for building graphs using the graph module of this
package. Additionally a number of convenience functions for re-occurring data processing
are given.

Functions:
    - def boundary_difference_of_means(label_image, (original_image)): simple mean value base boundary term
    - def boundary_stawiaski(label_image, (gradient_image)): boundary term implementation in (1)
    - def boundary_stawiaski_directed(label_image, (gradient_image, directedness)): boundary term implementation in (1) with directed edges

(1) Stawiaski J., Decenciere E., Bidlaut F. / "Interactive Liver Tumor Segmentation
Using Graph-cuts and watershed" / MICCAI 2008 participation

@author Oskar Maier
@version r0.2.1
@since 2012-01-18
@status Release
"""

# build-in module
import math

# third-party modules
import scipy.ndimage
import sys

# own modules

# code
def boundary_difference_of_means(label_image, (original_image)): # label image is not required to hold continuous ids or to start from 1
    """
    An implementation of the boundary term, suitable to be used with the
    graphcut.generate.graph_from_labels() function.
    
    This simple energy function computes the mean values for all regions. The weights of
    the edges are then determined by the difference in mean values.
    
    The graph weights generated have to be strictly positive and preferably in the
    interval (0, 1].
    
    To ensure this, the maximum possible difference in mean values is computed as
    \f[
        \alpha = \|\max \bar{I} - \min \bar{I}\|
    \f]
    , where \f$\min \bar{I}\f$ constitutes the lowest mean intensity value of all regions in
    the image, while \f$\max \bar{I}\f$ constitutes the highest mean intensity value 
    
    With this value the weights between a voxel \f$x\f$ and its neighbour \f$y\f$ can be
    computed
    \f[
        w(x,y) = \max \left( 1 - \frac{\|\bar{I}_x - \bar{I}_y\|}{\alpha}, \epsilon \right)
    \f]
    where \f$\epsilon\f$ is the smallest floating point step and thus
    \f$w(x,y) \in (0, 1]\f$ holds true.
    
    @note This function requires the original image to be passed along. That means that
    graphcut.generate.graph_from_labels() has to be called with boundary_term_args set to the
    original image. 
    
    @note This function is tested on 2D and 3D images and theoretically works on all
    dimensions. 
    
    @param label_image the label image
    @type label_image numpy.ndarray
    @param original_image The original image.
    @type original_image numpy.ndarray
    
    @return a dictionary with the edges as keys and the respective weight tuples as
            values
    @rtype dict
    """
    # convert to arrays if necessary
    label_image = scipy.asarray(label_image)
    original_image = scipy.asarray(original_image)
    
    if label_image.flags['F_CONTIGUOUS']: # strangely one this one is required to be ctype ordering
        label_image = scipy.ascontiguousarray(label_image)
    
    # create a lookup-table that translates from a label id to its position in the sorted unique vector
    labels_unique = scipy.unique(label_image)
    
    # compute the mean intensities of all regions
    # Note: Bug in mean implementation: means over labels is only computed if the indexes are also supplied
    means = scipy.ndimage.measurements.mean(original_image, labels=label_image, index=labels_unique)
    
    # compute the maximum possible intensity difference
    max_difference = float(abs(min(means) - max(means)))

    # create a lookup table that relates region ids to their respective intensity values
    means = dict(zip(labels_unique, means))

    # get the adjuncancy of the labels
    edges = __compute_edges(label_image)
    dic = dict.fromkeys(edges)
    
    # compute the difference of means for each adjunct region and add it as a tuple to the dictionary
    if 0. == max_difference: # special case when the divider is zero and therefore all values can be assured to equal zero
        dic = dict.fromkeys(edges, (sys.float_info.min, sys.float_info.min))
    else:    
        # compute the difference of means for each adjunct region and add it as a tuple to the dictionary
        for key in dic.iterkeys():
            value = max(1. - abs(means[key[0]] - means[key[1]]) / max_difference, sys.float_info.min)
            dic[key] = (value, value)

    return dic



def boundary_stawiaski(label_image, (gradient_image)): # label image is not required to hold continuous ids or to start from 1
    """
    An implementation of the boundary term in (1), suitable to be used with the
    graphcut.generate.graph_from_labels() function.
    
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
    be passed along. That means that graphcut.generate.graph_from_labels() has to be called with
    boundary_term_args set to the gradient image.
    
    @note This function is tested on 2D and 3D images and theoretically works on all
    dimensions.
    
    @param label_image the label image
    @type label_image numpy.ndarray
    @param gradient_image The gradient magnitude image of the original image.
    @type gradient_image numpy.ndarray
    
    @return a dictionary with the edges as keys and the respective weight tuples as
    values
    @rtype dict
    """
    # convert to arrays if necessary
    label_image = scipy.asarray(label_image)
    gradient_image = scipy.asarray(gradient_image)
    
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
        value = max(value, sys.float_info.min) # ensure that no value is zero; this can occure due to rounding errors
        dic[key] = (value, value)

    return dic



def boundary_stawiaski_directed(label_image, (gradient_image, directedness)): # label image is not required to hold continuous ids or to start from 1
    """
    An implementation of the boundary term in (1), suitable to be used with the
    graphcut.generate.graph_from_labels() function.
    
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
        w_{i,j} = \sum_{e_{m,n}|inF_{(r_i,r_j)}}g(\max(|I(m)|,|I(n)|))
    \f]
    , where \f$F_{(r_i,r_j)}\f$ is the set of border voxel-pairs \f$e_{m,n}\f$ between
    the regions \f$r_i\f$ and \f$r_j\f$ and \f$|I(p)|\f$ the absolute of the gradient
    magnitude at the voxel \f$p\f$
    
    This boundary_function works as an edge indicator in the original image. In simpler
    words the weight (and therefore the energy) is obtained by summing the local contrast
    along the boundaries between two regions.
    
    When the directedness parameter is set to zero, the resulting graph will be undirected.
    When it is set to a positive value, light-to-dark transitions are favored i.e. voxels
    with a lower intensity (darker) than the objects tend to be assigned to the object.
    The boundary term is thus changed to
    \f[
          g_{ltd}(x) = \left\{
              \begin{array}{l l}
                g(x) + \beta & \quad \textrm{if $I_i > I_j$}\\
                g(x) & \quad \textrm{if $I_i \leq I_j$}\\
              \end{array} \right.
    \f]
    With a negative value for directedness, the opposite effect can be achieved i.e.
    voxels with a higher intensity (lighter) than the objects tend to be assigned to the
    object. The boundary term is thus changed to
    \f[
      g_{dtl} = \left\{
          \begin{array}{l l}
            g(x) & \quad \textrm{if $I_i > I_j$}\\
            g(x) + \beta & \quad \textrm{if $I_i \leq I_j$}\\
          \end{array} \right.
    \f]
    Subsequently the \f$g(x)\f$ in the computation of \f$w_{i,j}\f$ is substituted by
    \f$g_{ltd}\f$ resp. \f$g_{dtl}\f$. The value \f$\beta\$ determines the power of the
    directedness and corresponds to the absolute value of the supplied directedness
    parameter. Experiments showed values between 0.0001 and 0.0003 to be good candidates.
    
    @note This function requires the gradient magnitude image of the original image to
    be passed along. That means that graphcut.generate.graph_from_labels() has to be called with
    boundary_term_args set to the gradient image.
    
    @note This function is tested on 2D and 3D images and theoretically works on all
    dimensions. 
    
    @param label_image the label image
    @type label_image numpy.ndarray
    @param gradient_image The gradient magnitude image of the original image.
    @type gradient_image numpy.ndarray
    @param directedness The weight of the directedness, a positive number to favour
    light-to-dark and a negative to dark-to-light transitions. See function
    description for more details.
    @type directedness int
    
    @return a dictionary with the edges as keys and the respective weight tuples as
            values
    @rtype dict
    """
    # convert to arrays if necessary
    label_image = scipy.asarray(label_image)
    gradient_image = scipy.asarray(gradient_image)
    
    if label_image.flags['F_CONTIGUOUS']: # strangely one this one is required to be ctype ordering
        label_image = scipy.ascontiguousarray(label_image)
        
    beta = abs(directedness)
        
    def addition_directed_ltd(key1, key2, v1, v2, dic): # for light-to-dark # tested
        "Takes a key defined by two uints, two voxel intensities and a dict to which it adds g(v1, v2)."
        if not key1 == key2: # do not process voxel pairs which belong to the same region
            if key2 > key1: # build a sorted key, as we only want one entry for each adjunct region pair; also switch vs
                tmp = v1
                v1 = v2
                v2 = tmp
                key = (key2, key1)
            else:
                key = (key1, key2)
            # The function used to compute the weight contribution of each voxel pair
            value = math.pow(1./(1. + max(abs(v1), abs(v2))), 2)
            # ensure that no value is zero; this can occur due to rounding errors
            value = max(value, sys.float_info.min)
            # add weighted values to already existing edge
            if v1 > v2: dic[key] = [sum(x) for x in zip(dic.get(key, (0, 0)), (min(1, value + beta), value))]
            else: dic[key] = [sum(x) for x in zip(dic.get(key, (0, 0)), (value, min(1, value + beta)))]
            
    def addition_directed_dtl(key1, key2, v1, v2, dic): # for dark-to-light # tested
        "Takes a key defined by two uints, two voxel intensities and a dict to which it adds g(v1, v2)."
        if not key1 == key2: # do not process voxel pairs which belong to the same region
            if key2 > key1: # build a sorted key, as we only want one entry for each adjunct region pair; also switch vs
                tmp = v1
                v1 = v2
                v2 = tmp
                key = (key2, key1)
            else:
                key = (key1, key2)
            # The function used to compute the weight contribution of each voxel pair
            value = math.pow(1./(1. + max(abs(v1), abs(v2))), 2)
            # ensure that no value is zero; this can occur due to rounding errors
            value = max(value, sys.float_info.min)
            # add weighted values to already existing edge
            if v1 > v2: dic[key] = [sum(x) for x in zip(dic.get(key, (0, 0)), (value, min(1, value + beta)))]
            else: dic[key] = [sum(x) for x in zip(dic.get(key, (0, 0)), (min(1, value + beta), value))]            
                                                  
    # pick and vectorize the function to achieve a speedup
    if 0 > directedness:
        vaddition = scipy.vectorize(addition_directed_dtl)
    else:
        vaddition = scipy.vectorize(addition_directed_ltd)
    
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

    return dic

def __compute_edges(label_image):
    """
    Computes the region neighbourhood defined by a star shaped n-dimensional structuring
    element (as returned by scipy.ndimage.generate_binary_structure(ndim, 1)) for the
    supplied region/label image.
    Note The returned set contains neither duplicates, nor self-references
    (i.e. (id_1, id_1)), nor reversed references (e.g. (id_1, id_2) and (id_2, id_1).
    
    @param label_image An image with labeled regions (nD).
    @param return A set with tuples denoting the edge neighbourhood.
    """
    # compute the neighbours
    Er = __compute_edges_nd(label_image)
    
    # remove reversed neighbours and self-references
    for edge in list(Er):
        if (edge[1], edge[0]) in Er:
            Er.remove(edge)
    return Er
    
    
def __compute_edges_nd(label_image):
    """
    Computes the region neighbourhood defined by a star shaped n-dimensional structuring
    element (as returned by scipy.ndimage.generate_binary_structure(ndim, 1)) for the
    supplied region/label image.
    @note The returned set can contain self references (i.e. (id_1, id_1)) as well as
    reversed references (e.g. (id_1, id_2) and (id_2, id_1).
    @see __compute_edges_nd2 alternative implementation (slighty slower)
    @see __compute_edges_3d faster implementation for three dimensions only
    
    @param label_image An image with labeled regions (nD).
    @param return A set with tuples denoting the edge neighbourhood.
    """
    Er = set()
    for dim in range(label_image.ndim):
        slices_x = []
        slices_y = []
        for di in range(label_image.ndim):
            slices_x.append(slice(None, -1 if di == dim else None))
            slices_y.append(slice(1 if di == dim else None, None))
        Er = Er.union(set(zip(label_image[slices_x].flat,
                              label_image[slices_y].flat)))
    return Er
