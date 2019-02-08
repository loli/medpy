# MedPy

[GitHub](https://github.com/loli/medpy/) | [Documentation](http://loli.github.io/medpy/) | [Tutorials](http://loli.github.io/medpy/) | [Issue tracker](https://github.com/loli/medpy/issues) | [Contact](oskar.maier@gmail.com)

**MedPy** is a library and script collection for medical image processing in Python, providing basic functionalities for **reading**, **writing** and **manipulating** large images of **arbitrary dimensionality**.
Its main contributions are n-dimensional versions of popular **image filters**, a collection of **image feature extractors**, ready to be used with [scikit-learn](http://scikit-learn.org), and an exhaustive n-dimensional **graph-cut** package.

* [Installation](#installation)
* [Getting started with the library](#getting-started-with-the-library)
* [Getting started with the scripts](#getting-started-with-the-scripts)
* [Read/write support for medical image formats](#read-write-support-for-medical-image-formats)
* [Requirements](#requirements)
* [License](#license)

## Installation

```bash
sudo apt-get install libboost-python-dev build-essential
pip3 install medpy
```

**MedPy** requires **Python 3** and officially supports Ubuntu as well as other Debian derivatives.
For installation instructions on other operating systems see the [documentation](http://loli.github.io/medpy/).
While the library itself is written purely in Python, the **graph-cut** extension comes in C++ and has it's own requirements. More details can be found in the [documentation](http://loli.github.io/medpy/).

### Using Python 2

**Python 2** is no longer supported. But you can still use the older releases.

```bash
pip install medpy==0.3.0
```

## Getting started with the library

If you already have a medical image whose format is support (see the [documentation](http://loli.github.io/medpy/>) for details), then good.
Otherwise, navigate to http://www.nitrc.org/projects/inia19, click on the *Download Now* button, unpack and look for the *inia19-t1.nii* file. Open it in your favorite medical image viewer (I personally fancy [itksnap](http://www.itksnap.org)) and beware: the INIA19 primate brain atlas.

Load the image

```python
from medpy.io import load
image_data, image_header = load('/path/to/image.xxx')
```

The data is stored in a numpy ndarray, the header is an object containing additional metadata, such as the voxel-spacing. Now lets take a look at some of the image metadata

```python
image_data.shape
```

`(168, 206, 128)`

```python
image_data.dtype
```

`dtype(float32)`

And the header gives us

```python
from medpy.io import header
header.get_pixel_spacing(image_header)
```

`(0.5, 0.5, 0.5)`

```python
header.get_offset(image_header)
```

`(0.0, 0.0, 0.0)`

Now lets apply one of the **MedPy** filter, more exactly the [Otsu thresholding](https://en.wikipedia.org/wiki/Otsu%27s_method), which can be used for automatic background removal

```python
from medpy.filter import otsu
threshold = otsu(image_data)
output_data = image_data > threshold
```

And save the binary image, marking the foreground

```python
from medpy.io import save
save(output_data, '/path/to/otsu.xxx', image_header)
```

After taking a look at it, you might want to dive deeper with the tutorials found in the [documentation](http://loli.github.io/medpy/).

## Getting started with the scripts

**MedPy** comes with a range of read-to-use commandline scripts, which are all prefixed by `medpy_`.
To try these examples, first get an image as described in the previous section. Now call

```bash
medpy_info.py /path/to/image.xxx
```

will give you some details about the image. With

```bash
medpy_diff.py /path/to/image1.xxx /path/to/image2.xxx
```

you can compare two image. And

```bash
medpy_anisotropic_diffusion.py /path/to/image.xxx /path/to/output.xxx
```

lets you apply an edge preserving anisotropic diffusion filter. For a list of all scripts, see the [documentation](http://loli.github.io/medpy/).


## Read/write support for medical image formats

MedPy builds on 3rd party modules to load and save images. Currently
implemented are the usages of

* NiBabel
* PyDicom
* ITK

, each of which supports the following formats.

**NiBabel** enables support for:

* NifTi - Neuroimaging Informatics Technology Initiative (.nii, nii.gz)
* Analyze (plain, SPM99, SPM2) (.hdr/.img, .img.gz)
* and some others more (http://nipy.org/nibabel/)

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

## Requirements

MedPy comes with a number of dependencies and optional functionality that can require you to install additional packages.

### Main dependencies

* [scipy](http://www.scipy.org)
* [numpy](http://www.numpy.org)
* [nibabel](http://nipy.org/nibabel/) (enables support for NIfTI and Analyze image formats)
* [pydicom](https://pydicom.github.io/) (enables support for DICOM image format)

### Optional functionalities

* compilation with `max-flow/min-cut` (enables the GraphCut functionalities)
* [itk](http://www.itk.org)_ >= 3.16.0 with Python bindings (enables support for a large number of image formats)

## License

MedPy is distributed under the GNU General Public License, a version of which can be found in the LICENSE.txt file.
