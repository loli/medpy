=========
  MedPy
=========

MedPy is a library and script collection for medical image processing
in Python. It contains basic functionalities for reading, writing and
manipulating large images of arbitrary dimensions.

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

Paragraphs are separated by blank lines. *Italics*, **bold**,
and ``monospace`` look like this.


A Section
=========

Lists look like this:

* First

* Second. Can be multiple lines
  but must be indented properly.

Urls are http://like.this and links can be
written `like this <http://www.example.com/foo/bar>`_.

Reading/writing image and supported formats
-------------

MedPy builds on 3rd party modules to load and save images. Currently
implemented are the usages of

* NiBabel
* PyDicom
* WrapITK

, each of which supports the following formats

**NiBabel** enables support for:
* NifTi - Neuroimaging Informatics Technology Initiative (.nii, nii.gz)
* Analyze (plain, SPM99, SPM2) (.hdr/.img, .img.gz)
* and some others more (http://nipy.sourceforge.net/nibabel/)
**PyDicom** enables support for:
* Dicom - Digital Imaging and Communications in Medicine (.dcm, .dicom)
**WrapITK** enables support for:
* NifTi - Neuroimaging Informatics Technology Initiative (.nii, nii.gz)
* Analyze (plain, SPM99, SPM2) (.hdr/.img, .img.gz)
* Dicom - Digital Imaging and Communications in Medicine (.dcm, .dicom)
* Itk/Vtk MetaImage (.mhd, .mha/.raw)
* Nrrd - Nearly Raw Raster Data (.nhdr, .nrrd)
* and many others more (http://www.cmake.org/Wiki/ITK/File_Formats)

These modules have to be installed seperately. **NiBabel** and **PyDicom** are
the prefered, faster packages and available under PyPi and can be easily
installed using

    easy_install nibabel

respectively

    easy_install pydicom

The easy_install script belongs to the Python setup tools. Under Ubuntu these
can be easily obtained using

    apt-get install python-setuptools

**ITK** (The Insight Toolkit) is a large C++ libarary for medical image processing
and includes Python wrappers. It can either be compiled on your own or (under Ubuntu)
installed via

    apt-get install python-insighttoolkit3

