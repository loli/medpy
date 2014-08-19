"""A learning method to align the intensity ranges of images."""

# build-in modules

# third-party modules
import numpy
from scipy.interpolate.interpolate import interp1d

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2013-09-04"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = "A learning method to align the intensity ranges of images."

# code
class IntensityRangeStandardization (object):
    """
    Class to standardize intensity ranges between a number of images.
    
    Short description:
    Often images containing similar objects or scenes have different intensity ranges
    that make it difficult to compare them manually as well as to process them
    further.
    
    IntensityRangeStandardization offers a way to transform a number of such images
    intensity ranges to a common standard intensity space without any loss of
    information using a multi-segment linear transformation model.
    
    Once learned, this model can be applied to other, formerly unseen images to map
    them to the same standard intensity space.
    
    Application example:
    We have a number of similar images with varying intensity ranges. To make them
    comparable, we would like to transform them to a common intensity space. Thus we
    run:
    
        from medpy.filter import IntensityRangeStandardization
        irs = IntensityRangeStandardization()
        trained_model, transformed_images = irs.train_transform(images)
        
    Let us assume we now obtain another, new image, that we would like to make
    comparable to the others. As long as it does not differ to much from these, we
    can simply call:
        
        transformed_image = irs.transform(new_image)
        
    For many application, not all images are already available at the time of
    execution. It would therefore be good to be able to preserve a once trained
    model. The solution is to just pickle the once trained model:
    
        import pickle
        with open('my_trained_model.pkl', 'wb') as f:
            pickle.dump(irs, f)
            
    And load it again when required with:
    
        with open('my_trained_model.pkl', 'r') as f:
            irs = pickle.load(f)
            
    Concept of similar images:
    IntensityRangeStandardization is limited to similar images. Images containing
    different object or different compositions of objects are not suitable to be
    transformed to a common intensity space (and it would furthermore not make much
    sense).
    
    A typical application of IntensityRangeStandardization are MRI images showing the
    same body region. These often have different intensity ranges, even when acquired
    from the same patient and using the same scanner. For further processing, e.g.
    for training a classifier, they have to be mapped to a common intensity space.
    
    Failure of the transformation:
    The method implemented in IntensityRangeStandardization ensures that no
    information is lost i.e. a lossless transformation is performed. This can be
    assured when there exists a one-to-one mapping between the images original
    intensity values and their values mapped to the standard intensity space.
    
    But since the transformation model is trained on, and the standard intensity
    space range selected over the training images, this can not be guaranteed for all
    formerly unseen image. If they differ greatly from the training set images, a
    lossless transformation can not be assured anymore. In this case the transform()
    method will throw an InformationLossException.
    
    Should this happen, the model needs to be re-trained with the original training
    images and additionally the images which caused the failure. Since this will lead
    to a new intensity standard space, all already transformed images have to be
    processed again.
    
    Setting the training parameters:
    The method comes with a set of default parameters, that are suitable for most
    cases. But for some special cases, it might be better to set them on your own. Ti
    understand the working of the parameters, it is recommended to read the detailed
    method description first.
    
    The method depends of three parameters:
    cutoffp, i.e. the cut-off percentiles
        These are used to the define the intensity outliers, both during training and
        image transformation. The default values are usualy a good choice.
        (in [1] these are called the minimum and maximum percentile values pc1 and pc2 respectively)
    landmarkp, i.e. the landmark percentiles
        These percentiles define the landmark positions. The more supplied, the more
        exact but less general becomes the model. It is common to supply equally
        spaced percentiles between 0 and 100.
        (in [1] these are called the landmark locations mu_1, .., mu_l)
    strange, i.e. the standard intensity space range
        These two intensity values define roughly the standard intensity space (or
        common intensity space of the images; or even target intensity space) to
        which each images intensities are mapped. This space can be supplied, but it
        is usually recommended to let the method select it automatically during the
        training process. It is additionally possible to supply only the lower or
        upper range border and set the other to ''auto'', in which case the method
        chooses the range automatically, but not the position. 
        (in [1] these are called the minimum and maximum intensities on the standard scale of the IOI s1 resp. s2)
    
    
    Details of the method:
    In the following the method is described in some more detail. For even more
    information see [1].
         
    Essentially the method is based on a multi-segment linear transformation model. A
    standard intensity space (or common intensity space) is defined by an intensity
    value range ''stdrange''.
    During the training phase, the intensity values at certain cut-off percentiles of
    each image are computed and a single-segment linear mapping from them to the
    standard intensity space range limits created. Then the images intensity values
    at a number of landmark percentiles are extracted and passed to the linear
    mapping to be transfered roughly to the standard intensity space. The mean of all
    these mapped landmark intensities form the model learned.
      
    When presented with an image to transform, these images intensity values are
    extracted at the cut-off percentile as well as at the landmark percentile
    positions. This results in a number of segments. Using these and the
    corresponding standard intensity space range values and learned mean landmark
    values, a multi-segment linear transformation model is created for the image.
    This is then applied to the images intensity values to map them to the standard
    intensity space.
    
    Outliers, i.e. the images intensity values that lie outside of the cut-off
    percentiles, are treated separately. They are transformed like the first resp.
    last segmented of the transformation model. Not that this means the transformed
    images intensity values do not always lie inside the standard intensity space
    range, but are fitted as best as possible inside.
    
    The implementation is based on:
    [1] Nyul, L.G.; Udupa, J.K.; Xuan Zhang, "New variants of a method of MRI scale
        standardization," Medical Imaging, IEEE Transactions on , vol.19, no.2, pp.143-150,
        Feb. 2000
    """
    
    # static member variables
    L2 = [50]
    L3 = [25, 50, 75]
    L4 = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    
    def __init__(self, cutoffp = (1, 99), landmarkp = L4, stdrange = 'auto'):
        """
        See class description for more details.
        
        @param cutoffp lower and upper cut-off percentiles to exclude outliers
        @type cutoffp 2-tuple of numbers
        @param landmarkp list of percentiles serving as model landmarks, must lie between
                         the cutoffp values
        @type landmarkp sequence of numbers
        @param stdrange the range of the standrad intensity space for which a
                        transformation is learned; when set to ''auto'', automatically
                        determined from the training image upon training; it is also
                        possible to fix either the upper or the lower border value and
                        setting the other to ''auto'' 
        @type stdrange string | 2-tuple of numbers
        """
        # check parameters
        if not IntensityRangeStandardization.is_sequence(cutoffp):
            raise ValueError('cutoffp must be a sequence')
        if not 2 == len(cutoffp):
            raise ValueError('cutoffp must be of length 2, not {}'.format(len(cutoffp)))
        if not IntensityRangeStandardization.are_numbers(cutoffp):
            raise ValueError('cutoffp elements must be numbers')
        if not IntensityRangeStandardization.are_in_interval(cutoffp, 0, 100, 'included'):
            raise ValueError('cutoffp elements must be in [0, 100]')
        if not cutoffp[1] > cutoffp[0]:
            raise ValueError('the second element of cutoffp must be larger than the first')
        
        if not IntensityRangeStandardization.is_sequence(landmarkp):
            raise ValueError('landmarkp must be a sequence')
        if not 1 <= len(landmarkp):
            raise ValueError('landmarkp must be of length >= 1, not {}'.format(len(landmarkp)))
        if not IntensityRangeStandardization.are_numbers(landmarkp):
            raise ValueError('landmarkp elements must be numbers')
        if not IntensityRangeStandardization.are_in_interval(landmarkp, 0, 100, 'included'):
            raise ValueError('landmarkp elements must be in [0, 100]')
        if not IntensityRangeStandardization.are_in_interval(landmarkp, cutoffp[0], cutoffp[1], 'excluded'):
            raise ValueError('landmarkp elements must be in between the elements of cutoffp')
        if not len(landmarkp) == len(numpy.unique(landmarkp)):
            raise ValueError('landmarkp elements must be unique')
        
        if 'auto' == stdrange:
            stdrange = ('auto', 'auto')
        else:
            if not IntensityRangeStandardization.is_sequence(stdrange):
                raise ValueError('stdrange must be a sequence or \'auto\'')
            if not 2 == len(stdrange):
                raise ValueError('stdrange must be of length 2, not {}'.format(len(stdrange)))
            if not 'auto' in stdrange:
                if not IntensityRangeStandardization.are_numbers(stdrange):
                    raise ValueError('stdrange elements must be numbers or \'auto\'')
                if not stdrange[1] > stdrange[0]:
                    raise ValueError('the second element of stdrange must be larger than the first')
            elif 'auto' == stdrange[0] and not IntensityRangeStandardization.is_number(stdrange[1]):
                raise ValueError('stdrange elements must be numbers or \'auto\'')
            elif 'auto' == stdrange[1] and not IntensityRangeStandardization.is_number(stdrange[0]):
                raise ValueError('stdrange elements must be numbers or \'auto\'')
                
        
        # process parameters
        self.__cutoffp = IntensityRangeStandardization.to_float(cutoffp)
        self.__landmarkp = IntensityRangeStandardization.to_float(sorted(landmarkp))
        self.__stdrange = ['auto' if 'auto' == x else float(x) for x in stdrange]
            
        # initialize remaining instance parameters
        self.__model = None
        self.__sc_umins = None
        self.__sc_umaxs = None
        
    def train(self, images):
        """
        Train a standard intensity space and an associated transformation model.
        
        Note that the passed images should be masked to contain only the foreground.
        
        @param images a number of images
        @type image sequence of ndarrays
        
        @return this instance of IntensityRangeStandardization
        @rtype IntensityRangeStandardization
        """
        self.__stdrange = self.__compute_stdrange(images)
        
        lim = []
        for idx, i in enumerate(images):
            ci = numpy.array(numpy.percentile(i, self.__cutoffp))
            li = numpy.array(numpy.percentile(i, self.__landmarkp))
            ipf = interp1d(ci, self.__stdrange)
            lim.append(ipf(li))

            # treat single intensity accumulation error            
            if not len(numpy.unique(numpy.concatenate((ci, li)))) == len(ci) + len(li):
                raise SingleIntensityAccumulationError('Image no.{} shows an unusual single-intensity accumulation that leads to a situation where two percentile values are equal. This situation is usually caused, when the background has not been removed from the image. Another possibility would be to reduce the number of landmark percentiles landmarkp or to change their distribution.'.format(idx))
            
        self.__model = [self.__stdrange[0]] + list(numpy.mean(lim, 0)) + [self.__stdrange[1]]
        self.__sc_umins = [self.__stdrange[0]] + list(numpy.min(lim, 0)) + [self.__stdrange[1]]
        self.__sc_umaxs = [self.__stdrange[0]] + list(numpy.max(lim, 0)) + [self.__stdrange[1]]
            
        return self
        
    def transform(self, image, surpress_mapping_check = False):
        """
        Transform an images intensity values to the learned standard intensity space.
        
        Note that the passed image should be masked to contain only the foreground.
        
        The transformation is guaranteed to be lossless i.e. a one-to-one mapping between
        old and new intensity values exists. In cases where this does not hold, an error
        is thrown. This can be suppressed by setting surpress_mapping_check to ''True''.
        Do this only if you know what you are doing.
        
        @param image the image to transform
        @type image ndarray
        @param surpress_mapping_check whether to ensure a lossless transformation or not
        @type surpress_mapping_check bool
        
        @return the transformed image
        @rtype ndarray
        
        @raises InformationLossException if a lossless transformation can not be ensured
        @raises Exception if no model has been trained before
        """
        if None == self.__model:
            raise UntrainedException('Model not trained. Call train() first.')
        
        image = numpy.asarray(image)
        
        # determine image intensity values at cut-off percentiles & landmark percentiles
        li = numpy.percentile(image, [self.__cutoffp[0]] + self.__landmarkp + [self.__cutoffp[1]])
        
        # treat single intensity accumulation error            
        if not len(numpy.unique(li)) == len(li):
            raise SingleIntensityAccumulationError('The image shows an unusual single-intensity accumulation that leads to a situation where two percentile values are equal. This situation is usually caused, when the background has not been removed from the image. The only other possibility would be to re-train the model with a reduced number of landmark percentiles landmarkp or a changed distribution.')
        
        # create linear mapping models for the percentile segments to the learned standard intensity space  
        ipf = interp1d(li, self.__model, bounds_error = False)
        
        # transform the input image intensity values
        output = ipf(image)
        
        # treat image intensity values outside of the cut-off percentiles range separately
        llm = IntensityRangeStandardization.linear_model(li[:2], self.__model[:2])
        rlm = IntensityRangeStandardization.linear_model(li[-2:], self.__model[-2:])
        
        output[image < li[0]] = llm(image[image < li[0]])
        output[image > li[-1]] = rlm(image[image > li[-1]])
        
        if not surpress_mapping_check and not self.__check_mapping(li):
            raise InformationLossException('Image can not be transformed to the learned standard intensity space without loss of information. Please re-train.')
        
        return output
    
    def train_transform(self, images, surpress_mapping_check = False):
        ret = self.train(images)
        outputs = [self.transform(i, surpress_mapping_check) for i in images]
        return ret, outputs
    
    @property
    def stdrange(self):
        """Get the set resp. learned standard intensity range."""
        return self.__stdrange
    
    @property
    def cutoffp(self):
        """Get the cut-off percentiles."""
        return self.__cutoffp
    
    @property
    def landmarkp(self):
        """Get the landmark percentiles."""
        return self.__landmarkp
    
    @property
    def model(self):
        """Get the model i.e. the learned percentile values."""
        return self.__model
    
    def __compute_stdrange(self, images):
        """
        Computes a common standard intensity range over a number of images.
        
        Depending on the settings of the internal self.__stdrange variable,
        either (1) the already fixed values are returned, (2) a complete standard
        intensity range is computed from the supplied images, (3) an intensity range
        fixed at the lower end or (4) an intensity range fixed at the upper end is
        returned.
        
        Takes into account the maximum length of each percentile segment over all
        images, then adds a security margin defined by the highest variability among
        all segments over all images.
        
        Be
        \f[
            L = (cop_l, lp_1, lp_2, ..., lp_n, cop_u)
        \f]
        the set formed by the two cut-off percentiles \f$cop_l\f$ and \f$cop_u\f$ and the
        landmark percentiles \f$lp_1, ..., lp_n\f$. The corresponding intensity values of
        an image \f$i\in I\f$ are then
        \f[
            V_i = (v_{i,1}, v_{i,2}, ..., v_{i,n+2})
        \f]
        The distance between each of these intensity values forms a segment along the
        images \f$i\f$ intensity range denoted as
        \f[
            S_i = (s_{i,1}, s_{i,2}, ..., s_{i, n+1})
        \f]
        The common standard intensity range \f$sir\f$ over the set of images \f$I\f$ is
        then defined as
        \f[
            sir = \sum_{l=1}^{n+1}\max_{i=1}^I s_{i,l} * \max_{l=1}^{n+1} \left(\frac{\max_{i=1}^I s_{i,l}}{\min_{i=1}^I s_{i,l}}\right)
        \f]
        
        @param images a number of images
        @type images sequence of ndarrays
        
        @return the borders of the computed standard intensity range
        @rtype tuple of numbers
        """
        if not 'auto' in self.__stdrange:
            return self.__stdrange
        
        copl, copu = self.__cutoffp
        
        # collect cutoff + landmark percentile segments and image mean intensity values 
        s = []
        m = []
        for idx, i in enumerate(images):
            li = numpy.percentile(i, [copl] + self.__landmarkp + [copu])
            
            s.append(numpy.asarray(li)[1:] - numpy.asarray(li)[:-1])
            m.append(i.mean())
            
            # treat single intensity accumulation error
            if 0 in s[-1]:
                raise SingleIntensityAccumulationError('Image no.{} shows an unusual single-intensity accumulation that leads to a situation where two percentile values are equal. This situation is usually caused, when the background has not been removed from the image. Another possibility would be to reduce the number of landmark percentiles landmarkp or to change their distribution.'.format(idx))
            
        # select the maximum and minimum of each percentile segment over all images
        maxs = numpy.max(s, 0)
        mins = numpy.min(s, 0)
        
        # divide them pairwise
        divs = numpy.divide(numpy.asarray(maxs, dtype=numpy.float), mins) 
        
        # compute interval range according to generalized theorem 2 of [1]
        intv = numpy.sum(maxs) + numpy.max(divs)
        
        # compute mean intensity value over all images (assuming equal size)
        im = numpy.mean(m)
        
        # return interval with borders according to settings
        if 'auto' == self.__stdrange[0] and 'auto' == self.__stdrange[1]:
            return im - intv / 2, im + intv / 2
        elif 'auto' == self.__stdrange[0]:
            return self.__stdrange[1] - intv, self.__stdrange[1]
        else:
            return self.__stdrange[0], self.__stdrange[0] + intv
        
    def __check_mapping(self, landmarks):
        """
        Checks whether the image, from which the supplied landmarks were extracted, can
        be transformed to the learned standard intensity space without loss of
        information.
        """
        sc_udiff = numpy.asarray(self.__sc_umaxs)[1:] - numpy.asarray(self.__sc_umins)[:-1]
        l_diff = numpy.asarray(landmarks)[1:] - numpy.asarray(landmarks)[:-1]
        return numpy.all(sc_udiff > numpy.asarray(l_diff))
        
    @staticmethod
    def is_sequence(arg):
        """
        Checks via its hidden attribute whether the passed argument is a sequence (but
        excluding strings).
        
        Credits to Steve R. Hastings a.k.a steveha @ http://stackoverflow.com
        """
        return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))
        
    @staticmethod
    def is_number(arg):
        """
        Checks whether the passed argument is a valid number or not.
        """
        import numbers
        return isinstance(arg, numbers.Number)
    
    @staticmethod
    def are_numbers(arg):
        """
        Checks whether all elements in a sequence are valid numbers.
        """
        return numpy.all([IntensityRangeStandardization.is_number(x) for x in arg])
    
    @staticmethod
    def is_in_interval(n, l, r, border = 'included'):
        """
        Checks whether a number is inside the interval l, r.
        """
        if 'included' == border:
            return (n >= l) and (n <= r)
        elif 'excluded' == border:
            return (n > l) and (n < r)
        else:
            raise ValueError('borders must be either \'included\' or \'excluded\'')
        
    @staticmethod
    def are_in_interval(s, l, r, border = 'included'):
        """
        Checks whether all number in the sequence s lie inside the interval formed by
        l and r.
        """
        return numpy.all([IntensityRangeStandardization.is_in_interval(x, l, r, border) for x in s])
    
    @staticmethod
    def to_float(s):
        """
        Cast a sequences elements to float numbers.
        """
        return [float(x) for x in s]
    
    @staticmethod
    def linear_model((x1, x2), (y1, y2)):
        """
        Returns a linear model transformation function fitted on the two supplied points.
        y = m*x + b
        Note: Assumes that slope > 0, otherwise division through zero might occure.
        """
        m = (y2 - y1) / (x2 - x1)
        b = y1 - (m * x1)
        return lambda x: m * x + b
    
class SingleIntensityAccumulationError(Exception):
    """
    Thrown when an image shows an unusual single-intensity peaks which would obstruct
    both, training and transformation.
    """
    
class InformationLossException(Exception):
    """
    Thrown when a transformation can not be guaranteed to be lossless.
    """
    pass
    
class UntrainedException(Exception):
    """
    Thrown when a transformation is attempted before training.
    """
    pass