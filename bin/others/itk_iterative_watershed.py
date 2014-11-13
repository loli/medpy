#!/usr/bin/python

"""Executes an iterative watershed algorithm over images."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import scipy
import itk

# path changes

# own modules
from medpy.core import Logger
import medpy.itkvtk.utilities.itku as itku
from medpy.filter import LabelImageStatistics


# information
__author__ = "Oskar Maier"
__version__ = "d0.2, 2011-12-30"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  Applies the iterative watershed segmentation to a number of images
                  with a range of parameters. When a certain maximum region size is
                  reached, the algoithm terminates.
                  The resulting image is saved in the supplied folder with the same
                  name as the input image, but with a suffix '_watershed_[parameters]'
                  attached.
                  """

__INITIAL_THRESHOLD = 0.2
__IDEAL_REGION_SIZE = 1000. #67.584

# code
def main():
    # parse cmd arguments
    parser = getParser()
    parser.parse_args()
    args = getArguments(parser)
    
    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # iterate over input images
    for image in args.images:
        
        # load image as float using ITK
        logger.info('Loading image {} as float using ITK...'.format(image))
        image_type = itk.Image[itk.F, 3]  # causes PyDev to complain -> ignore error warning
        reader = itk.ImageFileReader[image_type].New()
        reader.SetFileName(image)
        reader.Update()
            
        
        logger.debug(itku.getInformation(reader.GetOutput()))
        
        # build output image name
        image_watershed_name = args.folder + '/' + image.split('/')[-1][:-4] + '_watershed' + image.split('/')[-1][-4:]
        
        # check if output image exists
        if not args.force:
            if os.path.exists(image_watershed_name):
                logger.warning('The output image {} already exists. Skipping this input image.'.format(image_watershed_name))
                continue
                
        # prepare watershed
        # assign to watershed_source the image to be passed to the watershed
        watershed_source = reader.GetOutput()
        # extract data from original image to scipy
        itk_py_converter_orig = itk.PyBuffer[image_type]  # causes PyDev to complain -> ignore error warning
        original_image_array = itk_py_converter_orig.GetArrayFromImage(reader.GetOutput())        
        # recover input image dimensions
        rs = original_image_array.shape
        # create empty final label image array
        image_label_final_array = scipy.zeros(rs[0] * rs[1] * rs[2], dtype=scipy.int32).reshape(rs) #!TODO: Is 32bit enough?
        # create an empty watershed result array
        watershed_result_array = scipy.zeros_like(image_label_final_array)
        # create initial label mask covering the whole image space
        label_mask = scipy.zeros(rs[0] * rs[1] * rs[2], dtype=scipy.bool_).reshape(rs)
        label_mask.fill(True)
        # set threhold to use
        threshold = __INITIAL_THRESHOLD
        # set the point to the largest region to process
        region_pointer = -1

        
        # apply the watershed
        logger.info('Applying watershed...')
        
        while True:
            # initialize the watershed filter object
            logger.info('Watershedding with settings: thr={} / level={}...'.format(threshold, 0.0))
            image_watershed = itk.WatershedImageFilter[image_type].New()
            image_watershed.SetInput(watershed_source)
            image_watershed.SetThreshold(threshold)
            image_watershed.SetLevel(0.0)
            
            try:
                image_watershed.Update()
                
                logger.debug(itku.getInformation(image_watershed.GetOutput()))
            
                logger.info('Adding resulting labels to final result image...')
                # converting to scipy
                itk_py_converter_ws = itk.PyBuffer[itku.getImageType(image_watershed.GetOutput())]  # causes PyDev to complain -> ignore error warning
                watershed_result_array = itk_py_converter_ws.GetArrayFromImage(image_watershed.GetOutput())
                # recovering current offset for the new label ids
                min_label_id = image_label_final_array.max()
                # updating final label image
                image_label_final_array[label_mask] = watershed_result_array[label_mask] + min_label_id
                
                logger.info('Last watershed led to {} new labels, {} in total now...'.format(len(scipy.unique(watershed_result_array)) - 1, len(scipy.unique(image_label_final_array))))
                
    #            # lower the threshold if no new labels were created, or skip label if a threshold of 0 did not help
                if 100 >= len(scipy.unique(watershed_result_array)) - 1:
                    if 0 == threshold:
                        region_pointer -= 1
                        logger.info('Skipping this region as threshold lowering did not lead to the production of more than 100 labels...')
                    else:
                        threshold /= 2.
                        if threshold < 0.001: threshold = 0.0
                        logger.info('Lowering threshold for next region to {} ...'.format(threshold))
                else:
                    threshold = __INITIAL_THRESHOLD
                    logger.info('Resetting threshold to original value of {} ...'.format(__INITIAL_THRESHOLD))
                    
            except RuntimeError as error:
                if 0 == threshold:
                    region_pointer -= 1
                    logger.warning('Watershed processing terminated with error {}. Skipping this region as threshold lowering did not succeed.'.format(error))
                else:
                    threshold /= 2
                    if threshold < 0.001: threshold = 0.0
                    logger.warning('Watershed processing terminated with error {}. Lowering threshold to {}.'.format(error, threshold))
            
                        
            logger.info('Computing statistics / checking stop condition...')
            statistics = LabelImageStatistics(image_label_final_array, original_image_array)
            
            # check medium region size and if stop condition reached, break
            sizes = sorted(iter(statistics.get_sizes().items()), key=lambda x: x[1]) # get sizes sorted (biggest region last)
            if __IDEAL_REGION_SIZE >= sizes[region_pointer][1]:
                logger.info('Stopping condition {} with a maximum region size of {} reached: Stopping processing...'.format(__IDEAL_REGION_SIZE, sizes[region_pointer][1]))
                break
#            if __IDEAL_REGION_SIZE >= sum(map(lambda x: x[1], sizes)) / float(len(sizes)):
#                logger.info('Stopping condition {} with a medium region size of {} reached: Stopping processing...'.format(__IDEAL_REGION_SIZE, sum(map(lambda x: x[1], sizes)) / float(len(sizes))))
#                break
                
            logger.info('Stopping condition {} with a maximum region size of {} not reached: Preparing next run...'.format(__IDEAL_REGION_SIZE, sizes[region_pointer][1]))
#            logger.info('Stopping condition {} with a medium region size of {} not reached: Preparing next run...'.format(__IDEAL_REGION_SIZE, sum(map(lambda x: x[1], sizes)) / float(len(sizes))))
            
            logger.info('Biggest region scheduled for breaking up: {} with {} voxels and intensity distribution score of {}...'.format(sizes[region_pointer][0], sizes[region_pointer][1], statistics.get_intensity_distributions()[sizes[region_pointer][0]]))
            # update label mask to cover the biggest label
            label_mask = (sizes[region_pointer][0] == image_label_final_array)
                
            # create the new input for the watershed algorithm
            watershed_source_array = scipy.zeros_like(original_image_array)
            watershed_source_array[label_mask] = original_image_array[label_mask]
            #watershed_source_array[scipy.invert(label_mask)] = watershed_source_array[label_mask].max() + 1 #!TODO: Not sure if this works, as I have the gradient image! High value = high gradient!?
            
            # cast to ITK image to apply watershed in the next step            
            watershed_source = itk_py_converter_orig.GetImageFromArray(watershed_source_array.tolist())

            logger.debug(itku.getInformation(watershed_source))
            
        # cast to ITK image to save (uses the watershed converter)
        image_label_final = itk_py_converter_ws.GetImageFromArray(image_label_final_array.tolist())

        logger.debug(itku.getInformation(image_label_final))

        logger.info('Overall skipped regions: {}...'.format(-1 * region_pointer - 1))

        # save file
        logger.info('Saving watershed image as {}...'.format(image_watershed_name))
        watershed_image_type = itku.getImageType(image_watershed.GetOutput())
        writer = itk.ImageFileWriter[watershed_image_type].New()
        writer.SetFileName(image_watershed_name)
        writer.SetInput(image_label_final)
        writer.Update()
    
    logger.info('Successfully terminated.')
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    #args.thresholds = map(float, args.thresholds.split(','))
    #args.levels = map(float, args.levels.split(','))
    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('folder', help='The place to store the created images in.')
    #parser.add_argument('levels', help='A colon separated list of values to be passed to the levels attribute (e.g. 0.1,0.2).')
    #parser.add_argument('thresholds', help='A colon separated list of values to be passed to the threshold attribute (e.g. 0.01,0.05).')
    parser.add_argument('images', nargs='+', help='One or more input images.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()        
