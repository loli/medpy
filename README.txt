=========
  MedPy
=========

**MedPy** is a library and script collection for medical image processing
in Python. It contains basic functionalities for reading, writing and
manipulating large images of arbitrary dimensions.

Additionally some image manipulation scripts are installed under the
*medpy_*-prefix which offer various functionalities.

One of the central usages is graph-cuts for image segmentation. **Medpy** 
implements a voxel based standard and a label based version.

Code
====
You can find our sources and single-click downloads:

* `Main repository <https://github.com/loli/medpy>`_ on Github.
* API documentation for all releases and current development tree can be created using `Doxygen <http://www.doxygen.org>`_
* Download as a zip file the `current trunk <https://github.com/loli/medpy/archive/master.zip>`_.

Installation
============
Note that MedPy requires *boost.python* (http://www.boost.org/doc/libs/1_53_0/libs/python/doc/index.html) to be installed. All major Linux distributions have this in their repositories. Then
simply run::

	easy_install medpy

which will install **MedPy** and all required dependencies.
Alternatively it is possible to download the package from here, unpack an run::

	python setup.py install

, in which case you will have to install the `Dependencies`_ on your own.

See `Installing recommendations`_ for information on how to install the recommendations.

Dependencies
============

* `scipy <http://www.scipy.org/>`_ >= 0.9.0
* `numpy <http://www.numpy.org/>`_ >= 1.6.1

Recommendations
===============

* `nibabel <http://nipy.sourceforge.net/nibabel//>`_ >= 1.3.0
* `pydicom <http://code.google.com/p/pydicom/>`_ >= 0.9.7
* `itk <http://www.itk.org/>`_ >= 3.16.0 with `WrapITK <http://code.google.com/p/wrapitk/>`_

Recommendations and image read/write support
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

For some funtionalities, which are collected in the *medpy.itkvtk* package **ITK** is also required. This includes beside others the watershed filter for label graph-cuts.


Installing recommendations
==========================
*nibabel* and *pydicom* are both available over the Package Index PyPi. *itk* is a segmentation & registration toolkit written in C++ which can be compiled with Python wrappers. These steps are more complicated and therefore described in some details.

1. Installing ITK with Python binding on Ubuntu (>= 10.04)
**********************************************************
The Ubuntu repositories provide a package which can simply be installed using::
	
	sudo apt-get install python-insighttoolkit3

But this package wraps only a subset of ITKs functionality and therefore does not unleash **MedPy** s complete power. The recommendation is to follow the second or third approach.

2. Installing ITK with Python binding on Ubuntu (= 12.04)
*********************************************************
If you are running Ubuntu 12.04, you can simply contact the author who will provide you with a pre-compiled Ubuntu package.

3. Compiling ITK with Python bindings on POSIX/Unix platforms
*************************************************************
All descriptions are for ITK 3.20 but might also be valid for newer versions.

Getting ITK
-----------
Got to http://www.itk.org/ITK/resources/software.html , download the *InsightToolkit-3.20.1.tar.gz* resp. *InsightToolkit-3.20.1.zip* archive and unpack it to a folder called somthing like *IKT3.20.1/src*.

Configuring ITK
---------------
Compiling ITK requires *cmake* which can be found for almost all platforms. Create a new directory *IKT3.20.1/build* and enter it. Then run::

	ccmake ../src

and subsequently hit the *c* key to configure the build. When finished, hit the *t* key to toggle the advanced mode and activate the following options::

	BUILD_SHARED_LIBS ON
	ITK_USE_REVIEW	  ON
	USE_WRAP_ITK	  ON

, then *c* onfigure again. Ignore the warning by pressing *e*. Now set the following options::

	WRAP_FFT	    OFF
	WRAP_ITK_DIMS	    2;3;4 (or more, if you require)
	WRAP_ITK_JAVA	    OFF
	WRAP_ITK_PYTHON	    ON
	WRAP_ITK_TCL	    OFF

	WRAP_double         ON
	WRAP_float          ON
	WRAP_signed_char    ON
	WRAP_signed_long    ON
	WRAP_signed_short   ON
	WRAP_unsigned_char  ON
	WRAP_unsigned_long  ON
	WRAP_unsigned_short ON
	WRAP_<datatype>	  Select yourself which more to activate.

, and *c* onfigure another time. Finally press *g* to generate the make-file.

If *cmake* signals any errors during the configuration process, try to resolve the dependencies from which they originate.

Compiling ITK
-------------
Now that the configuration is done, we can compile ITK. Run::

	make -j<number-of-your-porcessors>

and wait. This will take some time, depending on your computer up to 2 days are not unlikely.


If an error occurs, try to understand it and eventually re-run the previpous step with some options changed.

Installing ITK
--------------
Install ITK and its Python bindings simply by running::

	make install (as root)

Addditional step
----------------
The ITK Python bindings require a third-party module called PyBuffer which is shipped with ITK but not automatically compiled. Furthermore it holds a small bug. After finishing the previous steps, create a folder called *PyBuffer/src* somewhere and copy all files and folders from *ITK/src/Wrapping/WrapITK/ExternalProjects/PyBuffer/* into it. Now open *itkPyBuffer.txx* with an text editor and change the line::
	
	int dimensions[ ImageDimension ];

to::

	npy_intp dimensions[ ImageDimension ];

(see http://code.google.com/p/wrapitk/issues/detail?id=39 for patch details). Then create a folder *PyBuffer/build*, enter it and run::

	ccmake ../src

After *c* onfiguring you will see some warnings. Set::

	WrapITK_DIR	ITK/bin/Wrapping/WrapITK/

In some cases you will also have to set::

	PYTHON_NUMARRAY_INCLUDE_DIR	/usr/include/numpy

Now *c* onfigure again and *g* enerate. To finalize run::

	make
	make install (as root)

Congratulations, you are done compiling and installing ITK with Python wrappers.

License
=======
MedPy is distributed under the GNU General Public License, a version of which can be found in the LICENSE.txt file.

Library examples
================

Simple example
**************

Typical usage often looks like this::

    #!/usr/bin python

    from medpy.io import load, save

    # load input image no.1
    data_input1, header_input1 = load(args.input)

    # load input image no.2
    data_input2, header_input2 = load(args.input)

    # substract to create difference image
    data_output = data_input1 - data_input2

    # save resulting image
    save(data_output, "/location/output.nii", header_input1, FALSE)

Script examples
===============

Voxel-based graph-cut
*********************
To segment an object in an image using voxel-based graph cuts, the first step is to create some marker image depicting foreground and background of the object, where all ones (1) depict foreground and all twos (2) background. This can be done with any image tool. The graphcut can then be executed using::
	
	medpy_graphcut_voxel.py 10.0 original_image.dcm marker_image.dcm result_image.dcm 

, where the output is a binary image depicting the object in the original image.

Region-based graph-cut
**********************
These version executes the graph-cut on regions/labels rather than single pixel. It performs therefore substantially faster at a low accuracy cost. For this the original image has first to be split into regions using::

	medpy_gradient.py original_image.dcm gradient_image.dcm

	medpy_itk_watershed.py gradient_image.dcm watershed_image.dcm

The cut itself again required foreground and background markers as in the voxel-based example. The cut is then executed using::
	
	medpy_graphcut_label.py gradient_image.dcm watershed_image.dcm marker_image.dcm result_image.dcm 

, where the output is a binary image depicting the object in the original image.


