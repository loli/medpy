=========
  MedPy
=========

**MedPy** is a library and script collection for medical image processing in Python, providing basic functionalities for **reading**, **writing** and **manipulating** large images of **arbitrary dimensionality**.
Its main contributions are n-dimensional versions of popular **image filters**, a collection of **image feature extractors**, ready to be used with `scikit-learn <http://scikit-learn.org/>`_, and an exhaustive n-dimensional **graph-cut** package.

**Troubles?** Feel free to write me with any questions / comments / suggestions: oskar.maier@googlemail.com

**Found a bug?** https://github.com/loli/medpy/issues


Installing MedPy the fast way (Ubuntu and derivatives)
======================================================
First::

    sudo apt-get install python-pip python-numpy python-scipy libboost-python-dev build-essential
    
Then::

    sudo pip install nibabel pydicom medpy
 
Done. More installation instructions can be found in the `documentation <http://pythonhosted.org/MedPy/>`_.


Getting started with the library
================================
If you already have one, whose format is support (see in the `documentation <http://pythonhosted.org/MedPy/>`_.), then good.
Otherwise navigate to http://www.nitrc.org/projects/inia19, click on the *Download Now* button, unpack and look for the *inia19-t1.nii* file.
Open it in your favorite medical image viewer (I personally fancy `itksnap <http://www.itksnap.org>`_) and beware a the INIA19 primate brain atlas.

Load the image

>>> from medpy.io import load
>>> image_data, image_header = load('/path/to/image.xxx')

The data is stored in a numpy ndarray, the header is an object containing additional metadata, such as the voxel-spacing.
No lets take a look at some of the image metadata

>>> image_data.shape
(168, 206, 128)
>>> image_data.dtype
dtype(float32)

And the header gives us

>>> from medpy.io import header
>>> header.get_pixel_spacing(image_header)
(0.5, 0.5, 0.5)
>>> header.get_offset(image_header)
(0.0, 0.0, 0.0)

Now lets apply one of the **MedPy** filter, more exactly the Otsu thresholding, which can be used for automatic background removal

>>> from medpy.filter import otsu
>>> threshold = otsu(image_data)
>>> output_data = image_data > threshold

And save the binary image, marking the foreground

>>> from medpy.io import save
>>> save(output_data, '/path/to/otsu.xxx', image_header)

After taking a look at it, you might want to dive deeper with the `documentation <http://pythonhosted.org/MedPy/>`_.


Getting started with the library
================================
Get an image as described above. Now::

	medpy_info.py /path/to/image.xxx
	
will give you some details about the image. With::

	medpy_diff.py /path/to/image1.xxx /path/to/image2.xxx

you can compare two image. And::

	medpy_anisotropic_diffusion.py /path/to/image.xxx /path/to/output.xxx
	
lets you apply an edge preserving anisotropic diffusion filter. For a list of all scripts, see the `documentation <http://pythonhosted.org/MedPy/>`_.


Read/write support for medical image formats
============================================
MedPy builds on 3rd party modules to load and save images. Currently
implemented are the usages of

* NiBabel
* PyDicom
* ITK

, each of which supports the following formats.

**NiBabel** enables support for:

* NifTi - Neuroimaging Informatics Technology Initiative (.nii, nii.gz)
* Analyze (plain, SPM99, SPM2) (.hdr/.img, .img.gz)
* and some others more (http://nipy.sourceforge.net/nibabel/)

**PyDicom** enables support for:

* Dicom - Digital Imaging and Communications in Medicine (.dcm, .dicom)

**ITK** enables support for:

* NifTi - Neuroimaging Informatics Technology Initiative (.nii, nii.gz)
* Analyze (plain, SPM99, SPM2) (.hdr/.img, .img.gz)
* Dicom - Digital Imaging and Communications in Medicine (.dcm, .dicom)
* Itk/Vtk MetaImage (.mhd, .mha/.raw)
* Nrrd - Nearly Raw Raster Data (.nhdr, .nrrd)
* and many others more (http://www.cmake.org/Wiki/ITK/File_Formats)

For some functionalities, which are collected in the *medpy.itkvtk* package **ITK** is also required.


Code
====
You can find our sources and single-click downloads:

* `Main repository <https://github.com/loli/medpy>`_ on Github.
* API documentation for all releases and current development tree can be created using `Doxygen <http://www.doxygen.org>`_
* Download as a zip file the `current trunk <https://github.com/loli/medpy/archive/master.zip>`_.


Tutorials and API Documentation
===============================
http://pythonhosted.org/MedPy 

Requirements
============
MedPy comes with a number of dependencies and optional functionality that can require you to install additional packages.

Dependencies
------------

* `scipy <http://www.scipy.org/>`_ >= 0.9.0
* `numpy <http://www.numpy.org/>`_ >= 1.6.1

Recommendations
---------------
* `nibabel <http://nipy.sourceforge.net/nibabel//>`_ >= 1.3.0 (enables support for NIfTI and Analyze image formats)
* `pydicom <http://code.google.com/p/pydicom/>`_ >= 0.9.7 (enables support for DICOM image format)

Optional functionalities
------------------------
* compilation with `max-flow/min-cut` (enables the GraphCut functionalities)
* `itk <http://www.itk.org/>`_ >= 3.16.0 with `WrapITK <http://code.google.com/p/wrapitk/>`_ (enables support for a large number of image formats)


License
=======
MedPy is distributed under the GNU General Public License, a version of which can be found in the LICENSE.txt file.

