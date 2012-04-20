#!/usr/bin/python

import argparse
import subprocess
import os
import scipy.stats

__description__ = "Temporary script to create fitting plots for all combinations between some attributes and some target sigmas."

___gpl_script__ = """
set term postscript eps enhanced color
set output '{}.eps'
set title "{} vs. Sigma fitting plot"
set xlabel "{}"
set ylabel "sigma"

plot '{}' using 2:3 with points lw 4 notitle
"""

def main():
    args = getArguments(getParser())
    
    # prepare data and access list 
    keys = ['image', 'bterm', 'sigma', 'filename', 'time', 'max_memory', 'memory_swaps', 'mask_size', 'voe', 'rvd', 'assd', 'mssd', 'rmsssd']
    data = []
    
    # parse data on by-line basis
    with open(args.results, 'r') as f:
        f.readline() # skip header line
        for line in f.readlines():
            values = line.strip().split(';')
            if not 13 == len(values):
                print 'Notice: Ignoring corrupted line [{}].'.format(line.strip()) 
                continue
            image = int(values[0])
            bterm = values[1].strip()
            sigma = float(values[2])
            filename = values[3].strip()
            max_memory, memory_swaps, mask_size = map(int, values[5:8])
            voe, rvd, assd, mssd, rmsssd = map(float, values[8:13])
            # split time into hh:mm:ss.ms
            time = values[4].strip().split(':')
            if not 3 == len(time): time = [0] + time # add hour if not present
            time = map(int, time[:-1]) + map(int, time[-1].strip().split('.')) # break last entry into seconds and milliseconds
            if not 4 == len(time): time = time + [0] # add milliseconds if not present
            if args.bterm == bterm: # filte out entries that do not belong to the supplied bterm
                data.append([image, bterm, sigma, filename, time, max_memory, memory_swaps, mask_size, voe, rvd, assd, mssd, rmsssd])
            
    # compute additional additional statistical terms such as score
    # Note: The score calculations follow the schema of the MICCAI07 cgrand challenge
    keys.extend(['voe_score', 'rvd_score', 'assd_score', 'mssd_score', 'rmsssd_score', 'score'])
    for entry in data:
        voe_score = max(100 - 25 * entry[keys.index('voe')]/6.4, 0)
        rvd_score = max(100 - 25 * abs(entry[keys.index('rvd')])/4.7, 0)
        assd_score = max(100 - 25 * entry[keys.index('assd')]/1, 0)
        mssd_score = max(100 - 25 * entry[keys.index('mssd')]/19, 0)
        rmsssd_score = max(100 - 25 * entry[keys.index('rmsssd')]/1.8, 0)
        score = sum([voe_score, rvd_score, assd_score, mssd_score, rmsssd_score]) / 5.
        entry.extend([voe_score, rvd_score, assd_score, mssd_score, rmsssd_score, score]) 
            
    # CREATE STATISTICS GROUPED BY IMAGE, CROP THEM BY X AND AND BOXPLOT THE SIGMA
    data_image, keys_image = __group_by(data, keys, 'image')
    
    # statistics of best score that do not differ more than one percent
    data_image = __select_best(data_image, keys_image, 'score', args.bestx) # crop by score
    for key in data_image.iterkeys():
        data_image[key] = __compute_boxplot(data_image[key][keys_image.index('sigma')]) # compute statistics over sigma
    
    
    
    # parse candidate file
    with open(args.attributes, 'r') as f:
        cand_keys = f.readline().strip().split(';')[1:] # header as keys
        cand_data = []
        for line in f.readlines():
            cand_data.append(map(float, line.strip().split(';')[1:])) # skip image name, as ordering implicit
    
    # compute additional candidates by cross-substraction
    add_cand_keys = []
    for key in cand_keys[:-17]: # skip last 17, as real and boundary values
        for other in cand_keys[cand_keys.index(key)+1:-17]:
            add_cand_keys.append('{}-{}'.format(key, other))
            for image in cand_data: # for each image
                value = image[cand_keys.index(key)] - image[cand_keys.index(other)]
                image.append(value)
    cand_keys.extend(add_cand_keys)
    
    
    # create plot for each candidate
    for key in cand_keys:
        print "Plotting sigma to {}".format(key)
        __plot_key(key, cand_data, cand_keys, data_image, args)
    
    
    # compute correlations between sigmas and attributes
    sigma_row = []
    for image in data_image.itervalues():
        sigma_row.append(image[0]) # mean value
    
    pearson = []
    spearman = []
    pointbiserial = []
    kendalltau = []
    for key in cand_keys:
        data_row = []
        for image in cand_data:
            data_row.append(image[cand_keys.index(key)])
        # compute correlations
        pearson.append(list(scipy.stats.pearsonr(sigma_row, data_row)) + [key])
        spearman.append(list(scipy.stats.spearmanr(sigma_row, data_row)) + [key])
        pointbiserial.append(list(scipy.stats.pointbiserialr(sigma_row, data_row)) + [key])
        kendalltau.append(list(scipy.stats.kendalltau(sigma_row, data_row)) + [key])
        
    # print best correlations
    def abs_cmp(x, y):
        x = abs(x)
        y = abs(y) 
        if x > y: return 1
        elif x == y: return 0
        else: return -1
    x = 5
    print 'Best {} Pearson correlations:'.format(x)
    pearson.sort(cmp=abs_cmp, reverse=True, key=lambda x: x[0])
    for entry in pearson[:x]: print entry
    
    print 'Best {} Spearman correlations:'.format(x)
    spearman.sort(cmp=abs_cmp, reverse=True, key=lambda x: x[0])
    for entry in spearman[:x]: print entry
    
    print 'Best {} Pointbiserial correlations:'.format(x)
    pointbiserial.sort(cmp=abs_cmp, reverse=True, key=lambda x: x[0])
    for entry in pointbiserial[:x]: print entry
    
    print 'Best {} Kendalltau correlations:'.format(x)
    kendalltau.sort(cmp=abs_cmp, reverse=True, key=lambda x: x[0])
    for entry in kendalltau[:x]: print entry
    
                             
    
    
    
    print "Successfully terminated."

# helper functions
def __plot_key(key, cand_data, cand_keys, data_image, args):
    # create data file
    with open('{}_tmp.dat'.format(args.output), 'w') as f:
        f.write('#image\t{}\tsigma\n'.format(key))
        for idx, line in enumerate(cand_data):
            f.write('{}\t{}\t{}\n'.format(idx + 1, line[cand_keys.index(key)], data_image[idx+1][0])) # mean of sigma
    # create gnuplot file
    with open('{}_tmp.plt'.format(args.output), 'w') as f:
        f.write(___gpl_script__.format('{}_{}'.format(args.output, key), key, key, os.path.abspath('{}_tmp.dat'.format(args.output))))
    # run gnuplot file
    cmd = 'gnuplot ' + '{}_tmp.plt'.format(args.output)
    subprocess.call(cmd, shell=True)
    

def __write_file_boxplot(file_name, data, grouped_by):
    with open(file_name, 'w') as f:
        f.write('#{}\tmean\tmedian\tlower_quartile\tupper_quartile\tmin\tmax\tlower_iqr\tupper_iqr\n'.format(grouped_by))
        for attribute, values in data.iteritems():
            f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(attribute, *values))

def __select_best(data_grouped, keys_grouped, attribute, offset):
    """
    Croppes the grouped data in a way, that it contains only the entries where attributes is in the upper offset values.
    """
    data_new = {}    
    for key, data in data_grouped.iteritems():
        # fun with sorting
        data_sorted = sorted(__swapaxes(data), key=lambda x: x[keys_grouped.index(attribute)], reverse=True)
        attribute_max_value = data_sorted[0][keys_grouped.index(attribute)]
        attribute_border_value = attribute_max_value - offset
        data_new[key] = []
        for value in data_sorted[0]: data_new[key].append([value])
        for entry in data_sorted[1:]:
            if entry[keys_grouped.index(attribute)] < attribute_border_value: break
            for idx, value in enumerate(entry):
                data_new[key][idx].append(value)
    return data_new

def __swapaxes(arr):
    """
    Swaps the two axes of a rectangular list-array.
    """
    arr_new = []
    for i in range(len(arr[0])):
        arr_new.append([])
        for entry in arr:
            arr_new[i].append(entry[i])
    return arr_new

def __group_by(data, keys, group_by):
    "Takes the data and the key lists and returns a list grouped by one attribute and a new access key."
    new_data = {}
    for entry in data:
        collection = entry[:keys.index(group_by)] + entry[keys.index(group_by) + 1:]
        if entry[keys.index(group_by)] in new_data:
            for idx, value in enumerate(collection):
                new_data[entry[keys.index(group_by)]][idx].append(value)
        else:
            new_data[entry[keys.index(group_by)]] = []
            for value in collection:
                new_data[entry[keys.index(group_by)]].append([value])             
    return new_data, keys[:keys.index(group_by)] + keys[keys.index(group_by) + 1:]

def __compute_boxplot(data):
    """
    Computes a number of statistical value over the supplied discrete data set that can
    be used for box-plots.
    """
    if 0 == len(data): return 0,0,0,0,0,0,0
    data = sorted(data)
    if 0 == len(data)%2: # even
        median = (data[len(data)/2-1] + data[len(data)/2])/2.
        left = data[:len(data)/2]
        right = data[len(data)/2:]
    else: # odd
        median = data[(len(data)+1)/2-1]
        left = data[:(len(data)+1)/2]
        right = data[(len(data)+1)/2-1:]
        
    lower_q = __compute_median(left)
    upper_q = __compute_median(right)
    
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
        
    mean = sum(data) / float(len(data)) 
    
    return mean, median, lower_q, upper_q, min(left), max(right), lower_border, upper_border
    
def __compute_median(data):
    """
    Computes the median of a discrete data set.
    """
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
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('bterm', help='The boundary term to use.')
    parser.add_argument('results', help='Original, cleaned up results file.')
    parser.add_argument('attributes', help='The attributes file.')
    parser.add_argument('bestx', type=int, help='How many of the best scoring sigmas to combine.')
    parser.add_argument('output', help='Folder + basename to create the resulting fitting plots in.')
    return parser    

if __name__ == "__main__":
    main()        