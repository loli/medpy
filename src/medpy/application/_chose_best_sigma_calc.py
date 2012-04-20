#!/usr/bin/python

import argparse

def main():
    args = getArguments(getParser())
    
    # load ideal sigma settings
    data = []
    with open(args.sigma, 'r') as f:
        f.readline()
        f.readline()
        for line in f.readlines():
            values = map(float, line.strip().split('\t'))
            if 1 == args.fit: median, lower_quartile, upper_quartile = values[1], values[2], values[3]
            elif 5 == args.fit: median, lower_quartile, upper_quartile = values[8], values[9], values[10]
            else: median, lower_quartile, upper_quartile = values[15], values[16], values[17]
            data.append((median, lower_quartile, upper_quartile))
            
    # load candidates
    candidates = {}
    with open(args.candidates, 'r') as f:
        headers = f.readline().strip().split('\t')
        for header in headers[1:13]: candidates[header] = []
        for line in f.readlines():
            values = map(float, line.strip().split('\t'))
            for key, value in zip(headers[1:13], values[1:13]):
                candidates[key].append(value)
    
    # compute differences
    for key in candidates.iterkeys():
        for i in range(len(candidates[key])):
            print key, i, candidates[key][i], data[i][0]
            candidates[key][i] = abs(candidates[key][i] - data[i][0])
            
    # compute statistics and save to file
    with open(args.output, 'w') as f:
        f.write('#x;type;medium;median;lower_q;upper_q;min;max;lower_border;upper_border\n')
        for idx, key in enumerate(candidates.keys()):
            f.write('{};{};{};{};{};{};{};{};{};{}\n'.format(
                idx,
                key,
                sum(candidates[key])/float(len(candidates[key])),
                *_compute_boxplot(candidates[key])))
        
def _compute_boxplot(data):
    data = sorted(data)
    if 0 == len(data)%2: # even
        median = (data[len(data)/2-1] + data[len(data)/2])/2.
        left = data[:len(data)/2]
        right = data[len(data)/2:]
    else: # odd
        median = data[(len(data)+1)/2-1]
        left = data[:(len(data)+1)/2]
        right = data[(len(data)+1)/2-1:]
        
    lower_q = _compute_median(left)
    upper_q = _compute_median(right)
    
    iqr = upper_q - lower_q
    lower_fence = lower_q - 1.5 * iqr
    upper_fence = upper_q + 1.5 * iqr
    
    left = sorted(left)
    for val in left:
        if val >= lower_fence:
            lower_border = val
            break
    
    right = sorted(right, reverse=True)
    for val in right:
        if val <= upper_fence:
            upper_border = val
            break 
    
    return median, lower_q, upper_q, min(left), max(right), lower_border, upper_border
    
def _compute_median(data):
    data = sorted(data)
    if 0 == len(data)%2: # even
        median = (data[len(data)/2-1] + data[len(data)/2])/2.
    else: # odd
        median = data[(len(data)+1)/2-1]
    return median

def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    return parser.parse_args()

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description="Temporary script for an experiment that can parse a certain time output file and an evaluation file to add them combined as a line to another file.")
    parser.add_argument('fit', help="1,5 or 10")
    parser.add_argument('sigma')
    parser.add_argument('candidates')
    parser.add_argument('output')
    return parser    

if __name__ == "__main__":
    main()        