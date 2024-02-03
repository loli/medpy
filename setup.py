#!/usr/bin/env python

# version: 0.2.8
# Many thanks to simplejson for the idea on how to install c++-extention module optionally!
# https://pypi.python.org/pypi/simplejson/

import os
import sys
from ctypes.util import find_library
from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError, DistutilsExecError, DistutilsPlatformError

from setuptools import Command, Extension, setup

# CONSTANTS
IS_PYPY = hasattr(sys, "pypy_translation_info")  # why this?
PACKAGES = [
    "medpy",
    "medpy.core",
    "medpy.features",
    "medpy.filter",
    "medpy.graphcut",
    "medpy.io",
    "medpy.metric",
    "medpy.utilities",
]


#### FUNCTIONS
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def try_find_library(lib_name):
    if not find_library(lib_name):
        return None
    else:
        return lib_name


### PREDEFINED MODULES
# The maxflow graphcut wrapper using boost.python

# Special handling for homebrew Boost Python library
if sys.platform == "darwin":
    if sys.version_info.major > 2:
        boost_python_library = "boost_python" + str(sys.version_info.major)
    else:
        boost_python_library = "boost_python"
else:
    boost_python_library = try_find_library(
        "boost_python-py" + str(sys.version_info.major) + str(sys.version_info.minor)
    )
    if not boost_python_library:
        boost_python_library = try_find_library(
            "boost_python-py" + str(sys.version_info.major)
        )
    if not boost_python_library:
        boost_python_library = try_find_library(
            "boost_python" + str(sys.version_info.major) + str(sys.version_info.minor)
        )
    if not boost_python_library:
        # exact version not found, trying with major fit only as fallback
        boost_python_library = "boost_python" + str(sys.version_info.major)

maxflow = Extension(
    "medpy.graphcut.maxflow",
    define_macros=[("MAJOR_VERSION", "0"), ("MINOR_VERSION", "1")],
    sources=[
        "lib/maxflow/src/maxflow.cpp",
        "lib/maxflow/src/wrapper.cpp",
        "lib/maxflow/src/graph.cpp",
    ],
    libraries=[boost_python_library],
    extra_compile_args=["-O0"],
)

### FUNCTIONALITY FOR CONDITIONAL C++ BUILD
if sys.platform == "win32" and sys.version_info > (2, 6):
    # 2.6's distutils.msvc9compiler can raise an IOError when failing to
    # find the compiler
    # It can also raise ValueError http://bugs.python.org/issue7511
    ext_errors = (
        CCompilerError,
        DistutilsExecError,
        DistutilsPlatformError,
        IOError,
        ValueError,
    )
else:
    ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError)


class BuildFailed(Exception):
    pass


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        raise SystemExit(1)


class ve_build_ext(build_ext):
    # This class allows C++ extension building to fail.
    def run(self):
        try:
            build_ext.run(self)
        except DistutilsPlatformError:
            raise BuildFailed()

    def build_extension(self, ext):
        try:
            build_ext.build_extension(self, ext)
        except ext_errors:
            raise BuildFailed()


### MAIN SETUP FUNCTION
def run_setup(with_compilation):
    cmdclass = dict(test=TestCommand)
    if with_compilation:
        kw = dict(
            ext_modules=[maxflow], cmdclass=dict(cmdclass, build_ext=ve_build_ext)
        )
        ap = ["medpy.graphcut"]
    else:
        kw = dict(cmdclass=cmdclass)
        ap = []

    setup(
        name="MedPy",
        version="0.5.0",  # major.minor.micro
        description="Medical image processing in Python",
        author="Oskar Maier",
        author_email="oskar.maier@gmail.com",
        url="https://github.com/loli/medpy",
        license="LICENSE.txt",
        keywords="medical image processing dicom itk insight tool kit MRI CT US graph cut max-flow min-cut",
        long_description=read("README_PYPI.md"),
        long_description_content_type="text/markdown",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Environment :: Other Environment",
            "Intended Audience :: End Users/Desktop",
            "Intended Audience :: Developers",
            "Intended Audience :: Healthcare Industry",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: POSIX",
            "Operating System :: Unix",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: C++",
            "Topic :: Scientific/Engineering :: Medical Science Apps.",
            "Topic :: Scientific/Engineering :: Image Recognition",
        ],
        python_requires=">=3.5, <4",
        install_requires=["scipy >= 1.10", "numpy >= 1.24", "SimpleITK >= 2.1"],
        extras_require={
            "dev": ["pre-commit"],  # for development
            "test": ["pytest", "hypothesis"],  # for testing
            "watershed": ["scikit-image"],  # for watershed segmentation script
        },
        packages=PACKAGES + ap,
        scripts=[
            "bin/medpy_anisotropic_diffusion.py",
            "bin/medpy_apparent_diffusion_coefficient.py",
            "bin/medpy_binary_resampling.py",
            "bin/medpy_convert.py",
            "bin/medpy_create_empty_volume_by_example.py",
            "bin/medpy_dicom_slices_to_volume.py",
            "bin/medpy_dicom_to_4D.py",
            "bin/medpy_diff.py",
            "bin/medpy_extract_contour.py",
            "bin/medpy_extract_min_max.py",
            "bin/medpy_extract_sub_volume_auto.py",
            "bin/medpy_extract_sub_volume_by_example.py",
            "bin/medpy_extract_sub_volume.py",
            "bin/medpy_fit_into_shape.py",
            "bin/medpy_gradient.py",
            "bin/medpy_graphcut_label_bgreduced.py",
            "bin/medpy_graphcut_label_w_regional.py",
            "bin/medpy_graphcut_label_wsplit.py",
            "bin/medpy_graphcut_label.py",
            "bin/medpy_graphcut_voxel.py",
            "bin/medpy_grid.py",
            "bin/medpy_info.py",
            "bin/medpy_intensity_range_standardization.py",
            "bin/medpy_intersection.py",
            "bin/medpy_join_masks.py",
            "bin/medpy_join_xd_to_xplus1d.py",
            "bin/medpy_label_count.py",
            "bin/medpy_label_fit_to_mask.py",
            "bin/medpy_label_superimposition.py",
            "bin/medpy_merge.py",
            "bin/medpy_morphology.py",
            "bin/medpy_resample.py",
            "bin/medpy_reslice_3d_to_4d.py",
            "bin/medpy_set_pixel_spacing.py",
            "bin/medpy_shrink_image.py",
            "bin/medpy_split_xd_to_xminus1d.py",
            "bin/medpy_stack_sub_volumes.py",
            "bin/medpy_swap_dimensions.py",
            "bin/medpy_watershed.py",
            "bin/medpy_zoom_image.py",
        ],
        **kw
    )


### INSTALLATION
try:
    run_setup(not IS_PYPY)
except BuildFailed:
    BUILD_EXT_WARNING = "WARNING: The medpy.graphcut.maxflow external C++ package could not be compiled, all graphcut functionality will be disabled. You might be missing Boost.Python or some build essentials like g++."
    print(("*" * 75))
    print(BUILD_EXT_WARNING)
    print("Failure information, if any, is above.")
    print("I'm retrying the build without the graphcut C++ module now.")
    print(("*" * 75))
    run_setup(False)
    print(("*" * 75))
    print(BUILD_EXT_WARNING)
    print("Plain-Python installation succeeded.")
    print(("*" * 75))
