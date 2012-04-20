#!/usr/bin/python

import argparse

def main():
    # parse cmd arguments
    parser = getParser()
    args = getArguments(parser)
    
    # %image;bterm;%sigma
    base = '{};{};{}'.format(args.image, args.bterm, args.sigma)
    
    with open(args.time, 'r') as f:
        time_data = map(str.strip, f.readline().split(';'))
    
    with open(args.evaluation, 'r') as f:
        f.readline() # remove header
        evaluation_data = map(str.strip, f.readline().split(';'))
        
    err = False
    if not 3 == len(time_data):
        err = "Corrupted time file ({}).".format(args.time)
    elif not 7 == len(evaluation_data):
        if 3 == len(evaluation_data):
            err = "{};{};{};{};{};Could not evaluate (reason: {}).".format(evaluation_data[0], time_data[0], time_data[1], time_data[2], evaluation_data[1], evaluation_data[2])
        else:
            err = "{};{};{};{};Corrupted evaluation file ({}).".format("unknown", time_data[0], time_data[1], time_data[2], args.evaluation)
        
    with open(args.result, 'a') as f:
        if err:
            f.write('{};{}\n'.format(base, err))
        else:
            # '%file;%time;%maxmem;%memswaps;%msksize;%voe;%rvd;%assd;%mssd;%rmsssd'
            f.write('{};{};{};{};{};{};{};{};{};{};{}\n'.format(base,
                evaluation_data[0],
                time_data[0],
                time_data[1],
                time_data[2],
                evaluation_data[1],
                evaluation_data[2],
                evaluation_data[3],
                evaluation_data[4],
                evaluation_data[5],
                evaluation_data[6]))
        

def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description="Temporary script for an experiment that can parse a certain time output file and an evaluation file to add them combined as a line to another file.")
    parser.add_argument('image')
    parser.add_argument('bterm')
    parser.add_argument('sigma')
    parser.add_argument('time', help='Output-file of time in format E;M;W.')
    parser.add_argument('evaluation', help='Evaluation file in the usual format.')
    parser.add_argument('result', help='Result csv file to which to append the parsed information.')
    return parser    

if __name__ == "__main__":
    main()