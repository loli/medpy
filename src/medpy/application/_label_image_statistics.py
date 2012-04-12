#!/usr/bin/python

"""Takes a label/region image and an original image to compute some statistics."""

# build-in modules
import argparse
import logging
import os

# third-party modules
import numpy
from nibabel.loadsave import load, save

# path changes

# own modules
from medpy.core import Logger
from medpy.filter import LabelImageStatistics
from medpy.utilities import image_like


# information
__author__ = "Oskar Maier"
__version__ = "d0.3, 2011-12-13"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  Takes a label/region image and an original image to compute some statistics,
                  which are saved in seperate files.
                  """
                  
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
    
    # build output files name
    label_image_name = args.label_image.split('/')[-1]
    file_general_name = '{}/{}_general.sta'.format(args.folder, label_image_name)
    file_sphericity_name = '{}/{}_sphericity.sta'.format(args.folder, label_image_name)
    file_intensitydist_name = '{}/{}_intensitydist.sta'.format(args.folder, label_image_name)
    file_regionsize_name = '{}/{}_regionsize.sta'.format(args.folder, label_image_name)
    file_size_image_name = '{}/{}_size.nii'.format(args.folder, label_image_name)
    file_intensity_image_name = '{}/{}_intensity.nii'.format(args.folder, label_image_name)
    
    # check if output files exists
    if not args.force:
        if os.path.exists(file_general_name):
            logger.warning('The output file {} already exists. Skipping.'.format(file_general_name))
        elif os.path.exists(file_sphericity_name):
            logger.warning('The output file {} already exists. Skipping.'.format(file_sphericity_name))
        elif os.path.exists(file_intensitydist_name):
            logger.warning('The output file {} already exists. Skipping.'.format(file_intensitydist_name))
        elif os.path.exists(file_regionsize_name):
            logger.warning('The output file {} already exists. Skipping.'.format(file_regionsize_name))
        elif os.path.exists(file_size_image_name):
            logger.warning('The output file {} already exists. Skipping.'.format(file_size_image_name))
        elif os.path.exists(file_intensity_image_name):
            logger.warning('The output file {} already exists. Skipping.'.format(file_intensity_image_name))
            
    # open input images
    logger.info('Loading the label image {}...'.format(args.label_image))
    label_image = load(args.label_image)
    label_image_data = numpy.squeeze(label_image.get_data())
    logger.info('Loading the original image {}...'.format(args.original_image))
    original_image_data = numpy.squeeze(load(args.original_image).get_data())
    
    # compute the statistics
    logger.info('Computing the statistics...')
    statistics = LabelImageStatistics(label_image_data, original_image_data)
    
    # extract 10 biggest regions
    sizes_10 = sorted(statistics.get_sizes().iteritems(), key=lambda x: x[1])[-100:]
    print 'Top 100 sizes:'
    print '\t'.join(map(lambda x: '{}:{}'.format(*x), sizes_10))
    
    # extract 10 biggest intensity variations
    intensitydist_10 = sorted(statistics.get_intensity_distributions().iteritems(), key=lambda x: x[1])[-100:]
    print 'Top 100 intensity distributions:'
    print '\t'.join(map(lambda x: '{}:{}'.format(*x), intensitydist_10))
    
    print 'Regions that appear in both top 100:'
    for i in [x[0] for x in sizes_10]:
        if i in [x[0] for x in intensitydist_10]:
            print 'region {} detected in both'.format(i)
            
    print 'Sizes and intensity distributions of the 100 largest regions:'
    j = 0
    for label, size in sizes_10:
        j += 1
        print '({}) {}: {} / {}'.format(j, label, size, statistics.get_intensity_distributions()[label])
        
            
    print 'Sizes and intensity distributions of the 100 worst intensity distributions:'
    j = 0
    for label, intensity in intensitydist_10:
        j += 1
        print '({}) {}: {} / {}'.format(j, label, statistics.get_sizes()[label], intensity)        
    
    # save statistics
    logger.info('Extracting and saving general statistics in {}'.format(file_general_name))
    with open(file_general_name, 'w') as f:
        f.write('#{}\n'.format(label_image_name))
        f.write('number-of-labels\t{}\n'.format(statistics.get_label_count()))
        f.write('consecutive-labels\t{}\n'.format(statistics.labels_are_consecutive()))
        f.write('min-label-index\t{}\n'.format(statistics.get_min_label()))
        f.write('max-label-index\t{}\n'.format(statistics.get_max_label()))
        f.write('smallest-label\t{}\n'.format(min(statistics.get_sizes().values())))
        f.write('biggest-label\t{}\n'.format(max(statistics.get_sizes().values())))
        f.write('min-image-intensity\t{}\n'.format(statistics.get_min_intensity()))
        f.write('max-image-intensity\t{}\n'.format(statistics.get_max_intensity()))
    
    logger.info('Extracting and saving sphericity histogram in {}...'.format(file_sphericity_name))
    with open(file_sphericity_name, 'w') as f:
        f.write('#value\toccurrences\n')
        
    logger.info('Extracting and saving label size histogram in {}...'.format(file_regionsize_name))
    with open(file_regionsize_name, 'w') as f:
        f.write('#value\toccurrences\n')
        size_histogram = statistics.get_size_histogram()
        for value, occurrences in zip(size_histogram[1], size_histogram[0]):
            f.write('{}\t{}\n'.format(value, occurrences))            
            
    logger.info('Extracting and saving intensity distribution histogram in {}...'.format(file_intensitydist_name))
    with open(file_intensitydist_name, 'w') as f:
        f.write('#value\toccurrences\n')
        intensitydist_histogram = statistics.get_intensity_distribution_histogram()
        for value, occurrences in zip(intensitydist_histogram[1], intensitydist_histogram[0]):
            f.write('{}\t{}\n'.format(value, occurrences))
            
    logger.info('Creating image with the 100 biggest regions...')
    label_image_data_size_top_10 = numpy.zeros_like(label_image_data)
    i = 0
    for label, _ in sizes_10:
        i += 1
        label_image_data_size_top_10[label == label_image_data] = i
    logger.info('Saving resulting image as {} with data-type int8...'.format(file_size_image_name))
    label_image_data_size_top_10 = image_like(label_image_data_size_top_10, label_image)
    label_image_data_size_top_10.get_header().set_data_dtype(numpy.int8) # bool sadly not recognized
    save(label_image_data_size_top_10, file_size_image_name)
    
    logger.info('Creating image with the 100 worst intensity distribution regions...')
    label_image_data_intensity_top_10 = numpy.zeros_like(label_image_data)
    i = 0
    for label, _ in intensitydist_10:
        i += 1
        label_image_data_intensity_top_10[label == label_image_data] = i
    logger.info('Saving resulting image as {} with data-type int8...'.format(file_intensity_image_name))
    label_image_data_intensity_top_10 = image_like(label_image_data_intensity_top_10, label_image)
    label_image_data_intensity_top_10.get_header().set_data_dtype(numpy.int8) # bool sadly not recognized
    save(label_image_data_intensity_top_10, file_intensity_image_name)    
                    
    logger.info('Successfully terminated.')

      
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('folder', help='The place to store the generated statistics files. They are named as the input label image with an added suffix.')
    parser.add_argument('label_image', help='The label image.')
    parser.add_argument('original_image', help='The original image.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()            
    