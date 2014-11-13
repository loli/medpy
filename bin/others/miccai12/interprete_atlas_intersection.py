#!/usr/bin/python

"""Interpretes the results obtained by the check_intersection_atlas script."""

# build-in modules
import math
import argparse
import logging
from argparse import ArgumentError

# third-party modules

# path changes

# own modules
from medpy.core import Logger


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.1, 2012-08-07"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
    Takes a number of statistical CSV files and produces a statistic averaged over all images.

    Also prints some recommondations.
    """

# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)  
    
    # prepare static value container
    data_ed = dict()
    data_es = dict()
    
    # read in statistics from supplied files
    for statistic in args.statistics:
        with open(statistic, 'r') as f:
            line = f.readline()
            line = line.strip()
            threshold = line.split(';')[1]
            
            if not threshold in data_ed: data_ed[threshold] = []
            if not threshold in data_es: data_es[threshold] = []
            
            esmode = False
            for line in f.readlines():
                line = line.strip()
                if 0 == len(line): continue
                
                if 'ED' in line:
                    esmode = False
                    continue
                
                if 'ES' in line:
                    esmode = True
                    continue
                
                if '"' == line[0]: continue # title line
            
                values = list(map(float, line.split(';')))
                slid = int(values[0])
            
                if not esmode:
                    while slid >= len(data_ed[threshold]): data_ed[threshold].append([])
                    data_ed[threshold][slid].append(values[1:])
                else:            
                    while slid >= len(data_es[threshold]): data_es[threshold].append([])
                    data_es[threshold][slid].append(values[1:])
                
    # average the slice-wise values by their own length and remove empty ones
    for thr in data_ed:
        for i in range(len(data_ed[thr])):
            data_ed[thr][i] = [mean(l) for l in zip(*data_ed[thr][i])]
                
    for thr in data_es:
        for i in range(len(data_es[thr])):
            data_es[thr][i] = [mean(l) for l in zip(*data_es[thr][i])]
                
    # save threshold-wise results in csv files
    for thr in data_ed:
        make_csv(args.output.format(thr), data_ed[thr], data_es[thr])
            
            
    # Constant selections criteria

    # The FG rating is composed of two components, both expressed as percentages of the total real contour size:
    #    (1) the voxels rightly classified as FG
    #    (2) the voxels wrongly classified as FG
    # Both are important terms, therefore two different approaches exist:
    #    (a) For the minimal error approach, the wrongly classified voxels are penalized strongly when dropping under 0.05.
    #        Therefore the amount of righly classified voxels is only of minor importance.
    #    (b) For the maximum coverage approach, the wrongly classified voxels are penalized strongly when dropping under 0.15.
    #        Therefore the amount of righly classified voxels becomes more decisive.
    # (1): Only a value of 1.0 gives full score of 1, a value of 0.0 gives a score of 0.0.
    #    f1(x) = -1 * ((2)^(1/1))^(1-x) + 2
    # (2a): Only a value of 0.0 gives the full score of 1, a value of 0.15 already gives a score of 0.
    #    f2(x) = -1 * (2^(1/0.05))^x + 2
    # (2b): Only a value of 0.0 gives the full score of 1, a value of 0.30 already gives a score of 0.
    #    f2(x) = -1 * (2^(1/0.15))^x + 2
    fg_f1 = lambda x: -1. * math.pow(math.pow(2., 1. / 1.), 1 - x) + 2
    fg_f2a = lambda x: -1. * math.pow(math.pow(2., 1. / 0.15), x) + 2
    fg_f2b = lambda x: -1. * math.pow(math.pow(2., 1. / 0.30), x) + 2
    fg_rating = lambda v: (fg_f1(v[0]) + fg_f2a(v[1])) / 2.
    
    # The BG rating is composed of two components, both expressed as percentages of the total real contour size:
    #     (1) the score for the voxels which are wrongly assigned as bg
    #     (2) the score for the size of the area left undefined to be determined by the graph cut
    # The more important and therefore more influential part is (1), the less influential part is (2).
    # (1): Only a value of 0.0 gives the full score of 1, a value of 0.05 already gives a score of 0.
    #     f1(x) = -1 * (2^(1/0.05))^x + 2
    # (2): A value of 1 means perfect segmentation and gets the full score of 1; a value of 3 still gives a score of 0.5.
    #     f2(x) = 1 if x < 1 else -1 * ((2-0.5)^(1/(3-1))^(x-1) + 2
    # Both are combined to their average to achieve the total score.
    bg_f1 = lambda x: -1. * math.pow(math.pow(2., 1. / 0.05), x) + 2
    bg_f2 = lambda x: 1. if x < 1. else -1. * math.pow(math.pow(2. - 0.5, 1. / (3. - 1.)), x - 1.) + 2
    bg_rating = lambda v: (bg_f1(v[1]) + bg_f2(v[2])) / 2.
    
    
    if not args.bg:
        rating = fg_rating
    else:
        rating = bg_rating
    
    # select the best threshold for each slice
    print_optimal('ED', data_ed, rating)
    print_optimal('ES', data_es, rating)
    
def print_optimal(phase, data, rating):
    
    # dertemine maximu length
    maxl = 0
    for l in data.values():
        if len(l) > maxl: maxl = len(l)
    
    print('Optimal settings according to the selection registration approach:')
    print('{} phase:'.format(phase))
    print('slid\tthr\trating\t\tvalues (rightly classified (%), wrongly classified, undefined (%))')
    ratings = []
    for slid in range(maxl):
        best_value = False
        best_thr = False
        sbest_value = False
        sbest_thr = False      
        for thr in data:
            if slid < len(data[thr]):
                if not best_value:
                    best_value = data[thr][slid]                    
                    best_thr = thr
                elif rating(data[thr][slid]) > rating(best_value):
                    sbest_value = best_value 
                    best_value = data[thr][slid]
                    sbest_thr = best_thr
                    best_thr = thr
                elif False == sbest_value or rating(data[thr][slid]) > rating(sbest_value):
                    sbest_value = data[thr][slid]
                    sbest_thr = thr
        ratings.append(rating(best_value))
        print('{}\t{}\t{:.3f}\t\t{:.3f}\t{:.3f}\t{:.3f} (first)'.format(slid, best_thr, rating(best_value), *best_value))
        print('\t{}\t{:.3f}\t\t{:.3f}\t{:.3f}\t{:.3f} (second)'.format(sbest_thr, rating(sbest_value), *sbest_value))
    print('average rating: {}'.format(sum(ratings)/float(len(ratings))))    
    
def make_csv(name, edstats, esstats):
    """
    Creates a csv files with the results obtained for one threshold averaged over all images.
    """
    
    average_ed = [mean(l) for l in zip(*edstats)]
    average_es = [mean(l) for l in zip(*esstats)]
    
    with open(name, 'w') as f:
        f.write('ED slices')
        f.write('"sliceno (from basal down)";"rightly classified (%)";"wrongly classified (%)";"undefined (%)"\n')
        for slid, entry in enumerate(edstats):
            f.write('{};{};{};{}\n'.format(slid, *entry))
        
        f.write('"mean";{};{};{}\n'.format(*average_ed))
        
        f.write('ES slices')
        f.write('"sliceno (from basal down)";"rightly classified (%)";"wrongly classified (%)";"undefined (%)"\n')
        for slid, entry in enumerate(edstats):
            f.write('{};{};{};{}\n'.format(slid, *entry))
        
        f.write('"mean";{};{};{}\n'.format(*average_es))
        
        edstats = list(edstats)
        edstats.extend(esstats)
        
        f.write('\n"total mean";{};{};{}'.format(*[mean(l) for l in zip(*esstats)]))
    
def write_results(f, title, sliceswise):
    """
    Write the standard csv file.
    """
    f.write('{}\n'.format(title))
    f.write('"sliceno (from basal down)";"rightly classified (%)";"wrongly classified (%)";"undefined (%)"\n')
    for slid, entry in enumerate(sliceswise): f.write('{};{};{};{}\n'.format(slid, *entry))

def mean(col):
    """Compute the mean value of a collection."""
    return sum(col)/float(len(col))
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    if not '{}' in args.output:
        raise ArgumentError('Could not find the string "{}" in the output file name.')
    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('output', help='Output CSV file, where to store the results. Must contain a {} in its name.')
    parser.add_argument('statistics', nargs='+', help='A number of statistics files.')
    parser.add_argument('-b', dest='bg', action='store_true', help='Process as bg results instead of fg results.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Override existing output files without prompting.')
    return parser

if __name__ == "__main__":
    main()     
