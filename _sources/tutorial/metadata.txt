==================
Accessing metadata
==================
Part of the images metadata can be read from the image data, the remaining from the header object.

>>> from medpy.io import load
>>> image_data, image_header = load('path/to/image.xxx')
>>> image_data.shape
(512, 512, 256)
>>> image_data.dtype
dtype('int16')

Some simple access function provide a common interface to the header, independent of the image type:

>>> from medpy.io import header
>>> header.get_pixel_spacing(image_header)
(0.5, 0.5, 2)
>>> header.get_offset(image_header)
(10, -23, 123)

More metadata is currently not supported by **MedPy**, as the different image formats handle them quite differently.
