#!/usr/bin/env python

"Temporary script for fast executions of code."

# build-in modules
import argparse
import logging

# third-party modules

# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save
from scipy import ndimage


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-05-25"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                  Temporary scripts.
                  """

# code
def main():
    args = getArguments(getParser())
    
    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    with open(args.output, 'w') as outf:        
        outf.write('C;;E;;D;;ED;(std);ES;(std);Total;(std)')        
        with open(args.input, 'r') as inf:            
            for line in inf.readlines():                
                line = line.strip()                
                if 'ced' == line[0:3]:
                    _tmp = line.split('_')[1:]
                    _c = _tmp[0].split('-')
                    _e = _tmp[1].split('-')
                    _d = _tmp[2].split('-')
                    outf.write('\n')
                    outf.write('{};{};{};{};{};{};'.format(_c[0][1:], _c[1], _e[0][1:], _e[1], _d[0][1:], _d[1]))
                elif 'Mean (std) endo DM' in line:
                    _tmp = line.split(' ')
                    outf.write('{};{};{};{};'.format(_tmp[5], _tmp[6], _tmp[8], _tmp[9]))
                elif 'Total mean (std) endo DM' in line:
                    _tmp = line.split(' ')
                    outf.write('{};{}'.format(_tmp[5], _tmp[6]))
    
    logger.info("Successfully terminated.")    
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Silently override existing output images.')
    return parser    

if __name__ == "__main__":
    main()        