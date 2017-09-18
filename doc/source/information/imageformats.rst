===============================
Supported medical image formats
===============================

.. note::

  You can check you currently supported image formats by running *tests/support.py* from `Github <https://github.com/loli/medpy>`_.

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
