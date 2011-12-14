#!/usr/bin/python

"""Executes the watershed region segmentation over an image."""

# build-in modules
import argparse

# third-party modules
import vtk
import itk

# path changes

# own modules
import medpy.itkvtk.utilities.itku as itku
import medpy.itkvtk.utilities.vtku as vtku

# information
__author__ = "Oskar Maier"
__version__ = "r0.1, 2011-12-07"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Watershed image segmentation based on ITK/VTK.
                  Uses gradient anisotropic diffusion to preprocess the image.
                  The resulting image is saved under the same name and place as
                  the input image with an suffix (_watershed) attached.
                  """

# code
def main():
    # !TODO: Add silent flag
    # !TODO: Make sure that this can be used as included script
    # parse cmd arguments
    parser = getParser()
    parser.parse_args()
    args = getArguments(parser)
    
    # load image using vtk
    print 'Loading image with VTK...'
    reader = vtk.vtkMetaImageReader()
    reader.SetFileName(args.image)
    reader.Update()
    print '...done.'
    
    if args.debug: print vtku.getInformation(reader.GetOutput())

    # cast image to float
    print 'Cast to float...'
    image_float = vtk.vtkImageCast()
    image_float.SetInput(reader.GetOutput())
    image_float.SetOutputScalarTypeToFloat()
    image_float.Update()
    print 'done'
    
    if args.debug: print vtku.getInformation(image_float.GetOutput())
    
    # convert image to ITK image
    print 'To ITK...'
    image_type = itku.getImageTypeFromVtk(image_float.GetOutput())
    image_vtk_itk = itk.VTKImageToImageFilter[image_type].New()
    image_vtk_itk.SetInput(image_float.GetOutput())
    image_vtk_itk.Update()
    print 'done'
    
    if args.debug: print itku.getInformation(image_vtk_itk.GetOutput())
    
    # pre-process/smooth with anisotropic diffusion image filters (which preserves edges)
    # for watershed one could use 10 iterations with conductance = 1.0
    print 'Smoothing...'
    image_smoothed = itk.GradientAnisotropicDiffusionImageFilter[image_type, image_type].New()
    image_smoothed.SetNumberOfIterations(10)
    image_smoothed.SetConductanceParameter(1.0)
    # The maximum allowable time step for this filter is 1/2^N, where N is the dimensionality of the image. For 2D images any value below 0.250 is stable, and for 3D images, any value below 0.125 is stable.
    # Note: Alg. claims that for the supplied input image the time step must be <0.0625
    image_smoothed.SetTimeStep(0.0624)
    image_smoothed.SetInput(image_vtk_itk.GetOutput())
    image_smoothed.Update()
    print 'done'
    
    if args.debug: print itku.getInformation(image_smoothed.GetOutput())
    
    if args.save_intermediate:
        image_smoothed_name = args.image[:-4] + '_smoothed'
        print 'Saving smoothed image as', image_smoothed_name, '...'
        itku.saveImageMetaIO(image_smoothed.GetOutput(), image_smoothed_name)
        print 'done'
    
    # compute a height function as watershed alg input
    # e.g. The following edge image was produced with an itk gradient magnitude image filter.
    print 'Height function...'
    image_height_function = itk.GradientMagnitudeImageFilter[image_type, image_type].New()
    image_height_function.SetInput(image_smoothed.GetOutput())
    image_height_function.Update()
    print 'done'
    
    if args.debug: print itku.getInformation(image_height_function.GetOutput())
    
    if args.save_intermediate:
        image_height_function_name = args.image[:-4] + '_height'
        print 'Saving height function image as', image_height_function_name, '...'
        itku.saveImageMetaIO(image_height_function.GetOutput(), image_height_function_name)
        print 'done'
    
    # run the watershed alg which produces an output image with unsigned long values
    # -> output dim = input dim, output-type = integer type
    # -> each pixel with the same value belongs to the same region
    # ! low level value = oversegmentation & less computation time
    # ! high level = more region merging = undersegmentation
    # ! low threshold = more initial minimums = more regions
    # Note: resetting the level to a lower value after it once has been processed doesn't require complete reprocessing and new results are produced in constant time
    print 'Watershed...'
    image_watershed = itk.WatershedImageFilter[image_type].New()
    image_watershed.SetThreshold(0.02)
    image_watershed.SetLevel(0.1)
    image_watershed.SetInput(image_height_function.GetOutput())
    image_watershed.Update()
    print 'done'
    
    if args.debug: print itku.getInformation(image_watershed.GetOutput())
    
    print 'To VTK...'
    itk_image_type = itku.getImageType(image_watershed.GetOutput())
    image_vtk_itk = itk.ImageToVTKImageFilter[itk_image_type].New()
    image_vtk_itk.SetInput(image_watershed.GetOutput())
    image_vtk_itk.Update()
    print 'done'
    
    if args.debug: print vtku.getInformation(image_vtk_itk.GetOutput())
    
    print 'To unsigned int...'
    image_cast = vtk.vtkImageCast()
    image_cast.SetInput(0, image_vtk_itk.GetOutput())
    image_cast.SetOutputScalarTypeToUnsignedInt()
    image_cast.Update()
    print 'done'
    
    if args.debug: print vtku.getInformation(image_cast.GetOutput())
        
    # save final image
    print 'Saving result...'
    image_watershed_name = args.image[:-4] + '_watershed'
    vtku.saveImageMetaIO(image_cast.GetOutput(), image_watershed_name)
    print 'done.'
    
    print 'EXIT'
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    
    parser.add_argument('image', help='An MetaI/O image file header (.mhd/.mha).')
    parser.add_argument('-s', dest='save_intermediate', action='store_true', help='Set this flag to save the images created in all intermediate processing steps.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    group_filter = parser.add_argument_group('Gradient anisotropic diffusion image filter')
    group_filter.add_argument('--smoothing-iterations', default=10, type=int, help='The number of iterations.')
    group_filter.add_argument('--smoothing-conductance', default=1.0, type=float, help='The conductance: The higher the more the image is smoothed in each iteration step.')
    group_filter.add_argument('--smoothing-time-step', default=0.0624, type=float, help='The time-step: Depends on the image dimension, a good value is time-step < 1/2^D.')
    
    group_watershed = parser.add_argument_group('Watershed')
    group_watershed.add_argument('--watershed-threshold', default=0.02, type=float, help='The watershed threshold: The higher the less regions will be created. Should always be less than the level value.')
    group_watershed.add_argument('--watershed-level', default=0.1, type=float, help='The watershed level: The higher this value, the more regions are merged together. A good value is 0.1.')
    
    return parser    
    
if __name__ == "__main__":
    main()
