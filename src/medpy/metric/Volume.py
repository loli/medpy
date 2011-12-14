#!/usr/bin/python

"""A metrics class computing volume metrics over two 3D-images contain each a binary object."""

# build-in modules

# third-party modules
import scipy

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "r0.2, 2011-12-01"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = "Volume metrics class."

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
    _mask = None
    """The reference image as scipy array."""
    _reference = None
    """The mask offset as scipy array."""
    _mask_offset = None
    """The reference offset as scipy array."""
    _reference_offset = None
    """The intersection window as rectangle with origin (0,0,0)."""
    _intersection_window = None
    """The size of the mask object."""
    _mask_size = None
    """The size of the reference object."""
    _reference_size = None
    """The size of the union of the two objects."""
    _union_size = None
    """The size of the intersection of the two objects."""
    _intersection_size = None
    
    def __init__(self, mask, reference, mask_offset = [0,0,0], reference_offset = [0,0,0]):
        """
        Initialize the class with two binary images whose 0 values are considered
        to be background voxels and the 1 values foreground.
        @param mask: mask as an scipy array (3D image)
        @param reference: reference as an scipy array (3D image)
        @param mask_offset: offset of the mask array to 0,0,0-origin
        @param mask_offset: offset of the reference array to 0,0,0-origin
        """
        # set member vars
        self._mask = mask
        self._reference = reference
        self._mask_offset = scipy.array(mask_offset)
        self._reference_offset = scipy.array(reference_offset)
        
        # execute necessary pre-computation
        self._ComputeIntersectionWindow()
        
    def GetRelativeVolumeDifference(self):
        """
        Returns the relative volume difference between two shapes defined by the
        non-background voxels of in the binary images.
        
        The relative volume distance of 0 means that the volumes are identical. Note that
        this doesn't apply that the shapes are identical or overlap at all. The result is
        given as signed number [-100,+100] to indicate over- or under-segmentation.
        Warning: Can produce values greater than -/+100 if the difference in volume
        exceeds 50%. Positive values means that the mask volume is too big, a negative
        value that it is too small.
        
        Warning: This measure is not actually a metric, as it is not symmetric.
        
        Metric definition:
        The relative volume difference between two sets of voxels \f$S(A)\f$ and \f$S(b)\f$
        is given in percent and defined as:
        \f[
            100 * \frac{|A - B|}{|B|}
        \f]        
        """
        # compute the objects sizes
        mask_size = self.GetMaskSize()
        reference_size = self.GetReferenceSize()
        
        # compute return value
        return 100. * float(mask_size - reference_size) / reference_size
    
    def GetVolumetricOverlapError(self):
        """
        Returns the volumetric overlap error between two shapes defined by the
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
        """
        # compute the union and intersection sizes
        union_size = self.GetUnionSize()
        intersection_size = self.GetIntersectionSize()
        
        # compute return value
        return 100. * (1. - float(intersection_size) / union_size)
        
    
    def GetMaskSize(self):
        """
        Computes the mask objects size if not yet done and returns it.
        """
        # compute if not yet done
        if None == self._mask_size:
            self._mask_size = (1 == self._mask).sum()
            
        return self._mask_size
        
    def GetReferenceSize(self):
        """
        Computes the reference objects size if not yet done and returns it.
        """
        # compute if not yet done
        if None == self._reference_size:
            self._reference_size = (1 == self._reference).sum()
            
        return self._reference_size
    
    def GetIntersectionSize(self):
        """
        Computes the two objects intersection size if not yet done and returns it.
        """
        if None == self._intersection_size:
            self._ComputeUnionAndIntersection()
        return self._intersection_size
    
    def GetUnionSize(self):
        """
        Computes the two objects union size if not yet done and returns it.
        """
        if None == self._union_size:
            self._ComputeUnionAndIntersection()
        return self._union_size
    
    def _ComputeIntersectionWindow(self):
        """
        Computes and sets the intersection windows of the two images.
        The intersection window marks the area in which the two images
        bounding boxes intersect.
        The returned rectangle is defined by its lower-left and upper-right corner.
        """
        mask_rec = scipy.array([self._mask_offset, # lower-left corner
                                self._mask_offset + scipy.array(self._mask.shape)]) # upper-right corner
        reference_rec = scipy.array([self._reference_offset, # lower-left corner
                                      self._reference_offset + scipy.array(self._reference.shape)]) # upper-right corner
        
        # check if an intersection occurs at all
        intersect = mask_rec[0][0] < reference_rec[1][0] and \
                    mask_rec[0][1] < reference_rec[1][1] and \
                    mask_rec[0][2] < reference_rec[1][2] and \
                    mask_rec[1][0] > reference_rec[0][0] and \
                    mask_rec[1][1] > reference_rec[0][1] and \
                    mask_rec[1][2] > reference_rec[0][2]
                    
        # if not, set an empty intersection
        if not intersect:
            self._intersection_window = scipy.array([[0,0,0],[0,0,0]]) # cube, offset
            return
        
        # otherwise compute intersection cube
        intersection = ((max(mask_rec[0][0], reference_rec[0][0]), #x lower
                         max(mask_rec[0][1], reference_rec[0][1]), #y lower
                         max(mask_rec[0][2], reference_rec[0][2])), #z lower
                        (min(mask_rec[1][0], reference_rec[1][0]), #x upper
                         min(mask_rec[1][1], reference_rec[1][1]), #y upper
                         min(mask_rec[1][2], reference_rec[1][2]))) #z upper
        
        # set intersection size (cube)
        self._intersection_window = scipy.array(intersection)        
    
    def _ComputeUnionAndIntersection(self):
        """
        Computes and sets the two image shapes union and intersection sizes.
        """
        # get window marking the images intersection
        iw = self._intersection_window
        # remove offset that has been added before to shift intersection window
        # to the corresponding image coordinates
        iw_m = iw - self._mask_offset
        iw_r = iw - self._reference_offset
        # overlay the images with the intersection window
        w_m = self._mask[iw_m[0][0]:iw_m[1][0], iw_m[0][1]:iw_m[1][1], iw_m[0][2]:iw_m[1][2]]
        w_r = self._reference[iw_r[0][0]:iw_r[1][0], iw_r[0][1]:iw_r[1][1], iw_r[0][2]:iw_r[1][2]]
        # compute intersection + its size
        intersection = w_m & w_r
        self._intersection_size = (1 == intersection).sum()
        # compute union size
        self._union_size = self.GetMaskSize() + self.GetReferenceSize() - self._intersection_size
        