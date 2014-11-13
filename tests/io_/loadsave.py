"""Unittest for the input/output facilities class."""

# build-in modules
import unittest
import tempfile
import os

# third-party modules
import scipy


# path changes

# own modules
from medpy.io import load, save
from medpy.core.logger import Logger

# information
__author__ = "Oskar Maier"
__version__ = "r0.1.2, 2012-05-25"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = "Input/output facilities unittest."

# code
class TestIOFacilities(unittest.TestCase):
    
    ####
    # Comprehensive list of image format endings
    ####
    # The most important image formats for medical image processing
    __important = ['.nii', '.nii.gz', '.hdr', '.img', '.img.gz', '.dcm', '.dicom', '.mhd', '.nrrd', '.mha']
    
    # some image format potentially manageable by pydicom
    __pydicom = ['.dcm', '.dicom']
    
    # some image format potentially manageable by nibabel
    __nifti = ['.nii', '.nii.gz', '.hdr', '.img', '.img.gz']
    
    # some more image format potentially manageable by itk
    __itk_more = ['.vtk', '.lsm', '.pic']
    
    # list of image formats ITK is theoretically able to load
    __itk = ['.analyze', # failed saving
             '.hdr',
             '.img',
             '.bmp',
             '.dcm',
             '.gdcm', # failed saving
             '.dicom',
             '.4x', # failed saving
             '.5x', # failed saving
             '.ge', # failed saving
             '.ge4x', # failed saving
             '.ge5x', # failed saving
             '.gipl',
             '.ipl', # failed saving
             '.jpg',
             '.jpeg',
             '.mha',
             '.mhd',
             '.png',
             '.raw', # failed saving
             '.vision', # failed saving
             '.siemens', # failed saving
             '.spr',
             '.sdt', # failed saving
             '.stimulate', # failed saving
             '.tif',
             '.tiff',
             '.bio', # failed saving
             '.biorad', # failed saving
             '.brains', # failed saving
             '.brains2', # failed saving
             '.brains2mask', # failed saving
             '.bruker', # failed saving
             '.bruker2d', # failed saving
             '.bruker2dseq', # failed saving
             '.mnc', # failed saving
             '.mnc2', # failed saving
             '.minc', # failed saving
             '.minc2', # failed saving
             '.nii',
             '.nifti', # failed saving
             '.nhdr',
             '.nrrd',
             '.philips', # failed saving
             '.philipsreq', # failed saving
             '.rec', # failed saving
             '.par', # failed saving
             '.recpar', # failed saving
             '.vox', # failed saving
             '.voxbo', # failed saving
             '.voxbocub'] # failed saving    
    
    ##########
    # Combinations to avoid due to technical problems, dim->file ending pairs
    #########
    __avoid = {4: ('.dcm', '.dicom')} # at least in version 3.16, trying to save a more than 3D dicom results in a memory corruption instead of an error
    
    def test_SaveLoad(self):
        """
        The bases essence of this test is to check if any one image format in any one
        dimension can be saved and read, as this is the only base requirement for using
        medpy.
        
        Additionally checks the basic expected behaviour of the load and save
        functionality.
        
        Since this usually does not make much sense, this implementation allows also to
        set a switch (verboose) which causes the test to print a comprehensive overview
        over which image formats with how many dimensions and which pixel data types
        can be read and written.
        """
        ####
        # VERBOOSE SETTINGS
        # The following are three variables that can be used to print some nicely
        # formatted additional output. When one of them is set to True, this unittest
        # should be run stand-alone.
        ####
        # Print a list of supported image types, dimensions and pixel data types
        supported = True
        # Print a list of image types that were tested but are not supported
        notsupported = False
        # Print a list of image type, dimensions and pixel data types configurations,
        # that seem to work but failed the consistency tests. These should be handled
        # with special care, as they might be the source of errors.
        inconsistent = True
        
        ####
        # OTHER SETTINGS
        ####
        # debug settings
        logger = Logger.getInstance()
        #logger.setLevel(logging.DEBUG)
        
        # run test either for most important formats or for all
        #__suffixes = self.__important # (choice 1)
        __suffixes = self.__pydicom + self.__nifti + self.__itk + self.__itk_more # (choice 2)
        
        
        # dimensions and dtypes to check
        __suffixes = list(set(__suffixes))
        __ndims = [1, 2, 3, 4, 5]
        __dtypes = [scipy.bool_,
                    scipy.int8, scipy.int16, scipy.int32, scipy.int64,
                    scipy.uint8, scipy.uint16, scipy.uint32, scipy.uint64,
                    scipy.float32, scipy.float64,
                    scipy.complex64, scipy.complex128]
        
        # prepare struct to save settings that passed the test
        valid_types = dict.fromkeys(__suffixes)
        for k1 in valid_types:
            valid_types[k1] = dict.fromkeys(__ndims)
            for k2 in valid_types[k1]:
                valid_types[k1][k2] = []
        
        # prepare struct to save settings that did not
        unsupported_type = dict.fromkeys(__suffixes)
        for k1 in unsupported_type:
            unsupported_type[k1] = dict.fromkeys(__ndims)
            for k2 in unsupported_type[k1]:
                unsupported_type[k1][k2] = dict.fromkeys(__dtypes)        
        
        # prepare struct to save settings that did not pass the data integrity test
        invalid_types = dict.fromkeys(__suffixes)
        for k1 in invalid_types:
            invalid_types[k1] = dict.fromkeys(__ndims)
            for k2 in invalid_types[k1]:
                invalid_types[k1][k2] = dict.fromkeys(__dtypes)
        
        # create artifical images, save them, load them again and compare them
        path = tempfile.mkdtemp()
        try:
            for ndim in __ndims:
                logger.debug('Testing for dimension {}...'.format(ndim))
                arr_base = scipy.random.randint(0, 10, list(range(10, ndim + 10)))
                for dtype in __dtypes:
                    arr_save = arr_base.astype(dtype)
                    for suffix in __suffixes:
                        # do not run test, if in avoid array
                        if ndim in self.__avoid and suffix in self.__avoid[ndim]:
                            unsupported_type[suffix][ndim][dtype] = "Test skipped, as combination in the tests __avoid array."
                            continue
                        
                        image = '{}/img{}'.format(path, suffix)
                        try:
                            # attempt to save the image
                            save(arr_save, image)
                            self.assertTrue(os.path.exists(image), 'Image of type {} with shape={}/dtype={} has been saved without exception, but the file does not exist.'.format(suffix, arr_save.shape, dtype))
                                   
                            # attempt to load the image
                            arr_load, header = load(image)
                            self.assertTrue(header, 'Image of type {} with shape={}/dtype={} has been loaded without exception, but no header has been supplied (got: {})'.format(suffix, arr_save.shape, dtype, header))
                            
                            # check for data consistency
                            msg = self.__diff(arr_save, arr_load)
                            if msg:
                                invalid_types[suffix][ndim][dtype] = msg
                            #elif list == type(valid_types[suffix][ndim]):
                            else:
                                valid_types[suffix][ndim].append(dtype)
                            
                            # remove image
                            if os.path.exists(image): os.remove(image)
                        except Exception as e: # clean up
                            unsupported_type[suffix][ndim][dtype] = e.message
                            if os.path.exists(image): os.remove(image)
        except Exception:
            if not os.listdir(path): os.rmdir(path)
            else: logger.debug('Could not delete temporary directory {}. Is not empty.'.format(path))
            raise
        
        if supported:
            print('\nsave() and load() support (at least) the following image configurations:')
            print('type\tndim\tdtypes')
            for suffix in valid_types:
                for ndim, dtypes in valid_types[suffix].items():
                    if list == type(dtypes) and not 0 == len(dtypes):
                        print('{}\t{}D\t{}'.format(suffix, ndim, [str(x).split('.')[-1][:-2] for x in dtypes]))
        if notsupported:
            print('\nthe following configurations are not supported:')
            print('type\tndim\tdtype\t\terror')
            for suffix in unsupported_type:
                for ndim in unsupported_type[suffix]:
                    for dtype, msg in unsupported_type[suffix][ndim].items():
                        if msg:
                            print('{}\t{}D\t{}\t\t{}'.format(suffix, ndim, str(dtype).split('.')[-1][:-2], msg))
            
        if inconsistent:
            print('\nthe following configurations show inconsistent saving and loading behaviour:')
            print('type\tndim\tdtype\t\terror')
            for suffix in invalid_types:
                for ndim in invalid_types[suffix]:
                    for dtype, msg in invalid_types[suffix][ndim].items():
                        if msg:
                            print('{}\t{}D\t{}\t\t{}'.format(suffix, ndim, str(dtype).split('.')[-1][:-2], msg))
        
    def __diff(self, arr1, arr2):
        """
        Returns an error message if the two supplied arrays differ, otherwise false.
        """ 
        if not arr1.ndim == arr2.ndim:
            return 'ndim differs ({} to {})'.format(arr1.ndim, arr2.ndim)
        elif not self.__is_lossless(arr1.dtype.type, arr2.dtype.type):
            return 'loss of data due to conversion from {} to {}'.format(arr1.dtype.type, arr2.dtype.type)
        elif not arr1.shape == arr2.shape:
            return 'shapes differs ({} to {}).'.format(arr1.shape, arr2.shape)
        elif not (arr1 == arr2).all():
            return 'contents differs'
        else: return False
    
    def __is_lossless(self, _from, _to):
        """
        Returns True if a data conversion from dtype _from to _to is lossless, otherwise
        False.
        """
        __int_order = [scipy.int8, scipy.int16, scipy.int32, scipy.int64]
        
        __uint_order = [scipy.uint8, scipy.int16, scipy.uint16, scipy.int32, scipy.uint32, scipy.int64, scipy.uint64]
        
        __float_order = [scipy.float32, scipy.float64, scipy.float128]
        
        __complex_order = [scipy.complex64, scipy.complex128, scipy.complex256]
        
        __bool_order = [scipy.bool_, scipy.int8, scipy.uint8, scipy.int16, scipy.uint16, scipy.int32, scipy.uint32, scipy.int64, scipy.uint64]
        
        __orders = [__int_order, __uint_order, __float_order, __complex_order, __bool_order]
        
        for order in __orders:
            if _from in order:
                if _to in order[order.index(_from):]: return True
                else: return False
        return False
        
    
if __name__ == '__main__':
    unittest.main()
