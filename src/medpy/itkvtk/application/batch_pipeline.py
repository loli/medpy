#!/usr/bin/python

"""Executes an image processing pipeline leading to the evaluation of the watershed alg."""

# build-in modules
import argparse

# third-party modules
import numpy
from nibabel.loadsave import load, save
import vtk
import itk

# path changes

# own modules
import medpy.itkvtk.utilities.itku as itku
import medpy.itkvtk.utilities.vtku as vtku
from medpy.filter import labels_reduce
from medpy.metric import Volume, Surface

# information
__author__ = "Oskar Maier"
__version__ = "0.1, 2011-12-09"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  Executes an image processing pipeline leading to the evaluation of
                  the watershed algorithm. The pipeline can be executed over many images
                  at once and includes smoothing, building of a height map, the
                  watershed, reducing to fit to a mask and evaluation.
                  The parameters ranges for smoothing and watershed that should be
                  processed are defined in this file.
                  The intermediate result images are saved in their respective folders
                  as defined in this file. Their suffixes denote the parameters, which
                  with they've been created.
                  """

# config vars
_FOLDER_SOURCE = '00originals/'
_FOLDER_SMOOTHING = '01smoothed/'
_FOLDER_HEIGHT = '02height/'
_FOLDER_WATERSHED = '03watershed/'
_FOLDER_REDUCED = '04regionmask/'
_FOLDER_EVALUATION = '05evaluation/'

_SMOOTHING_ITERATIONS = [1] #(2,5,10,15,20)
_SMOOTHING_CONDUCTANCE = [0.5] #(0.5, 1.0, 1.5)
_SMOOTHING_TIMESTEP = [0.0624]

_WATERSHED_THRESHOLD = [0.001] #(0.001, 0.005, 0.01, 0.05, 0.1)
_WATERSHED_LEVEL = [0.2] #(0.2, 0.15, 0.1, 0.05, 0.01) # decreasing

# member vars
_smoothed_images = []
_height_images = []
_watershed_images = []
_reduced_images = []

# code
def main():
    # parse cmd arguments
    parser = getParser()
    parser.parse_args()
    args = getArguments(parser)
    
    # iterate over the input images and process
    for input in args.pairs:
        print '################################'
        print 'Processing image/mask pair {}/{}'.format(input[0].split('/')[-1], input[1].split('/')[-1])
        print '################################'
    
        # load image using vtk
        print 'Loading image with VTK...'
        reader = vtk.vtkMetaImageReader()
        reader.SetFileName(input[0])
        reader.Update()
        print 'done.'
    
        if args.debug: print vtku.getInformation(reader.GetOutput())
    
        # cast image to float
        print 'Cast to float...'
        image_float = vtk.vtkImageCast()
        image_float.SetInput(reader.GetOutput())
        image_float.SetOutputScalarTypeToFloat()
        image_float.Update()
        print 'done.'
        
        if args.debug: print vtku.getInformation(image_float.GetOutput())
        
        # convert image to ITK image
        print 'To ITK...'
        image_type = itku.getImageTypeFromVtk(image_float.GetOutput())
        image_vtk_itk = itk.VTKImageToImageFilter[image_type].New()
        image_vtk_itk.SetInput(image_float.GetOutput())
        image_vtk_itk.Update()
        print 'done.'
        
        if args.debug: print itku.getInformation(image_vtk_itk.GetOutput())
        
        
        print 'Execute batch smoothing:'
        for iteration in _SMOOTHING_ITERATIONS:
            for conductance in _SMOOTHING_CONDUCTANCE:
                for timestep in _SMOOTHING_TIMESTEP:
                    print '\tSmoothing with iter={} / cond={} / tstep={}...'.format(iteration, conductance, timestep)
                    image_smoothed = itk.GradientAnisotropicDiffusionImageFilter[image_type, image_type].New()
                    image_smoothed.SetNumberOfIterations(iteration)
                    image_smoothed.SetConductanceParameter(conductance)
                    image_smoothed.SetTimeStep(timestep)
                    image_smoothed.SetInput(image_vtk_itk.GetOutput())
                    image_smoothed.Update()
                    print '\tsmoothed.'
                    
                    if args.debug: print itku.getInformation(image_smoothed.GetOutput())
                    
                    image_smoothed_name = _FOLDER_SMOOTHING + input[0].split('/')[-1][:-4] + '_smoothed'
                    image_smoothed_name += '_i{}_c{}_t{}'.format(iteration, conductance, timestep)
                    print '\tSaving as {}...'.format(image_smoothed_name)
                    itku.saveImageMetaIO(image_smoothed.GetOutput(), image_smoothed_name)
                    print '\tsaved.'
                    
                    _smoothed_images.append(image_smoothed_name + '.mhd')
        print 'Batch smoothing successfully finished.'
        
        
        print 'Execute height mapping:'
        for smoothed_image in _smoothed_images:
            print '\tLoading {}...'.format(smoothed_image)
            reader = vtk.vtkMetaImageReader()
            reader.SetFileName(smoothed_image)
            reader.Update()
            
            print '\tTo ITK...'
            image_type = itku.getImageTypeFromVtk(reader.GetOutput())
            image_vtk_itk = itk.VTKImageToImageFilter[image_type].New()
            image_vtk_itk.SetInput(reader.GetOutput())
            image_vtk_itk.Update()    
                    
            print '\tApplying height mapping...'
            image_height_function = itk.GradientMagnitudeImageFilter[image_type, image_type].New()
            image_height_function.SetInput(image_vtk_itk.GetOutput())
            image_height_function.Update()
            
            image_height_name = _FOLDER_HEIGHT + smoothed_image.split('/')[-1][:-4] + '_height'
            print '\tSaving as {}...'.format(image_height_name)
            itku.saveImageMetaIO(image_height_function.GetOutput(), image_height_name)
            
            _height_images.append(image_height_name + '.mhd')
            print '\tDone.'
        print 'Height mapping successfully finished.'
        
        
        print 'Execute batch watershed:'
        for height_image in _height_images:
            print '\tLoading {}...'.format(height_image)
            reader = vtk.vtkMetaImageReader()
            reader.SetFileName(height_image)
            reader.Update()
            
            print '\tTo ITK...'
            image_type = itku.getImageTypeFromVtk(reader.GetOutput())
            image_vtk_itk = itk.VTKImageToImageFilter[image_type].New()
            image_vtk_itk.SetInput(reader.GetOutput())
            image_vtk_itk.Update()    
            
            for threshold in _WATERSHED_THRESHOLD:
                image_watershed = itk.WatershedImageFilter[image_type].New()
                image_watershed.SetInput(image_vtk_itk.GetOutput())
                image_watershed.SetThreshold(threshold)
                for level in reversed(sorted(_WATERSHED_LEVEL)): # make sure to start with highest first
                    print '\t\tWatershed with thr={} / lvl={}...'.format(threshold, level)
                    image_watershed.SetLevel(level)
                    image_watershed.Update()
                    print '\t\twatersheded.'
    
                    if args.debug: print itku.getInformation(image_watershed.GetOutput())
                    
                    print '\t\tTo VTK...'
                    itk_image_type = itku.getImageType(image_watershed.GetOutput())
                    image_vtk_itk = itk.ImageToVTKImageFilter[itk_image_type].New()
                    image_vtk_itk.SetInput(image_watershed.GetOutput())
                    image_vtk_itk.Update()
                    print '\t\tdone.'
    
                    if args.debug: print vtku.getInformation(image_vtk_itk.GetOutput())
    
                    print '\t\tTo unsigned int...'
                    image_cast = vtk.vtkImageCast()
                    image_cast.SetInput(0, image_vtk_itk.GetOutput())
                    image_cast.SetOutputScalarTypeToUnsignedInt()
                    image_cast.Update()
                    print '\tdone.'
    
                    if args.debug: print vtku.getInformation(image_cast.GetOutput())                   
                    
                    image_watershed_name = _FOLDER_WATERSHED + height_image.split('/')[-1][:-4] + '_watershed'
                    print '\t\tSaving as {}...'.format(image_watershed_name)
                    vtku.saveImageMetaIO(image_cast.GetOutput(), image_watershed_name)
                
                    _watershed_images.append(image_watershed_name + '.mhd')
                    print '\tdone.'
        print 'Batch watershed successfully finished.'
        
        
        print 'Execute label reducing:'
        for watershed_image in _watershed_images:
            print '\tLoading label image {}...'.format(watershed_image)
            image_labels = load(watershed_image)
            print '\tLoading mask {}...'.format(input[1])
            image_mask = load(input[1])
            
            # copy image mask header for result image and image type
            header = image_mask.get_header().copy()
            image_mask_class = image_mask.__class__
            
            # convert images to numpy
            print '\t\tGet image data...'
            image_labels = image_labels.get_data()
            image_mask = image_mask.get_data()
            print '\t\t...done.'
            # saving result in file
            # reduce image dimensions to 3 (nibabel always loads with 4)
            print '\t\tReduce image dimensions...'
            image_labels = numpy.squeeze(image_labels)
            image_mask = numpy.squeeze(image_mask)
            print '\t\t...done.'
            
            # cast image_mask is of type bool
            print '\t\tCast mask to bool...'
            image_mask = (0 != image_mask)
            print '\t\t...done.'
            
            # create a mask from the label image
            print '\t\tCreate mask from label image...'
            image_labels = labels_reduce(image_labels, image_mask)
            print '\t\t...done.'
            
            # saving created mask
            image_labels_name = _FOLDER_REDUCED + watershed_image.split('/')[-1][:-4] + '_mask.mhd'
            print '\t\tSaving as {}...'.format(image_labels_name)
            header.set_data_dtype(numpy.uint8)
            image = image_mask_class(image_labels, header.get_base_affine(), header=header)
            image.update_header()
            save(image, image_labels_name)
            
            _reduced_images.append(image_labels_name)
            print '\t\tdone.'
        print 'Label reducing successfully finished.'
        
        
        print 'Evaluate masks:'
        for reduced_image in _reduced_images:
            print '\tLoading created mask {}...'.format(reduced_image)
            image_labels = load(reduced_image)
            print '\tLoading original mask {}...'.format(input[1])
            image_mask = load(input[1])
            
            # get physical spacing (assumed to be the same for both)
            spacing = image_labels.get_header().get_zooms()[0:3]
            
            # convert images to numpy
            print '\tGet image data...'
            image_labels = image_labels.get_data()
            image_mask = image_mask.get_data()
            
            # evaluating and saving result in file
            evaluation_file_name = _FOLDER_EVALUATION + reduced_image.split('/')[-1][:-4] + '.eval'
            print '\t\tTarget file: {}.'.format(evaluation_file_name)
            f = open('evaluation_file_name', 'w')
            print '\t\tVolume metrics:'
            vo = Volume(image_labels, image_mask)
            s = 'VolumetricOverlapError\t{}\n'.format(vo.GetVolumetricOverlapError())
            s += 'VolumetricOverlapError\t{}\n'.format(vo.GetRelativeVolumeDifference())
            f.write(s)
            print s            
            
            print '\t\tSurface metrics:'
            su = Surface(image_labels, image_mask, spacing)
            s = 'AverageSymmetricSurfaceDistance\t{}\n'.format(su.GetAverageSymmetricSurfaceDistance())
            s += 'MaximumSymmetricSurfaceDistance\t{}\n'.format(su.GetMaximumSymmetricSurfaceDistance())
            s += 'RootMeanSquareSymmetricSurfaceDistance\t{}\n'.format(su.GetRootMeanSquareSymmetricSurfaceDistance())
            f.write(s)
            print s
            
            f.close()
            
        print 'Evaluation successfully finished.'
        
    print 'EXIT.'
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    if 0 != len(args.images) % 2:
        raise ValueError('Please support image/mask pairs. An uneven number of input files was supplied.')
    args.pairs = [(args.images[i], args.images[i+1]) for i in range(0, len(args.images), 2)]
    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    
    parser.add_argument('images', nargs='+', help='Image/Mask pairs of Meta IO images (.mhd/.mha).')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    return parser    
    
if __name__ == "__main__":
    main()    