"""
@package medpy.metric.surface
Holds a metrics class computing surface metrics over two 3D-images contain each a binary object.

Classes:
    - Surface: Computes different surface metrics between two 3D-images contain each an object.

@author Oskar Maier
@version r0.4.1
@since 2011-12-01
@status Release
"""

# build-in modules
import math

# third-party modules
import scipy.spatial
import scipy.ndimage.morphology

# own modules

# code
class Surface(object):
    """
    Computes different surface metrics between two 3D-images contain each an object.
    The surface of the objects is computed using a 18-neighbourhood edge detection.
    The distance metrics are computed over all points of the surfaces using the nearest
    neighbour approach.
    Beside this provides a number of statistics of the two images.
    
    During the initialization the edge detection is run for both images, taking up to
    5 min (on 512^3 images). The first call to one of the metric measures triggers the
    computation of the nearest neighbours, taking up to 7 minutes (based on 250.000 edge
    point for each of the objects, which corresponds to a typical liver mask). All
    subsequent calls to one of the metrics measures can be expected be in the
    sub-millisecond area.
    
    Metrics defined in:
    Heimann, T.; van Ginneken, B.; Styner, M.A.; Arzhaeva, Y.; Aurich, V.; Bauer, C.; Beck, A.; Becker, C.; Beichel, R.; Bekes, G.; Bello, F.; Binnig, G.; Bischof, H.; Bornik, A.; Cashman, P.; Ying Chi; Cordova, A.; Dawant, B.M.; Fidrich, M.; Furst, J.D.; Furukawa, D.; Grenacher, L.; Hornegger, J.; Kainmuller, D.; Kitney, R.I.; Kobatake, H.; Lamecker, H.; Lange, T.; Jeongjin Lee; Lennon, B.; Rui Li; Senhu Li; Meinzer, H.-P.; Nemeth, G.; Raicu, D.S.; Rau, A.-M.; van Rikxoort, E.M.; Rousson, M.; Rusko, L.; Saddi, K.A.; Schmidt, G.; Seghers, D.; Shimizu, A.; Slagmolen, P.; Sorantin, E.; Soza, G.; Susomboon, R.; Waite, J.M.; Wimmer, A.; Wolf, I.; , "Comparison and Evaluation of Methods for Liver Segmentation From CT Datasets," Medical Imaging, IEEE Transactions on , vol.28, no.8, pp.1251-1265, Aug. 2009
    doi: 10.1109/TMI.2009.2013851
    """

    # The edge points of the mask object.
    __mask_edge_points = None
    # The edge points of the reference object.
    __reference_edge_points = None
    # The nearest neighbours distances between mask and reference edge points.
    __mask_reference_nn = None
    # The nearest neighbours distances between reference and mask edge points.
    __reference_mask_nn = None
    # Distances of the two objects surface points.
    __distance_matrix = None
    
    def __init__(self, mask, reference, physical_voxel_spacing = [1,1,1], mask_offset = [0,0,0], reference_offset = [0,0,0]):
        """
        Initialize the class with two binary images, each containing a single object.
        Assumes the input to be a representation of a 3D image, that fits one of the
        following formats:
            - 1. all 0 values denoting background, all others the foreground/object
            - 2. all False values denoting the background, all others the foreground/object
        The first image passed is referred to as 'mask', the second as 'reference'. This
        is only important for some metrics that are not symmetric (and therefore not
        really metrics). 
        @param mask binary mask as an scipy array (3D image)
        @param reference binary reference as an scipy array (3D image)
        @param physical_voxel_spacing The physical voxel spacing of the two images
            (must be the same for both)
        @param mask_offset offset of the mask array to 0,0,0-origin
        @param reference_offset offset of the reference array to 0,0,0-origin
        """
        # compute edge images
        mask_edge_image = Surface.compute_contour(mask)
        reference_edge_image = Surface.compute_contour(reference)
        
        # collect the object edge voxel positions
        # !TODO: When the distance matrix is already calculated here
        # these points don't have to be actually stored, only their number.
        # But there might be some later metric implementation that requires the
        # points and then it would be good to have them. What is better?
        mask_pts = mask_edge_image.nonzero()
        mask_edge_points = zip(mask_pts[0], mask_pts[1], mask_pts[2])
        reference_pts = reference_edge_image.nonzero()
        reference_edge_points = zip(reference_pts[0], reference_pts[1], reference_pts[2])
        
        # check if there is actually an object present
        if 0 >= len(mask_edge_points):
            raise Exception('The mask image does not seem to contain an object.')
        if 0 >= len(reference_edge_points):
            raise Exception('The reference image does not seem to contain an object.')
        
        # add offsets to the voxels positions and multiply with physical voxel spacing
        # to get the real positions in millimeters
        physical_voxel_spacing = scipy.array(physical_voxel_spacing)
        mask_edge_points += scipy.array(mask_offset)
        mask_edge_points *= physical_voxel_spacing
        reference_edge_points += scipy.array(reference_offset)
        reference_edge_points *= physical_voxel_spacing
        
        # set member vars
        self.__mask_edge_points = mask_edge_points
        self.__reference_edge_points = reference_edge_points
        
    def get_maximum_symmetric_surface_distance(self):
        """
        Computes the maximum symmetric surface distance, also known as Hausdorff
        distance, between the two objects surfaces.
        
        @return the maximum symmetric surface distance in millimeters
        
        For a perfect segmentation this distance is 0. This metric is sensitive to
        outliers and returns the true maximum error.
        
        Metric definition:
        Let \f$S(A)\f$ denote the set of surface voxels of \f$A\f$. The shortest
        distance of an arbitrary voxel \f$v\f$ to \f$S(A)\f$ is defined as:
        \f[
            d(v,S(A)) = \min_{s_A\in S(A)} ||v-s_A||
        \f]
        where \f$||.||\f$ denotes the Euclidean distance. The maximum symmetric
        surface distance is then given by:
        \f[
            MSD(A,B) = \max
                \left\{
                    \max_{s_A\in S(A)} d(s_A,S(B)),
                    \max_{s_B\in S(B)} d(s_B,S(A)),
                \right\}
        \f]
        """
        # Get the maximum of the nearest neighbour distances
        A_B_distance = self.get_mask_reference_nn().max()
        B_A_distance = self.get_reference_mask_nn().max()
        
        # compute result and return
        return max(A_B_distance, B_A_distance)
        
    def get_root_mean_square_symmetric_surface_distance(self):
        """
        Computes the root mean square symmetric surface distance between the
        two objects surfaces.
        
        @return root mean square symmetric surface distance in millimeters
        
        For a perfect segmentation this distance is 0. This metric punishes large
        deviations from the true contour stronger than the average symmetric surface
        distance.
        
        Metric definition:
        Let \f$S(A)\f$ denote the set of surface voxels of \f$A\f$. The shortest
        distance of an arbitrary voxel \f$v\f$ to \f$S(A)\f$ is defined as:
        \f[
            d(v,S(A)) = \min_{s_A\in S(A)} ||v-s_A||
        \f]
        where \f$||.||\f$ denotes the Euclidean distance. The root mean square
        symmetric surface distance is then given by:
        \f[
          RMSD(A,B) = 
            \sqrt{\frac{1}{|S(A)|+|S(B)|}}
            \times
            \sqrt{
                \sum_{s_A\in S(A)} d^2(s_A,S(B))
                +
                \sum_{s_B\in S(B)} d^2(s_B,S(A))
            }
        \f]
        """
        # get object sizes
        mask_surface_size = len(self.get_mask_edge_points())
        reference_surface_sice = len(self.get_reference_edge_points())
        
        # get minimal nearest neighbours distances
        A_B_distances = self.get_mask_reference_nn()
        B_A_distances = self.get_reference_mask_nn()
        
        # square the distances
        A_B_distances_sqrt = A_B_distances * A_B_distances
        B_A_distances_sqrt = B_A_distances * B_A_distances
        
        # sum the minimal distances
        A_B_distances_sum = A_B_distances_sqrt.sum()
        B_A_distances_sum = B_A_distances_sqrt.sum()

        # compute result and return
        return math.sqrt(1. / (mask_surface_size + reference_surface_sice)) * math.sqrt(A_B_distances_sum + B_A_distances_sum)        
        
    def get_average_symmetric_surface_distance(self):
        """
        Computes the average symmetric surface distance between the
        two objects surfaces.
        
        @return average symmetric surface distance in millimeters
        
        For a perfect segmentation this distance is 0.
        
        Metric definition:
        Let \f$S(A)\f$ denote the set of surface voxels of \f$A\f$. The shortest
        distance of an arbitrary voxel \f$v\f$ to \f$S(A)\f$ is defined as:
        \f[
            d(v,S(A)) = \min_{s_A\in S(A)} ||v-s_A||
        \f]
        where \f$||.||\f$ denotes the Euclidean distance. The average symmetric
        surface distance is then given by:
        \f[
            ASD(A,B) = 
                \frac{1}{|S(A)|+|S(B)|}
                \left(
                    \sum_{s_A\in S(A)} d(s_A,S(B))
                    +
                    \sum_{s_B\in S(B)} d(s_B,S(A))
                \right)
        \f]
        """
        # get object sizes
        mask_surface_size = len(self.get_mask_edge_points())
        reference_surface_sice = len(self.get_reference_edge_points())
        
        # get minimal nearest neighbours distances
        A_B_distances = self.get_mask_reference_nn()
        B_A_distances = self.get_reference_mask_nn()
        
        # sum the minimal distances
        A_B_distances = A_B_distances.sum()
        B_A_distances = B_A_distances.sum()
        
        # compute result and return
        return 1. / (mask_surface_size + reference_surface_sice) * (A_B_distances + B_A_distances)
        
    def get_mask_reference_nn(self):
        """
        @return The distances of the nearest neighbours of all mask edge points to all
                reference edge points.
        """
        # Note: see note for @see get_reference_mask_nn
        if None == self.__mask_reference_nn:
            tree = scipy.spatial.cKDTree(self.get_mask_edge_points())
            self.__mask_reference_nn, _ = tree.query(self.get_reference_edge_points())
        return self.__mask_reference_nn
            
    def get_reference_mask_nn(self):
        """
        @return The distances of the nearest neighbours of all reference edge points
                to all mask edge points.
                 
        The underlying algorithm used for the scipy.spatial.KDTree implementation is
        based on:
        Sunil Arya, David M. Mount, Nathan S. Netanyahu, Ruth Silverman, and
        Angela Y. Wu. 1998. An optimal algorithm for approximate nearest neighbor
        searching fixed dimensions. J. ACM 45, 6 (November 1998), 891-923 
        """
        # Note: KDTree is faster than scipy.spatial.distance.cdist when the number of
        # voxels exceeds 10.000 (computationally tested). The maximum complexity is
        # O(D*N^2) vs. O(D*N*log(N), where D=3 and N=number of voxels
        if None == self.__reference_mask_nn:
            tree = scipy.spatial.cKDTree(self.get_reference_edge_points())
            self.__reference_mask_nn, _ = tree.query(self.get_mask_edge_points())
        return self.__reference_mask_nn
        
    def get_mask_edge_points(self):
        """
        @return The edge points of the mask object.
        """
        return self.__mask_edge_points

    def get_reference_edge_points(self):
        """
        @return The edge points of the reference object.
        """
        return self.__reference_edge_points              
    
    @staticmethod
    def compute_contour(array):
        """
        Uses a 18-neighbourhood filter to create an edge image of the input object.
        Assumes the input to be a representation of a 3D image, that fits one of the
        following formats:
            - 1. all 0 values denoting background, all others the foreground/object
            - 2. all False values denoting the background, all others the foreground/object
        The area outside the array is assumed to contain background voxels. The method
        does not ensure that the object voxels are actually connected, this is silently
        assumed.
        
        @param array a numpy array with only 0/N\{0} or False/True values.
        @return a boolean numpy array with the input objects edges
        """
        # set 18-neighbourhood/conectivity (for 3D images) alias face-and-edge kernel
        # all values covered by 1/True passed to the function 
        # as a 1D array in order left-right, top-down
        # Note: all in all 19 ones, as the center value
        # also has to be checked (if it is a masked pixel)
        # [[[0, 1, 0], [[1, 1, 1],  [[0, 1, 0], 
        #   [1, 1, 1],  [1, 1, 1],   [1, 1, 1],
        #   [0, 1, 0]], [1, 1, 1]],  [0, 1, 0]]]
        footprint = scipy.ndimage.morphology.generate_binary_structure(3, 2)
        
        # create an erode version of the array
        erode_array = scipy.ndimage.morphology.binary_erosion(array, footprint)
        
        # xor the erode_array with the original and return
        return array ^ erode_array
    