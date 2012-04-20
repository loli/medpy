#!/usr/bin/python

import argparse

__description__ = "Temporary script: Parses the results of _run_experiments.py and creates a number of gnuplot-parsable statistic files."

def main():
    args = getArguments(getParser())
    
    # prepare data and access list 
    keys = ['image', 'bterm', 'sigma', 'filename', 'time', 'max_memory', 'memory_swaps', 'mask_size', 'voe', 'rvd', 'assd', 'mssd', 'rmsssd']
    data = []
    
    # parse data on by-line basis
    with open(args.input, 'r') as f:
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
            
    
    #####
    # CREATE STATISTICS GROUPED BY SIGMA
    #####
    data_sigma, keys_sigma = __group_by(data, keys, 'sigma')
    
    # score
    data_sigma_score = {}
    for key in data_sigma.iterkeys():
        data_sigma_score[key] = __compute_boxplot(data_sigma[key][keys_sigma.index('score')])
    __write_file_boxplot('{}_{}_{}.dat'.format(args.output, args.bterm, 'score'), data_sigma_score, 'sigma')
    
    # voe
    data_sigma_voe = {}
    for key in data_sigma.iterkeys():
        data_sigma_voe[key] = __compute_boxplot(data_sigma[key][keys_sigma.index('voe')])
    __write_file_boxplot('{}_{}_{}.dat'.format(args.output, args.bterm, 'voe'), data_sigma_voe, 'sigma')
    
    # rvd
    data_sigma_rvd = {}
    for key in data_sigma.iterkeys():
        data_sigma_rvd[key] = __compute_boxplot(data_sigma[key][keys_sigma.index('rvd')])
    __write_file_boxplot('{}_{}_{}.dat'.format(args.output, args.bterm, 'rvd'), data_sigma_rvd, 'sigma')
    
    # assd
    data_sigma_assd = {}
    for key in data_sigma.iterkeys():
        data_sigma_assd[key] = __compute_boxplot(data_sigma[key][keys_sigma.index('assd')])
    __write_file_boxplot('{}_{}_{}.dat'.format(args.output, args.bterm, 'assd'), data_sigma_assd, 'sigma')
    
    # mssd
    data_sigma_mssd = {}
    for key in data_sigma.iterkeys():
        data_sigma_mssd[key] = __compute_boxplot(data_sigma[key][keys_sigma.index('mssd')])
    __write_file_boxplot('{}_{}_{}.dat'.format(args.output, args.bterm, 'mssd'), data_sigma_mssd, 'sigma')
    
    # rmsssd
    data_sigma_rmsssd = {}
    for key in data_sigma.iterkeys():
        data_sigma_rmsssd[key] = __compute_boxplot(data_sigma[key][keys_sigma.index('rmsssd')])
    __write_file_boxplot('{}_{}_{}.dat'.format(args.output, args.bterm, 'rmsssd'), data_sigma_rmsssd, 'sigma')

    #####
    # CREATE STATISTICS RELATING SIGMA TO TIME
    #####
    data_sigma, keys_sigma = __group_by(data, keys, 'sigma')
    
    # modify time to state milliseconds
    for entry in data_sigma.itervalues():
        times = entry[keys_sigma.index('time')]
        for idx, time in enumerate(times):
            times[idx] = time[0] * 60 * 60 * 100 + time[1] * 60 * 100 + time[2] * 100 + time[3]
        entry[keys_sigma.index('time')] = times
        
    # save sigma to time relation
    data_image_time = {}
    for key in data_sigma.iterkeys():
        data_image_time[key] = __compute_boxplot(data_sigma[key][keys_sigma.index('time')])
    with open('{}_{}_{}.dat'.format(args.output, args.bterm, 'sigmatime'), 'w') as f:
        f.write('#sigma\tmean\tmedian\tlower_quartile\tupper_quartile\tmin\tmax\tlower_iqr\tupper_iqr\n')
        for sigma, values in data_image_time.iteritems():
            f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(sigma, *values))

    #####
    # CREATE STATISTICS GROUPED BY IMAGE
    #####
    data_image, keys_image = __group_by(data, keys, 'image')
    
    # statistics of best score that do not differ more than one percent
    data_image_1 = __select_best(data_image, keys_image, 'score', 1)
    for key in data_image_1.iterkeys():
        data_image_1[key] = __compute_boxplot(data_image_1[key][keys_image.index('score')])
    __write_file_boxplot('{}_{}_{}.dat'.format(args.output, args.bterm, '1p'), data_image_1, 'image')
    
    # statistics of best score that do not differ more than five percent
    data_image_5 = __select_best(data_image, keys_image, 'score', 5)
    for key in data_image_5.iterkeys():
        data_image_5[key] = __compute_boxplot(data_image_5[key][keys_image.index('score')])
    __write_file_boxplot('{}_{}_{}.dat'.format(args.output, args.bterm, '5p'), data_image_5, 'image')
    
    # statistics of best score that do not differ more than ten percent
    data_image_10 = __select_best(data_image, keys_image, 'score', 10)
    for key in data_image_10.iterkeys():
        data_image_10[key] = __compute_boxplot(data_image_10[key][keys_image.index('score')])
    __write_file_boxplot('{}_{}_{}.dat'.format(args.output, args.bterm, '10p'), data_image_10, 'image')

    
    
    ####
    # CREATE STATISTICS OF TIME AND MEMORY (grouped by image)
    ###
    data_image, keys_image = __group_by(data, keys, 'image')
    
    # parse image statistics file
    image_sizes = {}
    with open(args.statistics, 'r') as f:
        f.readline() # skip header
        for line in f.readlines():
            values = line.strip().split(';')
            image_sizes[int(values[0])] = values[9]
        
    # modify time to state milliseconds
    for entry in data_image.itervalues():
        times = entry[keys_image.index('time')]
        for idx, time in enumerate(times):
            times[idx] = time[0] * 60 * 60 * 100 + time[1] * 60 * 100 + time[2] * 100 + time[3]
        entry[keys_image.index('time')] = times
        
    # time + image size
    data_image_time = {}
    for key in data_image.iterkeys():
        data_image_time[key] = list(__compute_boxplot(data_image[key][keys_image.index('time')])) + [image_sizes[key]]
    with open('{}_{}_{}.dat'.format(args.output, args.bterm, 'timesize'), 'w') as f:
        f.write('#image\tmean\tmedian\tlower_quartile\tupper_quartile\tmin\tmax\tlower_iqr\tupper_iqr\tvoxels\n')
        for attribute, values in data_image_time.iteritems():
            f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(attribute, *values))
    
    # memory usage + image size
    data_image_memory = {}
    for key in data_image.iterkeys():
        data_image_memory[key] = list(__compute_boxplot(data_image[key][keys_image.index('max_memory')])) + [image_sizes[key]]
    with open('{}_{}_{}.dat'.format(args.output, args.bterm, 'memorysize'), 'w') as f:
        f.write('#image\tmean\tmedian\tlower_quartile\tupper_quartile\tmin\tmax\tlower_iqr\tupper_iqr\tvoxels\n')
        for attribute, values in data_image_memory.iteritems():
            f.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(attribute, *values))
    
    # memory usage + time
    data_image_timememory = {}
    for key in data_image.iterkeys(): # save mean and median only
        mean_time, median_time = list(__compute_boxplot(data_image[key][keys_image.index('time')]))[:2]
        mean_memory, median_memory = list(__compute_boxplot(data_image[key][keys_image.index('max_memory')]))[:2]
        data_image_timememory[key] = [mean_time, median_time, mean_memory, median_memory] 
    with open('{}_{}_{}.dat'.format(args.output, args.bterm, 'timememory'), 'w') as f:
        f.write('#image\ttime-mean\ttime-median\tmemory-mean\tmemory-mean\n')
        for attribute, values in data_image_timememory.iteritems():
            f.write('{}\t{}\t{}\t{}\t{}\n'.format(attribute, *values))




# helper functions
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
    parser.add_argument('bterm', help='The boundary term to filter from the results-file.')
    parser.add_argument('input', help='The results file produced by _run_eperiments.py.')
    parser.add_argument('statistics', help='The image statistics file kept with the image dataset.')
    parser.add_argument('output', help='The directory and base name of the output file.')
    return parser    

if __name__ == "__main__":
    main()
    