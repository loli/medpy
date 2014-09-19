=========================
Loading and saving images
=========================
The image loading/saving facilities can be found in :mod:`medpy.io`. Loading an image is straightforward with `~medpy.io.load`:

>>> from medpy.io import load
>>> image_data, image_header = load('path/to/image.xxx')

``image_data`` is a ``numpy`` ``ndarray`` with the image data and ``image_header`` is a header object holding the associated metadata.

Now, to save the image, use `~medpy.io.save.save`:

>>> from medpy.io import load, save
>>> save(image_data, 'path/to/image.xxx', image_header)

The image format is automatically deducted from the file ending.
