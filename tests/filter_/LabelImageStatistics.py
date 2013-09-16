"""Unittest for the label image statistics class."""

# build-in modules
import unittest

# third-party modules
import scipy
from  scipy import stats

# path changes

# own modules
from medpy.filter import LabelImageStatistics

# information
__author__ = "Oskar Maier"
__version__ = "r0.1.1, 2011-12-29"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = "Label image statistics class unittest."

# code
class TestLabelImageStatistics(unittest.TestCase):
        
    def test_Basic(self):
        """Test the case of a region with only one intensity value and some basic return values."""
        # Create label image with only one region
        label_image = scipy.zeros(2*2*2, dtype=scipy.int8).reshape(2,2,2)
        
        # Create original image with only one intensity value
        original_image = scipy.zeros(2*2*2, dtype=scipy.int8).reshape(2,2,2)
        
        # Initialize object
        statistics = LabelImageStatistics(label_image, original_image)
        
        # Check created intensity distribution
        intensity_distributions = statistics.get_intensity_distributions()
        self.assertEqual(len(intensity_distributions), 1)
        self.assertEqual(intensity_distributions[0], 0)
        
        intensity_distribution_histogram = statistics.get_intensity_distribution_histogram()
        self.assertEqual(len(intensity_distribution_histogram[0]), statistics.get_intensity_distribution_histogram_width())
        self.assertEqual(len(intensity_distribution_histogram[1]), statistics.get_intensity_distribution_histogram_width() + 1)
        self.assertEqual(intensity_distribution_histogram[0][statistics.get_intensity_distribution_histogram_width()/2], 1)
        self.assertEqual(intensity_distribution_histogram[0].max(), 1)
        self.assertEqual(intensity_distribution_histogram[0].min(), 0)
        
        # Check created size distribution
        sizes = statistics.get_sizes()
        self.assertEqual(len(sizes), 1)
        self.assertEqual(sizes[0], 2*2*2)
        
        sizes_histogram = statistics.get_size_histogram()
        self.assertEqual(len(sizes_histogram[0]), statistics.get_size_histogram_width())
        self.assertEqual(len(sizes_histogram[1]), statistics.get_size_histogram_width() + 1)
        self.assertEqual(sizes_histogram[0][statistics.get_size_histogram_width()/2], 1)
        self.assertEqual(sizes_histogram[0].max(), 1)
        self.assertEqual(sizes_histogram[0].min(), 0)
        
        # Check other statistics values
        self.assertTrue(statistics.labels_are_consecutive())
        self.assertEqual(statistics.get_min_intensity(), 0)
        self.assertEqual(statistics.get_max_intensity(), 0)
        self.assertEqual(statistics.get_min_label(), 0)
        self.assertEqual(statistics.get_max_label(), 0)
        self.assertEqual(statistics.get_label_count(), 1)

    def test_Homogeneous(self):
        """Checks the return value for a homogeneous region."""
        # Create label image with only one region
        label_image = scipy.zeros(2*2*2, dtype=scipy.int8).reshape(2,2,2)
        
        # Create original image with only one intensity value
        original_image = scipy.zeros(2*2*2, dtype=scipy.int8).reshape(2,2,2)
        
        # Initialize object
        statistics = LabelImageStatistics(label_image, original_image)
        
        # Check created intensity distribution
        intensity_distributions = statistics.get_intensity_distributions()
        self.assertEqual(len(intensity_distributions), 1)
        self.assertEqual(intensity_distributions[0], 0)
        
        intensity_distribution_histogram = statistics.get_intensity_distribution_histogram()
        self.assertEqual(len(intensity_distribution_histogram[0]), statistics.get_intensity_distribution_histogram_width())
        self.assertEqual(len(intensity_distribution_histogram[1]), statistics.get_intensity_distribution_histogram_width() + 1)
        self.assertEqual(intensity_distribution_histogram[0][statistics.get_intensity_distribution_histogram_width()/2], 1)
        self.assertEqual(intensity_distribution_histogram[0].max(), 1)
        self.assertEqual(intensity_distribution_histogram[0].min(), 0)
        
    def test_Equality(self):
        """Checks whether equally formed histograms in different intensity regions produce the same result."""
        # Create random value for testing
        x = scipy.random.randint(10, 10000) 
        
        # Create label image with only one region
        label_image = scipy.zeros(2*2*2, dtype=scipy.int8).reshape(2,2,2)
        
        # Create original images with two equally distributed intensity values
        original_image1 = scipy.zeros(2*2*2).reshape(2,2,2)
        original_image2 = scipy.zeros(2*2*2).reshape(2,2,2)
        original_image1[2:,:,:] = -x
        original_image1[:2,:,:] = 0
        original_image2[2:,:,:] = 0
        original_image2[:2,:,:] = x
        
        # Initialize objects
        statistics1 = LabelImageStatistics(label_image, original_image1)
        statistics2 = LabelImageStatistics(label_image, original_image2)
        
        # Check created intensity distribution to be different
        intensity_distributions1 = statistics1.get_intensity_distributions()
        intensity_distributions2 = statistics2.get_intensity_distributions()
        self.assertEqual(intensity_distributions1[0], intensity_distributions2[0])      
        
    def test_Continuity(self):
        """Checks if the returned values are continuous for more spaced intensity values."""
        # Create random value for testing
        x = scipy.random.randint(10, 10000) 
        
        # Create label image with only one region
        label_image = scipy.zeros(2*2*2, dtype=scipy.int8).reshape(2,2,2)
        
        # Create original images with two equally distributed intensity values
        original_image1 = scipy.zeros(2*2*2).reshape(2,2,2)
        original_image2 = scipy.zeros(2*2*2).reshape(2,2,2)
        original_image1[1:,:,:] = x
        original_image2[1:,:,:] = 2*x
        
        # Initialize objects
        statistics1 = LabelImageStatistics(label_image, original_image1)
        statistics2 = LabelImageStatistics(label_image, original_image2)
        
        # Check created intensity distribution to be different
        intensity_distributions1 = statistics1.get_intensity_distributions()
        intensity_distributions2 = statistics2.get_intensity_distributions()
        self.assertGreater(intensity_distributions2[0], intensity_distributions1[0])        

    def test_Uniform(self):
        """Checks the return value for an uniform intensity histogram."""
        # might not be possible for 3D image, as 3^X never divideable through 10
        pass

    def test_Intensity_1(self):
        """Test a case of distributed intensity values."""
        # Create label image with only one region
        label_image = scipy.zeros(2*2*2, dtype=scipy.int8).reshape(2,2,2)
        
        # Create original image with two equally distibuted intensity value
        original_image = scipy.zeros(2*2*2, dtype=scipy.int8)
        original_image[:4] = -1
        original_image[4:] = 1
        original_image = original_image.reshape(2,2,2)
        
        # Initialize object
        statistics = LabelImageStatistics(label_image, original_image)
        
        # Computed expected result
        i = scipy.array([-1,-1,-1,-1,1,1,1,1])
        h = scipy.histogram(i, statistics._intensity_distribution_local_histogram_width)
        hr = scipy.array(h[0]) / float(h[0].sum())
        g = stats.norm(*stats.norm.fit(i))
        r = abs(hr - g.pdf(h[1][:-1]))
        r *= h[1][-2] - h[1][0]
        r = r.sum()
        
        # Check created intensity distribution
        intensity_distributions = statistics.get_intensity_distributions()
        self.assertEqual(len(intensity_distributions), 1)
        self.assertEqual(intensity_distributions[0], i.std())
        
        intensity_distribution_histogram = statistics.get_intensity_distribution_histogram()
        self.assertEqual(intensity_distribution_histogram[0][statistics.get_intensity_distribution_histogram_width()/2], 1)
        self.assertEqual(intensity_distribution_histogram[0].max(), 1)
        self.assertEqual(intensity_distribution_histogram[0].min(), 0)
        self.assertEqual(intensity_distribution_histogram[1].mean(), i.std())

if __name__ == '__main__':
    unittest.main()