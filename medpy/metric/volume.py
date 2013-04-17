"""
@package medpy.metric.volume
Holds a metrics class computing volume metrics over two 3D-images contain each a binary object.

Classes:
    - Volume: Computes different volume metrics between two 3D-images contain each an object.

@author Oskar Maier
@version r0.2.1
@since 2011-12-01
@status Release
"""

# build-in modules

# third-party modules
import scipy

# own modules

# code
class Volume(object):
    """
    Computes different volume metrics between two 3D-images contain each a binary object.
    Beside this provides a number of statistics of the two images.
    
    Metrics defined in:
    Heimann, T.; van Ginneken, B.; Styner, M.A.; Arzhaeva, Y.; Aurich, V.; Bauer, C.; Beck, A.; Becker, C.; Beichel, R.; Bekes, G.; Bello, F.; Binnig, G.; Bischof, H.; Bornik, A.; Cashman, P.; Ying Chi; Cordova, A.; Dawant, B.M.; Fidrich, M.; Furst, J.D.; Furukawa, D.; Grenacher, L.; Hornegger, J.; Kainmuller, D.; Kitney, R.I.; Kobatake, H.; Lamecker, H.; Lange, T.; Jeongjin Lee; Lennon, B.; Rui Li; Senhu Li; Meinzer, H.-P.; Nemeth, G.; Raicu, D.S.; Rau, A.-M.; van Rikxoort, E.M.; Rousson, M.; Rusko, L.; Saddi, K.A.; Schmidt, G.; Seghers, D.; Shimizu, A.; Slagmolen, P.; Sorantin, E.; Soza, G.; Susomboon, R.; Waite, J.M.; Wimmer, A.; Wolf, I.; , "Comparison and Evaluation of Methods for Liver Segmentation From CT Datasets," Medical Imaging, IEEE Transactions on , vol.28, no.8, pp.1251-1265, Aug. 2009
    doi: 10.1109/TMI.2009.2013851
    """
    
    """The mask image as scipy array."""
    __mask = None
    """The reference image as scipy array."""
    __reference = None
    """The mask offset as scipy array."""
    __mask_offset = None
    """The reference offset as scipy array."""
    __reference_offset = None
    """The intersection window as rectangle with origin (0,0,0)."""
    __intersection_window = None
    """The size of the mask object."""
    __mask_size = None
    """The size of the reference object."""
    __reference_size = None
    """The size of the union of the two objects."""
    __union_size = None
    """The size of the intersection of the two objects."""
    __intersection_size = None
    
    def __init__(self, mask, reference, mask_offset = [0,0,0], reference_offset = [0,0,0]):
        """
        Initialize the class with two binary images whose 0 values are considered
        to be background voxels and the 1 values foreground.
        @param mask mask as an scipy array (3D image)
        @param reference reference as an scipy array (3D image)
        @param mask_offset offset of the mask array to 0,0,0-origin
        @param mask_offset offset of the reference array to 0,0,0-origin
        """
        # set member vars
        self.__mask = mask
        self.__reference = reference
        self.__mask_offset = scipy.array(mask_offset)
        self.__reference_offset = scipy.array(reference_offset)
        
        # execute necessary pre-computation
        self.__compute_intersection_window()
        
    def get_relative_volume_difference(self):
        """
        Return the relative volume difference between two shapes defined by the
        non-background voxels of in the binary images.
        
        The relative volume distance of 0 means that the volumes are identical. Note that
        this doesn't apply that the shapes are identical or overlap at all. The result is
        given as signed number [-100,+100] to indicate over- or under-segmentation.
        Warning: Can produce values greater than -/+100 if the difference in volume
        exceeds 50%. Positive values means that the mask volume is too big, a negative
        value that it is too small.
        
        @warning This measure is not actually a metric, as it is not symmetric.
        
        Metric definition:
        The relative volume difference between two sets of voxels \f$S(A)\f$ and \f$S(b)\f$
        is given in percent and defined as:
        \f[
            100 * \frac{|A - B|}{|B|}
        \f]
        
        @return The relative volume difference between two shapes
        """
        # compute the objects sizes
        mask_size = self.get_mask_size()
        reference_size = self.get_reference_size()
        
        # compute return value
        return 100. * float(mask_size - reference_size) / reference_size
    
    def get_volumetric_overlap_error(self):
        """
        Return the volumetric overlap error between two shapes defined by the
        non-background voxels of in two binary images.
        
        The volumetric overlap error is 0 for a perfect match and 100 if the two
        shapes don't overlap at all.
        
        Metric definition:
        The volumetric overlap error between two sets of voxels \f$S(A)\f$ and \f$S(b)\f$
        is given in percent and defined as:
        \f[
            100 * \left(
                1 - \frac{|A\cap B|}{|A\cup B|}
            \right)
        \f]
        
        @return The volumetric overlap error between two shapes.
        """
        # compute the union and intersection sizes
        union_size = self.get_union_size()
        intersection_size = self.get_intersection_size()
        
        # compute return value
        return 100. * (1. - float(intersection_size) / union_size)
        
    
    def get_mask_size(self):
        """
        Computes the mask objects size if not yet done and returns it.
        
        @return The size of the mask object.
        """
        # compute if not yet done
        if None == self.__mask_size:
            self.__mask_size = (1 == self.__mask).sum()
            
        return self.__mask_size
        
    def get_reference_size(self):
        """
        Computes the reference objects size if not yet done and returns it.
        
        @return The size of the reference object.
        """
        # compute if not yet done
        if None == self.__reference_size:
            self.__reference_size = (1 == self.__reference).sum()
            
        return self.__reference_size
    
    def get_intersection_size(self):
        """
        Computes the two objects intersection size if not yet done and returns it.
        
        @return The size of the intersection between the two shape.
        """
        if None == self.__intersection_size:
            self.__compute_union_and_intersection()
        return self.__intersection_size
    
    def get_union_size(self):
        """
        Computes the two objects union size if not yet done and returns it.
        
        @return The size of the union between the two shape.
        """
        if None == self.__union_size:
            self.__compute_union_and_intersection()
        return self.__union_size
    
    def __compute_intersection_window(self):
        """
        Computes and sets the intersection windows of the two images.
        The intersection window marks the area in which the two images
        bounding boxes intersect.
        @return a rectangle defining the intersections lower-left and upper-right corner.
        """
        mask_rec = scipy.array([self.__mask_offset, # lower-left corner
                                self.__mask_offset + scipy.array(self.__mask.shape)]) # upper-right corner
        reference_rec = scipy.array([self.__reference_offset, # lower-left corner
                                      self.__reference_offset + scipy.array(self.__reference.shape)]) # upper-right corner
        
        # check if an intersection occurs at all
        intersect = mask_rec[0][0] < reference_rec[1][0] and \
                    mask_rec[0][1] < reference_rec[1][1] and \
                    mask_rec[0][2] < reference_rec[1][2] and \
                    mask_rec[1][0] > reference_rec[0][0] and \
                    mask_rec[1][1] > reference_rec[0][1] and \
                    mask_rec[1][2] > reference_rec[0][2]
                    
        # if not, set an empty intersection
        if not intersect:
            self.__intersection_window = scipy.array([[0,0,0],[0,0,0]]) # cube, offset
            return
        
        # otherwise compute intersection cube
        intersection = ((max(mask_rec[0][0], reference_rec[0][0]), #x lower
                         max(mask_rec[0][1], reference_rec[0][1]), #y lower
                         max(mask_rec[0][2], reference_rec[0][2])), #z lower
                        (min(mask_rec[1][0], reference_rec[1][0]), #x upper
                         min(mask_rec[1][1], reference_rec[1][1]), #y upper
                         min(mask_rec[1][2], reference_rec[1][2]))) #z upper
        
        # set intersection size (cube)
        self.__intersection_window = scipy.array(intersection)        
    
    def __compute_union_and_intersection(self):
        """
        Computes and sets the two image shapes union and intersection sizes.
        """
        # get window marking the images intersection
        iw = self.__intersection_window
        # remove offset that has been added before to shift intersection window
        # to the corresponding image coordinates
        iw_m = iw - self.__mask_offset
        iw_r = iw - self.__reference_offset
        # overlay the images with the intersection window
        w_m = self.__mask[iw_m[0][0]:iw_m[1][0], iw_m[0][1]:iw_m[1][1], iw_m[0][2]:iw_m[1][2]]
        w_r = self.__reference[iw_r[0][0]:iw_r[1][0], iw_r[0][1]:iw_r[1][1], iw_r[0][2]:iw_r[1][2]]
        # compute intersection + its size
        intersection = w_m & w_r
        self.__intersection_size = (1 == intersection).sum()
        # compute union size
        self.__union_size = self.get_mask_size() + self.get_reference_size() - self.__intersection_size
        