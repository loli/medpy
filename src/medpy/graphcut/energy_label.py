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
@version r0.3.0
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
def boundary_difference_of_means(graph, label_image, (original_image)): # label image is not required to hold continuous ids or to start from 1
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
    
    @param graph the graph to add the weights to
    @type graph graphcut.graph.GCGraph    
    @param label_image the label image
    @type label_image numpy.ndarray
    @param original_image The original image.
    @type original_image numpy.ndarray
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
    
    # compute the difference of means for each adjunct region and add it as a tuple to the dictionary
    if 0. == max_difference: # special case when the divider is zero and therefore all values can be assured to equal zero
        for edge in edges:
            graph.add_nweight(edge[0] - 1, edge[1] - 1, sys.float_info.min, sys.float_info.min)
    else:    
        # compute the difference of means for each adjunct region and add it as a tuple to the dictionary
        for edge in edges:
            value = max(1. - abs(means[edge[0]] - means[edge[1]]) / max_difference, sys.float_info.min)
            graph.add_nweight(edge[0] - 1, edge[1] - 1, value, value)


def boundary_stawiaski(graph, label_image, (gradient_image)): # label image is not required to hold continuous ids or to start from 1
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
    
    @param graph the graph to add the weights to
    @type graph graphcut.graph.GCGraph
    @param label_image the label image
    @type label_image numpy.ndarray
    @param gradient_image The gradient magnitude image of the original image.
    @type gradient_image numpy.ndarray
    """
    # convert to arrays if necessary
    label_image = scipy.asarray(label_image)
    gradient_image = scipy.asarray(gradient_image)
    
    if label_image.flags['F_CONTIGUOUS']: # strangely one this one is required to be ctype ordering
        label_image = scipy.ascontiguousarray(label_image)
    
    def addition(key1, key2, v1, v2):
        "Takes a key defined by two uints, two voxel intensities and adds to the function wide graph a new nweight."
        if not key1 == key2:
            weight = math.pow(1./(1. + max(abs(v1), abs(v2))), 2) # weight contribution of a single pixel
            graph.set_nweight(min(key1, key2) - 1, max(key1, key2) - 1, weight, weight)
                                                  
    # vectorize the function to achieve a speedup
    vaddition = scipy.vectorize(addition)
    
    # iterate over each dimension
    for dim in range(label_image.ndim):
        slices_x = []
        slices_y = []
        for di in range(label_image.ndim):
            slices_x.append(slice(None, -1 if di == dim else None))
            slices_y.append(slice(1 if di == dim else None, None))
        vaddition(label_image[slices_x],
                  label_image[slices_y],
                  gradient_image[slices_x],
                  gradient_image[slices_y])


def boundary_stawiaski_directed(graph, label_image, (gradient_image, directedness)): # label image is not required to hold continuous ids or to start from 1
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
    
    @param graph the graph to add the weights to
    @type graph graphcut.graph.GCGraph    
    @param label_image the label image
    @type label_image numpy.ndarray
    @param gradient_image The gradient magnitude image of the original image.
    @type gradient_image numpy.ndarray
    @param directedness The weight of the directedness, a positive number to favour
    light-to-dark and a negative to dark-to-light transitions. See function
    description for more details.
    @type directedness int
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
            # The function used to compute the weight contribution of each voxel pair
            weight = math.pow(1./(1. + max(abs(v1), abs(v2))), 2)
            # ensure that no value is zero; this can occur due to rounding errors
            weight = max(weight, sys.float_info.min)
            # add weighted values to already existing edge
            if v1 > v2: graph.set_nweight(key1 - 1, key2 - 1, min(1, weight + beta), weight)
            else: graph.set_nweight(key1 - 1, key2 - 1, weight, min(1, weight + beta))
            
    def addition_directed_dtl(key1, key2, v1, v2): # for dark-to-light # tested
        "Takes a key defined by two uints, two voxel intensities and a dict to which it adds g(v1, v2)."
        if not key1 == key2: # do not process voxel pairs which belong to the same region
            # The function used to compute the weight contribution of each voxel pair
            weight = math.pow(1./(1. + max(abs(v1), abs(v2))), 2)
            # ensure that no value is zero; this can occur due to rounding errors
            weight = max(weight, sys.float_info.min)
            # add weighted values to already existing edge
            if v1 > v2: graph.set_nweight(key1 - 1, key2 - 1, weight, min(1, weight + beta))
            else: graph.set_nweight(key1 - 1, key2 - 1, min(1, weight + beta), weight)
                                                  
    # pick and vectorize the function to achieve a speedup
    if 0 > directedness:
        vaddition = scipy.vectorize(addition_directed_dtl)
    else:
        vaddition = scipy.vectorize(addition_directed_ltd)
    
    # iterate over each dimension
    for dim in range(label_image.ndim):
        slices_x = []
        slices_y = []
        for di in range(label_image.ndim):
            slices_x.append(slice(None, -1 if di == dim else None))
            slices_y.append(slice(1 if di == dim else None, None))
        vaddition(label_image[slices_x],
                  label_image[slices_y],
                  gradient_image[slices_x],
                  gradient_image[slices_y])

def regional_atlas(graph, label_image, (atlas_image, alpha)): # label image is required to hold continuous ids starting from 1
    """
    An implementation of a regions term using a statistical atlas, suitable to be used
    with the graphcut.generate.graph_from_labels() function.
    
    Computes the sum of all statistical atlas voxels under each region and uses this
    value as node weight for the graph cut.
    
    This regional term introduces statistical probability of a voxel to belong to the
    object to segment. 
    
    @note This function requires an atlas image of the same shape as the original image
    to be passed along. That means that graphcut.generate.graph_from_labels() has to be
    called with boundary_term_args set to the atlas image.
    
    @note This function is tested on 2D and 3D images and theoretically works on all
    dimensions.
    
    @param graph the graph to add the weights to
    @type graph graphcut.graph.GCGraph
    @param label_image the label image
    @type label_image numpy.ndarray
    @param atlas_image The atlas image associated with the object to segment.
    @type atlas_image numpy.ndarray
    """
    # finding the objects in the label image (bounding boxes around regions)
    objects = scipy.ndimage.find_objects(label_image)
    
    # iterate over regions and compute the respective sums of atlas values
    for rid in range(1, len(objects) + 1):
        weight = scipy.sum(atlas_image[objects[rid - 1]][label_image[objects[rid - 1]] == rid])
        graph.set_tweight(rid - 1, alpha * weight, -1. * alpha * weight) # !TODO: rid's inside the graph start from 0 or 1? => seems to start from 0
        # !TODO: I can exclude source and sink nodes from this!
        # !TODO: I only have to do this in the range of the atlas objects!


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
    return __compute_edges_nd(label_image)
    
def __compute_edges_nd(label_image):
    """
    Computes the region neighbourhood defined by a star shaped n-dimensional structuring
    element (as returned by scipy.ndimage.generate_binary_structure(ndim, 1)) for the
    supplied region/label image.
    Note The returned set contains neither duplicates, nor self-references
    (i.e. (id_1, id_1)), nor reversed references (e.g. (id_1, id_2) and (id_2, id_1).
    
    @param label_image An image with labeled regions (nD).
    @param return A set with tuples denoting the edge neighbourhood.
    """
    Er = set()
   
    def append(v1, v2):
        if v1 != v2:
            Er.update([(min(v1, v2), max(v1, v2))])
        
    vappend = scipy.vectorize(append)
   
    for dim in range(label_image.ndim):
        slices_x = []
        slices_y = []
        for di in range(label_image.ndim):
            slices_x.append(slice(None, -1 if di == dim else None))
            slices_y.append(slice(1 if di == dim else None, None))
        vappend(label_image[slices_x], label_image[slices_y])
        
    return Er
