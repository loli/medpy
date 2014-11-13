#!/usr/bin/python

"""Simply returns the offset of the ES slices for a dataset."""

# build-in modules
import argparse

# third-party modules

# path changes

# own modules

# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-06-15"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
    Returns the offset of the ES slices for a dataset
    """

# code
def main():
    args = getArguments(getParser()) 
    
    with open(args.slicelist, 'r') as f:
        for line in f.readlines():
            sliceno = int(line.split('\\')[-1].split('-')[1])
            if not 0 == sliceno % 20:
                print(sliceno % 20)
                return
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('slicelist', help='The slice list associated with the dataset.')
    return parser

if __name__ == "__main__":
    main()     