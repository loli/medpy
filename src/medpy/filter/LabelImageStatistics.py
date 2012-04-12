#!/usr/bin/python

"""A statistics object for a label/region image."""

# build-in modules
import math

# third-party modules
import scipy

# path changes

# own modules
from medpy.core import Logger

# information
__author__ = "Oskar Maier"
__version__ = "e0.3, 2011-12-21"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Experimental"
__description__ = "A statistics object for a label/region image."

# code
class LabelImageStatistics:
    # !TODO: Write a unittest for this
    
    """The label image."""
    _image_labels = None
    """The original image."""
    _image_original = None
    
    """The number of bars in the region size histogram."""
    _size_histogram_width = 100
    """The number of bars in the intensity size histogram."""
    _intensity_distribution_histogram_width = 100
    """The number of bars in the intensity size histograms of each region."""
    _intensity_distribution_local_histogram_width = 10
    
    def __init__(self, image_labels, image_original):
        """
        Computes a number of statistics for the labels of a label image.
        These include beside others:
        1. a histogram of the sizes of the regions
        2. a histogram of the sphericity (not roundness) of the regions
        3. a histogram of how the intensity distribution in each region differs
        from a Gaussian distribution
        
        @param image_lables: The label image for which the statistics should be
                             computed as a numpy array
        @param image_original: The original image for which the label image was created.
        """
        if image_labels.shape != image_original.shape:
            raise ValueError('The input images must be of the same shape.')
        
        if not 3 == len(image_labels.shape):
            raise ValueError('Currently this class is only working with 3D images.')
        
        # prepare logger
        self._logger = Logger.getInstance()
        
        self._image_labels = image_labels
        self._image_original = image_original
        
        self._compute()

    # getters/setters
    def get_size_histogram_width(self):
        """
        @see: set_size_histogram_width
        """
        return self._size_histogram_width

    def get_intensity_distribution_histogram_width(self):
        """
        @see: set_intensity_distribution_histogram_width
        """
        return self._intensity_distribution_histogram_width

    def set_size_histogram_width(self, value):
        """
        Set the width and therefore granularity of @see: get_sizes_histogram.
        The histogram created by @see: get_sizes_histogram will contain as many
        bars as the width given here.
        @param value: The width the sizes histogram should have.
        """        
        self._size_histogram_width = value

    def set_intensity_distribution_histogram_width(self, value):
        """
        Set the width and therefore granularity of @see: get_intensity_distribution_histogram.
        The histogram created by @see: get_intensity_distribution_histogram will contain as many
        bars as the width given here.
        @param value: The width the intensity distribution histogram should have.
        """
        self._intensity_distribution_histogram_width = value
    
    
    # statistic getters
    def labels_are_consecutive(self):
        """
        @return: True if the labels are consecutively numbered, False otherwise.
        Note that this can still mean that the first index is not equal to 1 or 0.
        """
        return self._continuous_labels
    
    def get_min_intensity(self):
        """
        @return: the original images minimium intensity
        """
        return self._min_intensity

    def get_max_intensity(self):
        """
        @return: the original images maximum intensity
        """
        return self._max_intensity

    def get_min_label(self):
        """
        @return: the smallest label index in the label image
        """
        return self._min_label
    
    def get_max_label(self):
        """
        @return: the largest label index in the label image
        """
        return self._max_label
    
    def get_label_count(self):
        """
        @return: The number of labels in the label image
        """
        return self._label_count
    
    def get_sizes(self):
        """
        @return: A dictionary with the labels as keys and their sizes as values.
        """
        return self._sizes
        
    def get_size_histogram(self):
        """
        Gives the region size distribution.
        @return: A histogram created from the normalized region sizes with
                 scipy.histogram.
        
        @note: The width and therefore the number of distinct values of the histogram can
               be set with @see: LabelImageStatistics.set_size_histogram_width.
        """
        return scipy.histogram(self._sizes.values(), self._size_histogram_width)
    
    def get_intensity_distributions(self):
        """
        @return: A dictionary with the labels as keys and the convolution of their
                 intensity distribution from an ideal Gaussian as values.
        """
        return self._intensity_distributions
    
    def get_intensity_distribution_histogram(self):
        """
        Gives the distribution of the smoothness of the intensity distribution in each region.
        @return: A histogram created from the normalized distances between
                 each regions intensity distribution and a ideally fitted
                 Gaussian with scipy.histogram.
        
        The raw values can be extracted using @see: LabelImageStatistics.get_intensity_distributions.
        
        @note: The width and therefore the number of distinct values of the histogram can
               be set with @see: LabelImageStatistics.set_intensity_distribution_histogram_width.
        """
        return scipy.histogram(self._intensity_distributions.values(), self._intensity_distribution_histogram_width)
            
            
    # private methods
    def _dataset_average_distance(self, d1, d2):
        """
        @param: an array of values
        @param: a second array of values
        
        @return: the average distance between the values in the two datasets
        """
        distances = abs(d1 - d2)
        return distances.sum() / float(len(distances))
            
    def _sphericity(self, points):
        """
        @param: A number of connected points in 3D space
        @return: The sphericity of the object represented by the supplied points.
        """
        #!TODO: Implement
        # Acording to http://en.wikipedia.org/wiki/Sphericity there are two possibilities
        # 1. Computing the surface area and volume to compute the classical Wadell sphericity
        # 2. To fit an ellipse over the region and use the computation of section "Ellipsoidal objects"
        
        return len(points)   
        
    def _compute(self):
        """
        Triggers the computation of the statistics.
        """
        
        # collect the labels appearing in the image
        #print 'Collecting labels...'
        labels = scipy.unique(self._image_labels)
        
        # collect some simple label statistics
        self._min_label = labels.min()
        self._max_label = labels.max()
        self._label_count = len(labels)
        
        self._logger.info('Computing the statistics will take approx. {} minutes.'.format(self._label_count/328571.))
        
        # check if they are continuous (Note: does not check if they are actually starting from 0 or any other number)
        if self._label_count == self._max_label - self._min_label + 1: self._continuous_labels = True
        else: self._continuous_labels = False
        
        # prepare collection dictionaries by setting their initial values
        intensities = {}
        for label in labels:
            intensities[label] = [] # for collecting the intensities
        self._min_intensity = self._max_intensity = self._image_original[0,0,0]
        
        # iterate over the label images pixels and collect the regions intensity values
        for x in range(self._image_labels.shape[0]):
            #print 'Processing slice {}'.format(x)
            for y in range(self._image_labels.shape[1]):
                for z in range(self._image_labels.shape[2]):
                    intensity = self._image_original[x,y,z]
                    # extract and collect intensity values
                    intensities[self._image_labels[x,y,z]].append(intensity)
                    # check for global min/max intensity
                    if intensity < self._min_intensity: self._min_intensity = intensity
                    elif intensity > self._max_intensity: self._max_intensity = intensity
                    
        # prepare parameters to collect statistics while iterating over the regions
        self._sizes = {}
        self._intensity_distributions = {}

        # compute intensity distribution, region sizes and other statistics from the regions
        for label, region_intensities in intensities.iteritems():
            #print 'Processing label {} / {}'.format(label, self._label_count)
            
            # calculate and collect region size
            self._sizes[label] = len(region_intensities)
            
            region_intensities = scipy.array(region_intensities)
            #self._intensity_distributions[label] = region_intensities.std()

            # calculate intensity distribution of the region
            # create a normed region intensity histogram from the region intensities (Note: histogram normed parameter behaves strange. Norming manually.)
            region_intensity_histogram = scipy.histogram(region_intensities, self._intensity_distribution_local_histogram_width)
            region_intensity_histogram_normed_values = region_intensity_histogram[0] / float(region_intensity_histogram[0].sum())

            #var = region_intensity_histogram_normed_values.var()
            #mean = region_intensity_histogram_normed_values.mean()
            region_intensities = scipy.array(region_intensities)
            var = region_intensities.var()
            mean = region_intensities.mean()

            if region_intensity_histogram_normed_values.max() == region_intensity_histogram_normed_values.sum(): # special case of a histogram with only one peak in the histogram (i.e. a region with only one intensity value)
                d = dict(zip(region_intensity_histogram[1][:-1], region_intensity_histogram_normed_values))
                gauss = lambda x: d[x]
            elif 0 == var: # special case of uniform distribution of the histogram values
                gauss = lambda x: 0 
            else: # normal case
                prefix = 1./math.sqrt(2.*math.pi*var)
                div = -2. * var # negative prefix of exponent is introduced here
                gauss = lambda x: prefix * math.exp(((x - mean)**2) / div)
                
            # get the distances between normalized histogram and ideal gaussian at the _intensity_distribution_local_histogram_width sample points
            distances = abs(region_intensity_histogram_normed_values - [gauss(x) for x in region_intensity_histogram[1][:-1]])
            
            # multiply results with each section of the actual histogram width, to (approx) the area by which the normalized histogram and ideal gaussian differ
            distances *= region_intensity_histogram[1][-2] - region_intensity_histogram[1][0]
                 
            # save computed value
            self._intensity_distributions[label] = distances.sum()
            
            #self._intensity_distributions[label] = distances.sum() / float(len(distances)) # this normalization just helps to get values (0,1), otherwise it keeps the ratios
            
            
            # fit a gauss to the histogram data (using mean() and std() of numpy.array)
            #gauss = stats.norm(*stats.norm.fit(region_intensity_histogram[0]))
            # sample the gauss at same points as the histogram (curiously scipy.histogram returns one more bin position value than actual bins defined, therefore the [:-1])
            #gauss_samples = gauss.pdf(region_intensity_histogram[1][:-1])
            # calculate the distance between the datasets as a measure of how well the gaussian fits to the data and collect
            #self._intensity_distributions[label] = self._dataset_average_distance(region_intensity_histogram[0], gauss_samples)
