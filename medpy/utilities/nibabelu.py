#!/usr/bin/python

"""Holds a number of utility function to process NiBabel images."""

# build-in modules

# third-party modules
from nibabel.spatialimages import SpatialImage 

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "d0.2.0, 2011-12-12"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development" # tested functions marked with tested keyword
__description__ = "NiBabel image utility functions."

# code
def image(data):
    """
    Creates a NiBabel image for the supplied data. The image object will be of a generic
    type and only made concrete during the saving process (nibabel.loadsave.save() takes
    care of this).
    @param data: a numpy array of arbitrary type
    @return: a NiBabel image for data of generic type SpatialImage
    """
    image = SpatialImage(data, None)
    image.update_header()
    return image

def image_like(data, reference):
    """
    Creates a NiBabel image for the data of the same type as image. Where the data
    is not sufficient to provide required information, the header attributes of image
    are used.
    @param data: a numpy array of arbitrary type
    @param image: a NiBabel image
    @param origin: the images origin that should get set, if None the one from the
                   reference header is used
    @return: a NiBabel image for data of same type as image
    """
    # !TODO: Check if this covers all know cases i.e. if the data can contain
    # information that is not used.
    header = reference.get_header().copy()
    #affine = reference.get_affine()
    # !TODO: This is not working correct: Somehow ItkSnap shows x/y origins to be negative. Why?
    #if None != origin: affine[:len(origin),-1] = origin
    image = reference.__class__(data, None, header=header)
    image.update_header()
    # !TODO: Is the following required? Works only for Nifty1. See the Nifty1 documentation/definition.
    #image.get_header()['qoffset_x'] = origin[0]
    #image.get_header()['qoffset_y'] = origin[1]
    #image.get_header()['qoffset_z'] = origin[2]
    return image