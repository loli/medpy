#!/usr/bin/python

"""
Executes gradient anisotropic diffusion over images.

Copyright (C) 2013 Oskar Maier

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# build-in modules
import argparse
import logging
import os

# third-party modules
import itk

# path changes

# own modules
from medpy.core import Logger
import medpy.itkvtk.utilities.itku as itku


# information
__author__ = "Oskar Maier"
__version__ = "r0.2.0, 2011-12-09"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Smoothed the input image using gradient anisotropic diffusion
                  with a range of parameters.
                  The resulting image is saved in the supplied folder with the same
                  name as the input image, but with a suffix '_smoothed_[parameters]'
                  attached.
                  
                  Copyright (C) 2013 Oskar Maier
                  This program comes with ABSOLUTELY NO WARRANTY; This is free software,
                  and you are welcome to redistribute it under certain conditions; see
                  the LICENSE file or <http://www.gnu.org/licenses/> for details.   
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
        
    # load image as float using ITK
    logger.info('Loading image {} as float using ITK...'.format(args.image))
    image_type = itk.Image[itk.F, 4] # causes PyDev to complain -> ignore error warning
    reader = itk.ImageFileReader[image_type].New()
    reader.SetFileName(args.image)
    reader.Update()
    
    logger.debug(itku.getInformation(reader.GetOutput()))
    
    # process/smooth with anisotropic diffusion image filters (which preserves edges)
    # for watershed one could use 20 iterations with conductance = 1.0
    logger.info('Smoothing...')
    for iteration in args.iterations:
        for conductance in args.conductances:
            for timestep in args.timesteps:
                # build output image name
                image_smoothed_name = '.'.join(args.output.split('.')[:-1]) # remove file ending
                image_smoothed_name += '_i{}_c{}_t{}.'.format(iteration, conductance, timestep) # add parameter suffix
                image_smoothed_name += args.output.split('.')[-1]
                
                # check if output image exists
                if not args.force:
                    if os.path.exists(image_smoothed_name):
                        logger.warning('The output image {} already exists. Skipping this step.'.format(image_smoothed_name))
                        continue
                
                # execute the smoothing
                logger.info('Smooth with settings: iter={} / cond={} / tstep={}...'.format(iteration, conductance, timestep))
                image_smoothed = itk.GradientAnisotropicDiffusionImageFilter[image_type, image_type].New()
                image_smoothed.SetNumberOfIterations(iteration)
                image_smoothed.SetConductanceParameter(conductance)
                image_smoothed.SetTimeStep(timestep)
                image_smoothed.SetInput(reader.GetOutput())
                image_smoothed.Update()
                
                logger.debug(itku.getInformation(image_smoothed.GetOutput()))
                
                # save file
                logger.info('Saving smoothed image as {}...'.format(image_smoothed_name))
                writer = itk.ImageFileWriter[image_type].New()
                writer.SetFileName(image_smoothed_name)
                writer.SetInput(image_smoothed.GetOutput())
                writer.Update()
    
    logger.info('Successfully terminated.')
        
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    args.iterations = map(float, args.iterations.split(','))
    args.conductances = map(float, args.conductances.split(','))
    args.timesteps = map(float, args.timesteps.split(','))
    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('image', help='The input image.')
    parser.add_argument('output', help='The output image.')
    parser.add_argument('iterations', help='A colon separated list of values to be passed to the iteration attribute.')
    parser.add_argument('conductances', help='A colon separated list of values to be passed to the conductances attribute.')
    parser.add_argument('timesteps', help='A colon separated list of values to be passed to the timestep attribute. The maximum allowable time step for this filter is 1/2^N, where N is the dimensionality of the image. For 2D images any value below 0.250 is stable, and for 3D images, any value below 0.125 is stable.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    
    return parser    
    
if __name__ == "__main__":
    main()        