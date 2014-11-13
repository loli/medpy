#!/usr/bin/python

"""Allow to plot a slice of an image with a masked area coloured."""

# build-in modules
import argparse

# third-party modules
import Gnuplot
import numpy
from nibabel.loadsave import load
from argparse import ArgumentError

# path changes

# own modules


# information
__author__ = "Oskar Maier"
__version__ = "d0.1.0, 2012-01-30"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Development"
__description__ = """
                  Takes an images as first and a mask as second input. Displays the image
                  as gnuplot topographical graph with the masked area coloured
                  differently. When displayed, it is possible to browse interactively
                  through the slices.
                  Requires gnuplot to be available as command on the system.
                  """

# code
def main():
    # parse cmd arguments
    parser = getParser()
    parser.parse_args()
    args = getArguments(parser)
    
    # load image data
    image_data = numpy.squeeze(load(args.image).get_data())
    mask_data = numpy.squeeze(load(args.mask).get_data()).astype(numpy.bool_)
    
    # sample data
    image_data = image_data[::args.sample[0], ::args.sample[1], ::args.sample[2]]
    mask_data = mask_data[::args.sample[0], ::args.sample[1], ::args.sample[2]]
    
    # check dimensions to be equal
    if image_data.shape != mask_data.shape:
        raise ArgumentError("The images dimensions are not euqal!")
    
    # extract relevant area from image_data
    highlighted_data = image_data.copy()
    highlighted_data[~mask_data] = image_data.min()
    
    # set the same values in the image to zero
    image_data[mask_data] = image_data.min()
    
    # load gnuplot
    g = Gnuplot.Gnuplot(debug=1)
    
    # set static gnuplot parameters
    g('set style data lines')
    g('set surface \n')
    g('set hidden3d\n')
    g('set view 60, 30, 1, 1\n')
    g('set key right\n')
    g('set xlabel "X"\n')
    g('set ylabel "Y"\n')
    g('set zlabel "Value"\n')
    g('set autoscale\n')

    # set default parameters
    dim = 0
    sl = 0
    getch = _Getch()
    
    # infinite loop 
    while True:
        # prepare slices
        sls =[]
        for i in range(image_data.ndim):
            if i == dim:
                sls.append(slice(sl, sl+1))
            else:
                sls.append(slice(None))
        sl_image = numpy.squeeze(image_data[sls])
        sl_highlighted = numpy.squeeze(highlighted_data[sls])
        
        # set variable gnuplot parameters
        g('set title "Topographical image axis={}/{}, slice={}/{}"\n'.format(dim + 1, image_data.ndim, sl + 1, image_data.shape[dim]))
        g('set zrange [{}:{}]\n'.format(image_data.min(), image_data.max()))
        
        # create temp files for matrix processing
        # plot
        image_plot = Gnuplot.GridData(sl_image,
                                      list(range(sl_image.shape[0])),
                                      list(range(sl_image.shape[1])),
                                      title='data outside mask',
                                      binary=0)
        #image_plot = Gnuplot.Data(sl_image, title='data out of mask')
        highlighted_plot = Gnuplot.GridData(sl_highlighted,
                                            list(range(sl_highlighted.shape[0])),
                                            list(range(sl_highlighted.shape[1])),
                                            title='data inside mask',
                                            binary=0)
        #highlighted_plot = Gnuplot.Data(sl_highlighted, title='data inside mask')
        g.splot(image_plot, highlighted_plot)
        
        # wait for key
        print("d/a = slices +/-; s/w = dimension +/-; e/q = slices +/- 10; ESC = exit\n")
        ch = getch()
        
        # check key pressed
        if 'a' == ch: # sl - 1
            sl = max(0, sl - 1)
        elif 'd' == ch: # sl + 1
            sl = min(image_data.shape[dim] - 1, sl + 1)
        elif 'w' == ch: # dimension - 1
            dim = max(0, dim - 1)
            sl = min(image_data.shape[dim] - 1, sl)
        elif 's' == ch: # dimension + 1
            dim = min(image_data.ndim - 1, dim + 1)
            sl = min(image_data.shape[dim] - 1, sl)
        elif 'q' == ch: # sl - 10
            sl = max(0, sl - 10)
        elif 'e' == ch: # sl + 10
            sl = min(image_data.shape[dim] - 1, sl + 10)
        elif "" == ch: break # ESC or other unknown char
        else: "Unrecognized key"
    
    #close the gnuplot window
    g('quit\n')
      
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    try:
        sample = int(args.sample)
        args.sample = (sample, sample, sample)
    except ValueError as e:
        args.sample = list(map(int, args.sample.split(',')))
    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)

    parser.add_argument('image', help='The image.')
    parser.add_argument('mask', help='The mask.')
    parser.add_argument('sample', help='The sample rate (an int or three colon separated ints). Use a value like 5 or 10 for an initial observation. When interested in one axis, set its sample rate to 1 and the other as low as your machine allows.')
    
    return parser

#def __save_as_gnuplot_grid(image_slice):
#    """
#    Takes a 2D image_slice and saves it as gnuplot matrix data.
#    @return the file name of the created temp-file.
#    """
#    with tempfile.NamedTemporaryFile(delete=False) as f:
#        f.write('#X\tY\tZ\n')
#        for x in range(image_slice.shape[0]):
#            f.write('\t'.join(map(str, image_slice[x])))
#            f.write('\n')
#        return f.name
    
class _Getch:
    """
    Gets a single character from standard input.  Does not echo to the
    screen.
    """
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch() 
    
if __name__ == "__main__":
    main()            
