"""
@package medpy.utilities.nibabelu
Holds a number of utility function to process NiBabel images.

@author Oskar Maier
@version d0.2.1
@since 2011-12-12
@status Development
"""

# build-in modules

# third-party modules
from nibabel.spatialimages import SpatialImage
from nibabel import Nifti1Image, Nifti1Pair

# path changes

# own modules

# constants
__suffix_to_type = {'nii': Nifti1Image, # mapping from file suffix to type string
                    'nii.gz': Nifti1Image,
                    'hdr': Nifti1Pair,
                    'img': Nifti1Pair,
                    'img.gz': Nifti1Pair}

# code
def image(data):
    """
    Creates a NiBabel image for the supplied data. The image object will be of a generic
    type and only made concrete during the saving process (nibabel.loadsave.save() takes
    care of this). No special meta-data can be associated with the image.
    @param data: a numpy array of arbitrary type
    @return: a NiBabel image for data of generic type SpatialImage
    """
    image = SpatialImage(data, None)
    image.update_header()
    return image

def image_new(data, filename):
    """
    Creates a NiBabel image for the supplied data. The function intends to directly
    create the appropriate image type, depending on the image header.
    @param data: a numpy array of arbitrary type
    @param filename the intended filename with the file ending telling the image type
    @return: a NiBabel image for data of any nibabel image type
    """
    # extract suffix and return apropriate image
    suffix = filename.split('.')[-1].lower()
    if not suffix in __suffix_to_type:
        suffix = '.'.join(map(lambda x: x.lower(), filename.split('.')[-2:]))
        if not suffix in __suffix_to_type:
            image = SpatialImage(data, None)
            image.update_header()
            return image
    image = __suffix_to_type[suffix](data, None)
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