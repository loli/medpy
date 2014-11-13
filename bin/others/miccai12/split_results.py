#!/usr/bin/python

"""Splits a (MICCAI'12) results file to evaluate the results also according to basal, mid and apical slices."""

# build-in modules
import argparse
import logging

# third-party modules

# path changes

# own modules
from medpy.core import Logger


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.0, 2012-08-07"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = """
                The scores created by the MICCAI'12 evaluation script do not include a
                differentiation between the type of slices.
                
                This script takes an _ImageResults.txt, as created by the script, and
                returns the results received in the basal (first 3), apical (last 3) and
                mid slices.
                
                The result is printed to the screen.
                """
                
# code
def main():
    args = getArguments(getParser())

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)
    
    # collect slice-wise results and compute average
    results_i, results_o = parseImageResults(args.score)
    results_i = splitResults(results_i)
    results_o = splitResults(results_o)
    

    # print results
    if args.csv:
        print('Inner contours')
        csvPrintResults(results_i)
        print('Outer contours')
        csvPrintResults(results_o)
    else:
        print("########## Inner contours ##########")
        prettyPrintResults(results_i)
        print("####################################")
        print()
        
        print("########## Outer contours ##########")
        prettyPrintResults(results_o)
        print("####################################")
    
def csvPrintResults(results):
    """
    Prints the results in a CSV format, using ":" as deliminator.
    """
    print(';;DM;HD')
    print('Basal;ED;{};{}'.format(results[0]['ed'][0], results[0]['ed'][1]))
    print(';ES;{};{}'.format(results[0]['es'][0], results[0]['es'][1]))
    print('Mid;ED;{};{}'.format(results[1]['ed'][0], results[1]['ed'][1]))
    print(';ES;{};{}'.format(results[1]['es'][0], results[1]['es'][1]))
    print('Apical;ED;{};{}'.format(results[2]['ed'][0], results[2]['ed'][1]))
    print(';ES;{};{}'.format(results[2]['es'][0], results[2]['es'][1]))
    
def prettyPrintResults(results):
    """
    Prints the results for all slice types in a pretty formated way.
    """
    print('Basal (first three) slices:')
    _prettyPrintResults(results[0])
    print('Mid slices:')
    _prettyPrintResults(results[1])
    print('Apical (last three) slices:')
    _prettyPrintResults(results[2])
    
def _prettyPrintResults(results):
    """
    Prints the results for a slice type in a pretty formated way.
    """
    print('\t{:>12}\t{:>12}'.format('DM', 'HD'))
    print('ED:\t{:12.4f}\t{:12.4f}'.format(results['ed'][0], results['ed'][1]))
    print('ES:\t{:12.4f}\t{:12.4f}'.format(results['es'][0], results['es'][1]))
    
def splitResults(results):
    """
    Splits the results (of either inner or outer contours) into the respective slice-wise
    results and return the average scores.
    """ 
    # split into basal, mid and apical results
    results_basal = {'ed': [[], []], 'es': [[], []]}
    results_mid = {'ed': [[], []], 'es': [[], []]}
    results_apical = {'ed': [[], []], 'es': [[], []]}
    
    # iterate over results and collect in convenient lists
    for patient in results:
        # ed dm results
        results_basal['ed'][0].extend(results[patient]['ed'][0][:3])
        results_mid['ed'][0].extend(results[patient]['ed'][0][3:-3])
        results_apical['ed'][0].extend(results[patient]['ed'][0][-3:])
        # ed hd results
        results_basal['ed'][1].extend(results[patient]['ed'][1][:3])
        results_mid['ed'][1].extend(results[patient]['ed'][1][3:-3])
        results_apical['ed'][1].extend(results[patient]['ed'][1][-3:])
        # es dm results
        results_basal['es'][0].extend(results[patient]['es'][0][:3])
        results_mid['es'][0].extend(results[patient]['es'][0][3:-3])
        results_apical['es'][0].extend(results[patient]['es'][0][-3:])
        # es hd results
        results_basal['es'][1].extend(results[patient]['es'][1][:3])
        results_mid['es'][1].extend(results[patient]['es'][1][3:-3])
        results_apical['es'][1].extend(results[patient]['es'][1][-3:])
        
    # compute average and return
    results_basal['ed'][0] = sum(results_basal['ed'][0]) / float(len(results_basal['ed'][0]))
    results_basal['ed'][1] = sum(results_basal['ed'][1]) / float(len(results_basal['ed'][1]))
    results_basal['es'][0] = sum(results_basal['es'][0]) / float(len(results_basal['es'][0]))
    results_basal['es'][1] = sum(results_basal['es'][1]) / float(len(results_basal['es'][1]))
    
    results_mid['ed'][0] = sum(results_mid['ed'][0]) / float(len(results_mid['ed'][0]))
    results_mid['ed'][1] = sum(results_mid['ed'][1]) / float(len(results_mid['ed'][1]))
    results_mid['es'][0] = sum(results_mid['es'][0]) / float(len(results_mid['es'][0]))
    results_mid['es'][1] = sum(results_mid['es'][1]) / float(len(results_mid['es'][1]))
    
    results_apical['ed'][0] = sum(results_apical['ed'][0]) / float(len(results_apical['ed'][0]))
    results_apical['ed'][1] = sum(results_apical['ed'][1]) / float(len(results_apical['ed'][1]))
    results_apical['es'][0] = sum(results_apical['es'][0]) / float(len(results_apical['es'][0]))
    results_apical['es'][1] = sum(results_apical['es'][1]) / float(len(results_apical['es'][1]))
    
    return (results_basal, results_mid, results_apical)
    
def parseImageResults(file):
    """
    Parses the image results in file and returns a construct with the read-in scores.
    """
    phases = 20 # constant
    
    results_i = {}
    results_o = {}
    
    with open(file, 'r') as f:
        for line in f.readlines():
            # extract and pre-process information
            descriptor, dm, hd = line.split(' ')
            patient, slno, kind = descriptor.split('-')
            patient = patient[1:]
            dm = float(dm)
            hd = float(hd)
            slno = int(slno)
            
            # select result dictionary
            if 'i' == kind: r = results_i
            else: r = results_o
            
            # eventually create entry
            if not patient in r: r[patient] = {'ed': ([], []), 'es': ([], [])}
                
            # decide if ed or es slice
            if 0 == slno % phases: phasename = 'ed'
            else: phasename = 'es' 
            
            # add results from line    
            r[patient][phasename][0].append(dm)
            r[patient][phasename][1].append(hd)
        
    return (results_i, results_o)
    
def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('score', help='The _ImageResults.txt file as produced by the MICCAI\'12 evaluation script.')
    parser.add_argument('-c', dest='csv', action='store_true', help='Print results in CSV format.')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    return parser

if __name__ == "__main__":
    main() 
    