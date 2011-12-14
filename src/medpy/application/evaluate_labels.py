#!/usr/bin/python

"""Evaluates a label image on how good it fits to a mask."""

# build-in modules
import argparse

# third-party modules
import numpy
from nibabel.loadsave import load, save
from nibabel.analyze import AnalyzeImage, AnalyzeHeader

# path changes

# own modules
from medpy.filter import labels_reduce
from medpy.metric import Volume, Surface
import time

# information
__author__ = "Oskar Maier"
__version__ = "0.1, 2011-12-07"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  Takes a label image, fits it best possible to the supplied mask
                  and then evaluates the result against the mask.
                  The supplied label image and mask image are assumed to be of same
                  orientation, offset and physical spacing.
                  """

# code
def main():
    # !TODO: Volume apparently needs some more unittests to figure everything out
    # !TODO: Check what file types can be loaded and write that in the description.
    # !TODO: Write a function to interpolate images with different pyhsical spacing
    # !TODO: Extract and pass on physical spacing and image offsets
    # !TODO: Print infos about the images when verbose flag is set
    # !TODO: Add silent flag
    # !TODO: Make sure that this can be used as included script
    # parse cmd arguments
    parser = getParser()
    parser.parse_args()
    args = getArguments(parser)
    
    # load images
    print 'Load images...'
    image_labels = load(args.label_image)
    image_mask = load(args.mask_image)
    print '...done.'
    
    # copy image mask header for result image and image type
    header = image_mask.get_header().copy()
    image_mask_class = image_mask.__class__
    
    # convert images to numpy
    print 'Get image data...'
    image_labels = image_labels.get_data()
    image_mask = image_mask.get_data()
    print '...done.'
    
    # reduce image dimensions to 3 (nibabel always loads with 4)
    print 'Reduce image dimensions...'
    image_labels = numpy.squeeze(image_labels)
    image_mask = numpy.squeeze(image_mask)
    print '...done.'
    
    # cast image_mask is of type bool
    print 'Cast mask to bool...'
    image_mask = (0 != image_mask)
    print '...done.'
    
    # create a mask from the label image
    print 'Create mask from label image...'
    tp = time.time()
    image_labels = labels_reduce(image_labels, image_mask)
    ts = time.time()
    print '\tExecution took: %0.3f ms' % ((ts-tp)*1000.0)
    print '...done.'
    
    if args.save_intermediate:
        # !TODO: No real header is created for this image, fix
        image_labels_name = args.label_image[:-4] + '_mask' + args.label_image[-4:]
        print 'Saving created mask image as', image_labels_name, '...'
        #hdr = AnalyzeHeader()
        header.set_data_dtype(numpy.uint8) # eventually keep old datatype?
        #hdr.set_data_dtype(numpy.uint8)
        image = image_mask_class(image_labels, header.get_base_affine(), header=header)
        image.update_header()
        #img = AnalyzeImage(image_labels, numpy.eye(4), header=hdr)
        save(image, image_labels_name)
        print 'done'
    
    # evaluate the resulting mask
    print 'Evaluate...'
    
    print 'Volume metrics:'
    v = Volume(image_labels, image_mask)
    print 'VolumetricOverlapError:', v.GetVolumetricOverlapError()
    print 'RelativeVolumeDifference:', v.GetRelativeVolumeDifference()
    
    print 'Surface metrics:'
    s = Surface(image_labels, image_mask, header.get_zooms()[0:3])
    print 'AverageSymmetricSurfaceDistance:', s.GetAverageSymmetricSurfaceDistance()
    print 'MaximumSymmetricSurfaceDistance', s.GetMaximumSymmetricSurfaceDistance()
    print 'RootMeanSquareSymmetricSurfaceDistance:', s.GetRootMeanSquareSymmetricSurfaceDistance()
    
    print '...done.'
    
    print 'EXIT'
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    
    parser.add_argument('label_image', help='A label image where different values designate different regions.')
    parser.add_argument('mask_image', help='A mask image with 0 or False values as background.')
    parser.add_argument('-s', dest='save_intermediate', action='store_true', help='Set this flag to save the mask created from the label image.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    
    return parser    
    
if __name__ == "__main__":
    main()