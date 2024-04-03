===============================
Supported medical image formats
===============================

.. note::

  You can check your currently supported image formats by grabbing the source code from `Github <https://github.com/loli/medpy/>`_ and running *python3 tests/support.py*.

**MedPy** relies on *SimpleITK*, which enables the power of ITK for image loading and saving.
The supported image file formats should include at least the following.

Medical formats:

- ITK MetaImage (.mha/.raw, .mhd)
- Neuroimaging Informatics Technology Initiative (NIfTI) (.nia, .nii, .nii.gz, .hdr, .img, .img.gz)
- Analyze (plain, SPM99, SPM2) (.hdr/.img, .img.gz)
- Digital Imaging and Communications in Medicine (DICOM) (.dcm, .dicom)
- Digital Imaging and Communications in Medicine (DICOM) series (<directory>/)
- Nearly Raw Raster Data (Nrrd) (.nrrd, .nhdr)
- Medical Imaging NetCDF (MINC) (.mnc, .MNC)
- Guys Image Processing Lab (GIPL) (.gipl, .gipl.gz)

Microscopy formats:

- Medical Research Council (MRC) (.mrc, .rec)
- Bio-Rad (.pic, .PIC)
- LSM (Zeiss) microscopy images (.tif, .TIF, .tiff, .TIFF, .lsm, .LSM)
- Stimulate / Signal Data (SDT) (.sdt)

Visualization formats:

- VTK images (.vtk)

Other formats:

- Portable Network Graphics (PNG) (.png, .PNG)
- Joint Photographic Experts Group (JPEG) (.jpg, .JPG, .jpeg, .JPEG)
- Tagged Image File Format (TIFF) (.tif, .TIF, .tiff, .TIFF)
- Windows bitmap (.bmp, .BMP)
- Hierarchical Data Format (HDF5) (.h5 , .hdf5 , .he5)
- MSX-DOS Screen-x (.ge4, .ge5)

For informations about which image formats, dimensionalities and pixel data types
your current configuration supports, run `python3 tests/support.py > myformats.log`.

Further information see https://simpleitk.readthedocs.io .
