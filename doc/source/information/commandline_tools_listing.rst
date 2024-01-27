.. _top:

=========================
List of commandline tools
=========================
MedPy is shipped with a number of python scripts (little programs) that are installed on your system together with MedPy. On this page you can find a short overview over these scripts.
All are prefixed with **medpy_**.

Categories
==========
* :ref:`basic`
* :ref:`volume`
* :ref:`binary`
* :ref:`filter`
* :ref:`mr`
* :ref:`gc`
* :ref:`others`

.. _basic:

Basic image manipulation
========================
:ref:`↑top <top>`

.. topic:: medpy_info.py (`notebook <https://github.com/loli/medpy/blob/master/notebooks/scripts/medpy_info.py.ipynb>`_)

	Prints basic information about an image to the stdout.

.. topic:: medpy_convert.py (`notebook <https://github.com/loli/medpy/blob/master/notebooks/scripts/medpy_convert.py.ipynb>`_)

	Converts between two image formats. Alternatively can be used to create an empty image by example.

.. topic:: medpy_create_empty_volume_by_example.py (`notebook <https://github.com/loli/medpy/blob/master/notebooks/scripts/medpy_create_empty_volume_by_example.py.ipynb>`_)

	Can be used to create an empty image by example.

.. topic:: medpy_resample.py

	Re-samples an image using b-spline interpolation.

.. topic:: medpy_set_pixel_spacing.py

	Manually set the pixel/voxel spacing of an image.

.. topic:: medpy_diff.py (`notebook <https://github.com/loli/medpy/blob/master/notebooks/scripts/medpy_diff.py.ipynb>`_)

	Compares the meta-data and intensity values of two images.

.. topic:: medpy_grid.py

	Creates a binary volume containing a regular grid.

.. topic:: medpy_extract_min_max.py

	Extracts the min and max intensity values of one or more images.

.. topic:: medpy_swap_dimensions.py

	Swap two image dimensions.


.. _volume:

Image volume manipulation
=========================
:ref:`↑top <top>`

.. topic:: medpy_extract_sub_volume.py (`notebook <https://github.com/loli/medpy/blob/master/notebooks/scripts/medpy_extract_sub_volume.py.ipynb>`_)

	Extracts a sub volume from an image.

.. topic:: medpy_extract_sub_volume_auto.py

	Splits a volume into a number of sub volumes along a given dimension.

.. topic:: medpy_extract_sub_volume_by_example.py (`notebook <https://github.com/loli/medpy/blob/master/notebooks/scripts/medpy_extract_sub_volume_by_example.py.ipynb>`_)

	Takes an image and a second image containing a binary mask, then extracts the sub volume of the first image defined by the bounding box of the foreground object in the binary image.

.. topic:: medpy_fit_into_shape.py

	Fit an existing image into a new shape by either extending or cutting all dimensions symmetrically.

.. topic:: medpy_intersection.py

  Extracts the intersecting parts of two volumes regarding offset and voxel-spacing.

.. topic:: medpy_join_xd_to_xplus1d.py

	Joins a number of xD images by adding a new dimension, resulting in a (x+1)D image.

.. topic:: medpy_split_xd_to_xminus1d.py

	Splits a xD image into a number of (x-1)D images.

.. topic:: medpy_stack_sub_volumes.py

	Stacks a number of sub volumes together along a defined dimension.

.. topic:: medpy_zoom_image.py

	Enlarges an image by adding (interpolated) slices.

.. topic:: medpy_shrink_image.py

	Reduces an image by simply discarding slices.

.. topic:: medpy_reslice_3d_to_4d.py

	Reslices a 3D image formed by stacked up 3D volumes into a real 4D images (as e.g. often necessary for DICOM).

.. topic:: medpy_dicom_slices_to_volume.py

	Takes a number of 2D DICOM slice (a DICOM series) and creates a 3D volume from them.

.. topic:: medpy_dicom_to_4D.py

    Takes a number of 2D DICOM slice (a DICOM series) and creates a 4D volume from them (split-points are passed as arguments).


.. _binary:

Binary image manipulation
=========================
:ref:`↑top <top>`

.. topic:: medpy_binary_resampling.py

  Re-samples a binary image according to a supplied voxel spacing using shape based interpolation where necessary.

.. topic:: medpy_extract_contour.py (`notebook <https://github.com/loli/medpy/blob/master/notebooks/scripts/medpy_extract_contour.py.ipynb>`_)

  Converts a binary volume into a surface contour.

.. topic:: medpy_join_masks.py

  Joins a number of binary images into a single conjunction using sum, avg, max or min.

.. topic:: medpy_merge.py

	Performs a logical OR on two binary images.


.. _filter:

Image filters
=============
:ref:`↑top <top>`

.. topic:: medpy_gradient.py (`notebook <https://github.com/loli/medpy/blob/master/notebooks/scripts/medpy_gradient.py.ipynb>`_)

	Gradient magnitude image filter. Output is float.

.. topic:: medpy_morphology.py

	Apply binary morphology (dilation, erosion, opening or closing) to a binary image.

.. topic:: medpy_anisotropic_diffusion.py (`notebook <https://github.com/loli/medpy/blob/master/notebooks/scripts/medpy_anisotropic_diffusion.py.ipynb>`_)

	Apply the edge preserving anisotropic diffusion filter to an image.

.. topic:: medpy_watershed.py (`notebook <https://github.com/loli/medpy/blob/master/notebooks/scripts/medpy_watershed.py.ipynb>`_)

    Applies a watershed filter, results in a label map / region image.


.. _mr:

Magnetic resonance (MR) related
===============================
:ref:`↑top <top>`

.. topic:: medpy_apparent_diffusion_coefficient.py (`notebook <https://github.com/loli/medpy/blob/master/notebooks/scripts/medpy_apparent_diffusion_coefficient.py.ipynb>`_)

	Computes the apparent diffusion coefficient (ADC) map from two diffusion weight (DW) volumes acquired with different b-values.

.. topic:: medpy_intensity_range_standardization.py

	Standardizes the intensity ranges of a number of MR images and produces a corresponding model that can be applied to new images.


.. _gc:

Graph-cut
=========
:ref:`↑top <top>`

GC based on (and shipped with, ask!) Max-flow/min-cut by Boykov-Kolmogorov algorithm, version 3.01 [1]_.

.. topic:: medpy_graphcut_voxel.py (`notebook <https://github.com/loli/medpy/blob/master/notebooks/scripts/medpy_graphcut_voxel.py.ipynb>`_)

	Executes a voxel based graph cut. Only supports the boundary term.

.. topic:: medpy_graphcut_label.py (`notebook <https://github.com/loli/medpy/blob/master/notebooks/scripts/medpy_graphcut_label.py.ipynb>`_)

	Executes a label based graph cut. Only supports the boundary term.

.. topic:: medpy_graphcut_label_bgreduced.py

	Executes a label based graph cut. Only supports the boundary term. Reduces the input image by considering only the region defined by the bounding box around the background markers.

.. topic:: medpy_graphcut_label_wsplit.py

	Executes a label based graph cut. Only supports the boundary term. Reduces the memory requirements by splitting the image into a number of sub-volumes. Note that this will result in a non-optimal cut.

.. topic:: medpy_graphcut_label_w_regional.py

	Executes a label based graph cut. With boundary and regional term.

.. topic:: medpy_label_count.py

	Counts the number of unique intensity values in an image i.e. the amount of labelled regions.

.. topic:: medpy_label_fit_to_mask.py

	Fits the labelled regions of a label map image to a binary segmentation map.

.. topic:: medpy_label_superimposition.py

	Takes to label maps and superimpose them to create a new label image with more regions.


.. _others:

Others
======
:ref:`↑top <top>`



References
==========
.. [1] http://vision.csd.uwo.ca/code/
