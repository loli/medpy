#!/usr/bin/env python

# version: 0.2.4
# Many thanks to simplejson for the idea on how to install c++-extention module optionally!
# https://pypi.python.org/pypi/simplejson/

import os
import sys
from distutils.command.build_ext import build_ext
from distutils.errors import CCompilerError, DistutilsExecError, DistutilsPlatformError

# setuptools >= 0.7 supports 'python setup.py develop'
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, Extension, Command

# CONSTANTS
IS_PYPY = hasattr(sys, 'pypy_translation_info') # why this?
PACKAGES= [
    'medpy',
    'medpy.core',
    'medpy.features',
    'medpy.filter',
    'medpy.io',
    'medpy.itkvtk',
    'medpy.itkvtk.filter',
    'medpy.itkvtk.utilities',
    'medpy.metric',
    'medpy.utilities'
]

#### FUNCTIONS
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

### PREDEFINED MODULES
# The maxflow graphcut wrapper using boost.python
maxflow = Extension('medpy.graphcut.maxflow',
                    define_macros = [('MAJOR_VERSION', '0'),
                                     ('MINOR_VERSION', '1')],
                    sources = ['lib/maxflow/src/maxflow.cpp', 'lib/maxflow/src/wrapper.cpp', 'lib/maxflow/src/graph.cpp'],
                    libraries = ['boost_python'],
                    extra_compile_args = ['-O0'])

### FUNCTIONALITY FOR CONDITIONAL C++ BUILD
if sys.platform == 'win32' and sys.version_info > (2, 6):
    # 2.6's distutils.msvc9compiler can raise an IOError when failing to
    # find the compiler
    # It can also raise ValueError http://bugs.python.org/issue7511
    ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError, IOError, ValueError)
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
        kw = dict(ext_modules = [maxflow],
                  cmdclass=dict(cmdclass, build_ext=ve_build_ext))
        ap = ['medpy.graphcut']
    else:
        kw = dict(cmdclass=cmdclass)
        ap = []

    setup(
          name='MedPy',
          version='0.2.2', # major.minor.micro
          description='Medical image processing in Python',
          author='Oskar Maier',
          author_email='oskar.maier@googlemail.com',
          url='https://github.com/loli/medpy',
          license='LICENSE.txt',
          keywords='medical image processing dicom itk insight tool kit MRI CT US graph cut max-flow min-cut',
          long_description=read('README.txt'),
        
          classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Console',
              'Environment :: Other Environment',
              'Intended Audience :: End Users/Desktop',
              'Intended Audience :: Developers',
              'Intended Audience :: Healthcare Industry',
              'Intended Audience :: Science/Research',
              'License :: OSI Approved :: GNU General Public License (GPL)',
              #'Operating System :: MacOS :: MacOS X',
              #'Operating System :: Microsoft :: Windows',
              'Operating System :: POSIX',
              'Operating System :: Unix',
              'Programming Language :: Python',
              'Programming Language :: C++',
              'Topic :: Scientific/Engineering :: Medical Science Apps.',
              'Topic :: Scientific/Engineering :: Image Recognition'
          ],
        
          install_requires=[
           	"scipy >= 0.9.0",
            "numpy >= 1.6.1",
          ],
        
          extras_require = {
            'NIfTI/Analyze':  ["nibabel >= 1.3.0"],
            'Dicom': ["pydicom >= 0.9.7"],
            'Additional image formats' : ["itk >= 3.16.0"]
          },
        
          packages = PACKAGES + ap,
          
          scripts=[
            'bin/medpy_anisotropic_diffusion.py',
            'bin/medpy_apparent_diffusion_coefficient.py',
            'bin/medpy_check_marker_intersection.py',
            'bin/medpy_convert.py',       
            'bin/medpy_create_empty_volume_by_example.py',
            'bin/medpy_dicom_slices_to_volume.py',    
            'bin/medpy_dicom_to_4D.py',             
            'bin/medpy_diff.py',
            'bin/medpy_extract_contour.py',
            'bin/medpy_extract_min_max.py',     
            'bin/medpy_extract_sub_volume_auto.py',     
            'bin/medpy_extract_sub_volume_by_example.py',        
            'bin/medpy_extract_sub_volume.py',
            'bin/medpy_gradient.py',
            'bin/medpy_graphcut_label_bgreduced.py',   
            'bin/medpy_graphcut_label_w_regional.py', 
            'bin/medpy_graphcut_label_wsplit.py',
            'bin/medpy_graphcut_label.py',
            'bin/medpy_graphcut_voxel.py',   
            'bin/medpy_grid.py',   
            'bin/medpy_info.py',  
            'bin/medpy_intensity_range_standardization.py', 
            'bin/medpy_intersection.py', 
            'bin/medpy_itk_gradient.py',
            'bin/medpy_itk_smoothing.py',
            'bin/medpy_itk_watershed.py',
            'bin/medpy_join_masks.py',
            'bin/medpy_join_xd_to_xplus1d.py',
            'bin/medpy_label_count.py',
            'bin/medpy_label_fit_to_mask.py',
            'bin/medpy_label_superimposition.py',
            'bin/medpy_merge.py',    
            'bin/medpy_morphology.py',  
            'bin/medpy_resample.py',
            'bin/medpy_reslice_3d_to_4d.py',     
            'bin/medpy_set_pixel_spacing.py',     
            'bin/medpy_shrink_image.py',  
            'bin/medpy_split_xd_to_xminus1d.py', 
            'bin/medpy_stack_sub_volumes.py',
            'bin/medpy_swap_dimensions.py',
            'bin/medpy_watershed.py',
            'bin/medpy_zoom_image.py'
          ],
          
          **kw
     )

### INSTALLATION
try:
    run_setup(not IS_PYPY)
except BuildFailed:
    BUILD_EXT_WARNING = ("WARNING: The medpy.graphcut.maxflow external C++ package could not be compiled, all graphcut functionality will be disabled. You might be missing Boost.Python or some build essentials like g++.")
    print('*' * 75)
    print(BUILD_EXT_WARNING)
    print("Failure information, if any, is above.")
    print("I'm retrying the build without the graphcut C++ module now.")
    print('*' * 75)
    run_setup(False)
    print('*' * 75)
    print(BUILD_EXT_WARNING)
    print("Plain-Python installation succeeded.")
    print('*' * 75)
