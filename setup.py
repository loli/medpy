#!/usr/bin/env python

import os
# uncomment these two line if you (1) want to use the power of distribute or (2) plan to run 'python setup.py develop'
from distribute_setup import use_setuptools
use_setuptools('0.6.23')
from setuptools import setup, Extension

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# The maxflow graphcut wrapper using boost.python
maxflow = Extension('medpy.graphcut.maxflow',
                    define_macros = [('MAJOR_VERSION', '1'),
                                     ('MINOR_VERSION', '0')],
		    sources = ['lib/maxflow/src/maxflow.cpp', 'lib/maxflow/src/wrapper.cpp', 'lib/maxflow/src/graph.cpp'],
                    libraries = ['boost_python'],
                    extra_compile_args = ['-O0'])

setup(name='MedPy',
      version='0.1.0', # major.minor.micro
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
	'Nifti/Analyze':  ["nibabel >= 1.3.0", "RXP"],
	'Dicom': ["pydicom >= 0.9.7"],
	'Additional image formats' : ["itk >= 3.16.0"]
      },

      packages = [
	'medpy',
	'medpy.metric',
	'medpy.io',
	'medpy.features',
	'medpy.utilities',
	'medpy.graphcut',
	'medpy.core',
	'medpy.filter',
	'medpy.itkvtk',
	'medpy.itkvtk.filter',
	'medpy.itkvtk.utilities'
      ],
      
      scripts=[
	'bin/medpy_check_marker_intersection.py',
	'bin/medpy_diff.py',
	'bin/medpy_gradient.py',
	'bin/medpy_reslice_3d_to_4d.py',      
	'bin/medpy_swap_dimensions.py',
	'bin/medpy_convert.py',                       
	'bin/medpy_evaluate_miccai2007.py',            
	'bin/medpy_graphcut_label_bgreduced.py',   
	'bin/medpy_info.py',                   
	'bin/medpy_set_pixel_spacing.py',     
	'bin/medpy_zoom_image.py',
	'bin/medpy_count_labels.py',                    
	'bin/medpy_extract_min_max.py',                
	'bin/medpy_graphcut_label.py',             
	'bin/medpy_join_xd_to_xplus1d.py',     
	'bin/medpy_shrink_image.py',          
	'bin/medpy_create_empty_volume_by_example.py',  
	'bin/medpy_extract_sub_volume_auto.py',        
	'bin/medpy_graphcut_label_w_regional.py', 
	'bin/medpy_merge.py',                  
	'bin/medpy_split_xd_to_xminus1d.py',
	'bin/medpy_dicom_slices_to_volume.py',        
	'bin/medpy_extract_sub_volume_by_example.py',
	'bin/medpy_graphcut_label_wsplit.py',
	'bin/medpy_morphology.py',  
	'bin/medpy_stack_sub_volumes.py',
	'bin/medpy_dicom_to_4D.py',                
	'bin/medpy_extract_sub_volume.py',
	'bin/medpy_graphcut_voxel.py',         
	'bin/medpy_reduce.py',         
	'bin/medpy_superimposition.py',
	'bin/medpy_itk_gradient.py',
	'bin/medpy_itk_smoothing.py',
	'bin/medpy_itk_watershed.py'
      ],

      ext_modules = [maxflow],
     )
