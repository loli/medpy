#!/usr/bin/env python

#from distutils.core import setup, Extension
from setuptools import setup, Extension

setup(name='MedPy',
      version='0.1.0', # major.minor.micro
      description='Medical image processing in Python',
      long_description=open('README.txt').read(),
      author='Oskar Maier',
      author_email='oskar.maier@googlemail.com',
      url='https://github.com/loli/medpy',
      license='LICENSE.txt',
      keywords='medical image processing dicom itk insight tool kit MRI CT US graph cut max-flow min-cut',

      install_requires=[
       	"scipy >= 0.9.0",
        "numpy >= 1.6.1",
      ],

      extras_require = {
	'Nifti/Analyze':  ["nibabel >= 1.3.0", "RXP"],
	'Dicom': ["pydicom >= 0.9.7"],
	'Additional formats' : ["itk > 1.0.0"] # !TODO: Is it at all possible to give a version here? Which one do I have?
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
	'medpy.itkvtk'
      ],
      
      scripts=[
	'bin/medpy_check_marker_intersection.py',
	'bin/medpy_diff.py',
	'bin/medpy_gradient.py',
	'bin/medpy_graphcut_voxel_single.py',
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
	'bin/medpy_superimposition.py'
      ],

      ext_modules=[Extension('medpy.graphcut.maxflow',
			     sources = ['lib/maxflow/src/maxflow.cpp', 'lib/maxflow/src/wrapper.cpp', 'lib/maxflow/src/graph.cpp'],
			     libraries = ['boost_python', 'python2.7'])] # eventually still requires to include -I/usr/include/python2.7 (include_dirs = ['/usr/include/python2.7'],)
     )
