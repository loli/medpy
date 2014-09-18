=========
  MedPy
=========

**MedPy** is a library and script collection for medical image processing in Python. It contains basic functionalities for reading, writing and manipulating large images of arbitrary dimensions.

Additionally some image manipulation scripts are installed under the *medpy_*-prefix which offer various functionalities. See https://github.com/loli/medpy/wiki for a complete list. 

One of the central usages is graph-cuts for image segmentation. **Medpy**  implements a voxel based standard and a label based version.

For some simple examples and further instructions, see also the `Wiki <https://github.com/loli/medpy/wiki>`_.

**Troubles?** Feel free to write me with any questions / comments / suggestions: oskar.maier@googlemail.com


Code
====
You can find our sources and single-click downloads:

* `Main repository <https://github.com/loli/medpy>`_ on Github.
* API documentation for all releases and current development tree can be created using `Doxygen <http://www.doxygen.org>`_
* Download as a zip file the `current trunk <https://github.com/loli/medpy/archive/master.zip>`_.


API Documentation
=================
http://pythonhosted.org/MedPy
See especially the sections `Packages` and `Package Functions`. 


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


Installing the dependencies
===========================
The dependencies will be automatically installed and compiled when installing **MedPy**. But *numpy* and *scipy* both have their own dependencies, that are not always easy to meet.
Luckily, most Unix distributions have them in their repositories. E.g. in Ubuntu, you can install them by calling::

	sudo apt-get install python-numpy python-scipy

Alternatively, your can find an installation instruction with all dependencies listed here: http://www.scipy.org/scipylib/building/linux.html

Global installation
===================
Note that the global installation makes **MedPy** available for all users and requires root privileges.  

Installation using `PIP <https://pypi.python.org/pypi/pip>`_
------------------------------------------------------------
Call::

	pip install medpy

Installation using `easy_install <https://pypi.python.org/pypi/setuptools>`_
----------------------------------------------------------------------------
Call::

	easy_install medpy

Installation from source
------------------------
Download the sources from https://pypi.python.org/pypi/MedPy/, unpack them, enter the directory and run::

	python setup.py install


Local installation
==================
The local install will place **MedPy** in your user site-packages directory and does not require root privileges. You can find our the location of your personal site-packages directory by calling::

	python -c 'import site;print site.USER_SITE'
	
In some cases, the Python configuration does not find packages in the users site-packages directory, in which case you will have to add it to your PYTHONPATH variable. To make this permanent, add the extension to your `.bashrc`, e.g. using::

	echo "export PYTHONPATH=${PYTHONPATH}:$( python -c 'import site;print site.USER_SITE' )" >> ~/.bashrc
	
More importantly, the script shipped with **MedPy** won't be in your PATH and hence can not be used directly. If your user site-packages directory is e.g. `/home/<user>/.local/lib/python2.7/site-packages/`, the scripts are most likely to be found under `/home/<user>/.local/bin/`. Add this directory to your PATH using::

	 echo "export PATH=${PATH}:/home/<user>/.local/bin/" >> ~/.bashrc
	 
(Don't forget to replace <user> with your own user name.)	

Installation using `pip <https://pypi.python.org/pypi/pip>`_
------------------------------------------------------------
Call::

	pip install --user medpy

Installation using `easy_install <https://pypi.python.org/pypi/setuptools>`_
----------------------------------------------------------------------------
Call::
	
	easy_install --user medpy

Installation from source
------------------------
Download the sources from https://pypi.python.org/pypi/MedPy/, unpack them, enter the directory and run::

	python setup.py install --user


Development installation
========================
If you care to work on the source directly, you can install **MedPy** in development mode. Then the sources will remain and any changes made them them be directly available system-wide.

Installation from source
------------------------
Download the sources from https://pypi.python.org/pypi/MedPy/, unpack them, enter the directory and run::

	python setup.py develop
	

Uninstall
=========
Only `pip` supports the removal of Python packages. If you have installed **MedPy** by other means, you will have to remove the package manually. With `pip`, call simply::

	pip uninstall medpy


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


Installing recommendations
==========================
*nibabel* and *pydicom* are both available over the Package Index PyPi::

	pip install nibabel pydicom

or::

	easy_install nibabel pydicom

Installing with GraphCut support
================================
The GraphCut functionalities of **MedPy** depend on the `max-flow/min-cut library <http://vision.csd.uwo.ca/code/>`_ by Boykov and Kolmogorov. During installation, **MedPy** will try to compile it and its python wrappers. If the compilation fails, **MedPy** will be installed without the GraphCut module.
To enable the GraphCut functionality of **MedPy**, the dependencies of the library must be met *before* installing **MedPy** (although it can always be simply re-installed).

Dependencies
------------
* Boost.Python
* g++
* gcc

These dependencies can be found in the repositories of all major distribution. For e.g. Ubuntu, you can simply call::

	sudo apt-get install python-boost build-essentials
	
	
License
=======
MedPy is distributed under the GNU General Public License, a version of which can be found in the LICENSE.txt file.

Usage examples
==============
See primarily The `Wiki <https://github.com/loli/medpy/wiki>`_ for usage examples.

Simple example
--------------

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
---------------------
To segment an object in an image using voxel-based graph cuts, the first step is to create some marker image depicting foreground and background of the object, where all ones (1) depict foreground and all twos (2) background. This can be done with any image tool. The graphcut can then be executed using::
	
	medpy_graphcut_voxel.py 10.0 original_image.dcm marker_image.dcm result_image.dcm 

, where the output is a binary image depicting the object in the original image.

Region-based graph-cut
----------------------
These version executes the graph-cut on regions/labels rather than single pixel. It performs therefore substantially faster at a low accuracy cost. For this the original image has first to be split into regions using::

	medpy_gradient.py original_image.dcm gradient_image.dcm

	medpy_itk_watershed.py gradient_image.dcm watershed_image.dcm

The cut itself again required foreground and background markers as in the voxel-based example. The cut is then executed using::
	
	medpy_graphcut_label.py gradient_image.dcm watershed_image.dcm marker_image.dcm result_image.dcm 

, where the output is a binary image depicting the object in the original image.	


Installing ITK wrappers
=======================
This is quite some work and absolutely not fail-save. Only try it, if you must (or are bored with too much time at hand).

1. Installing ITK with Python binding on Ubuntu (>= 10.04)
----------------------------------------------------------
The Ubuntu repositories provide a package which can simply be installed using::
	
	sudo apt-get install python-insighttoolkit3

But this package wraps only a subset of ITKs functionality and therefore does not unleash **MedPy** s complete power. The recommendation is to follow the second or third approach.

2. Installing ITK with Python binding on Ubuntu (= 12.04)
---------------------------------------------------------
If you are running Ubuntu 12.04, you can simply contact the author who will provide you with a pre-compiled Ubuntu package.

3. Compiling ITK with Python bindings on POSIX/Unix platforms
-------------------------------------------------------------
All descriptions are for ITK 3.20 but might also be valid for newer versions.

Getting ITK
***********
Got to http://www.itk.org/ITK/resources/software.html , download the *InsightToolkit-3.20.1.tar.gz* resp. *InsightToolkit-3.20.1.zip* archive and unpack it to a folder called somthing like *IKT3.20.1/src*.

Configuring ITK
***************
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
*************
Now that the configuration is done, we can compile ITK. Run::

	make -j<number-of-your-porcessors>

and wait. This will take some time, depending on your computer up to 2 days are not unlikely.


If an error occurs, try to understand it and eventually re-run the previpous step with some options changed.

Installing ITK
**************
Install ITK and its Python bindings simply by running::

	make install (as root)

Addditional step
****************
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

