"""
@package medpy.io.imagehader
Holds a image header object used to store meta information about an image.

@author Oskar Maier
@version d0.1.0
@since 2012-05-28
@status Development
"""

# build-in modules

# third-party modules

# own modules
from ..core import Logger

class ImageHeader (object):
    """
    A class representing a simple image header. Can be used to access and set some
    information about a loaded image and to save an image by example of another.
    """
    def __init__(self, original_header = False):
        """
        Create a new ImageHeader.
        The base informations are extracted from the supplied array, others have to be
        set manually.
        
        If the image has been loaded, the original header can be passed to the object.
        If existing, the information from this header is passed to the image save
        function.
        
        @param arr the scipy array of the image
        @param original_header the original header associated with the image if loaded
        """
        self.__original_header = original_header
        self.__slice_spacing = False
        self.__origin = False
    
    def get_slice_spacing(self):
        """
        @return The slice spacing of the image. If not known, 1 is assumed.
        """
        if not self.__slice_spacing:
            logger = Logger.getInstance()
            logger.info('The image slice spacing is a default value and might differ from the real slice spacing.')
            return self.__dimensions * [1]
        else:
            return self.__slice_spacing
        
    def get_origin(self):
        """
        @return The origin of the image. If not known, 0 is assumed.
        """
        if not self.__origin:
            logger = Logger.getInstance()
            logger.info('The image origin is a default value and might differ from the real origin.')
            return self.__dimensions * [0]
        else:
            return self.__origin
        
    def get_original_header(self):
        """
        @return The original image header. Can be of any type of False, if missing.
        """
        return self.__original_header
    
    def set_original_header(self, original_header):
        """
        @param The original image header. Can be of any type of False to delete.
        """
        self.__original_header = original_header   
    
    def set_slice_spacing(self, slice_spacing):
        """
        @param slice_spacing A sequence of number determining the slice spacing of the
                             image. If not valid is silently ignored.
        """
        try:
            if not self.__dimensions == len(slice_spacing):
                return
            self.__slice_spacing = list(map(float, slice_spacing))
        except TypeError:
            return
        
    def set_origin(self, origin):
        """
        @param origin A sequence of number determining the origin of the image. If not
                      valid is silently ignored.
        """
        try:
            if not self.__dimensions == len(origin):
                return
            self.__origin = list(map(float, origin))
        except TypeError:
            return
    