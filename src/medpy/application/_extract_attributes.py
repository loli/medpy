#!/usr/bin/python

import argparse
from nibabel.loadsave import load
import scipy.ndimage

def main():
    args = getArguments(getParser())
    
    # load images
    original = scipy.squeeze(load(args.original).get_data())
    mask = scipy.squeeze(load(args.mask).get_data()).astype(scipy.bool_)
    fg = scipy.squeeze(load(args.fg).get_data()).astype(scipy.bool_)
    bg = scipy.squeeze(load(args.bg).get_data()).astype(scipy.bool_)
    
    
    # collect marker voxels
    fg_voxels = original[fg]
    bg_voxels = original[bg]
    
    # collect real voxels
    real_voxels = original[mask]
    
    # collect boundary intensity differences
    mask_outer = scipy.ndimage.binary_dilation(mask)
    mask_inner = scipy.ndimage.binary_erosion(mask)
    label = scipy.zeros(original.shape, dtype=scipy.int_)
    mask_outer = mask_outer - mask
    mask_inner = mask - mask_inner
    label[mask_outer] = 1
    label[mask_inner] = 2
    boundary_intensities_dic = __boundary_statistics(label, original)
    
    # compute statistics
    fg_std = fg_voxels.std()
    bg_std = bg_voxels.std()
    real_std = real_voxels.std()
    fg_stats = __compute_boxplot(fg_voxels.tolist())
    bg_stats = __compute_boxplot(bg_voxels.tolist())
    real_stats = __compute_boxplot(real_voxels.tolist())
    boundary_stats = __compute_boxplot(boundary_intensities_dic[(1,2)])
    
    
    # calculate and print statistics
    header = '#file;'
    header += 'fg_std;fg_mean;fg_medium;fg_lower_q;fg_upper_q;fg_min;fg_max;fg_lower_ior;fg_upper_ior;'
    header += 'bg_std;bg_mean;bg_medium;bg_lower_q;bg_upper_q;bg_min;bg_max;bg_lower_ior;bg_upper_ior;'
    header += 'real_std;real_mean;real_medium;real_lower_q;real_upper_q;real_min;real_max;real_lower_ior;real_upper_ior;'
    header += 'boundary_mean;boundary_medium;boundary_lower_q;boundary_upper_q;boundary_min;boundary_max;boundary_lower_ior;boundary_upper_ior'
    line = '{};'.format(args.original)
    line += '{};'.format(fg_std)
    line += ';'.join(map(str, fg_stats)) + ';'
    line += '{};'.format(bg_std)
    line += ';'.join(map(str, bg_stats)) + ';'
    line += '{};'.format(real_std)
    line += ';'.join(map(str, real_stats)) + ';'
    line += ';'.join(map(str, boundary_stats))
    #print header
    print line
    
def __boundary_statistics(label_image, original_image):
    # convert to arrays if necessary
    label_image = scipy.asarray(label_image)
    gradient_image = scipy.asarray(original_image)
    
    if label_image.flags['F_CONTIGUOUS']: # strangely one this one is required to be ctype ordering
        label_image = scipy.ascontiguousarray(label_image)        
    
    def addition(key1, key2, v1, v2, dic):
        "Takes a key defined by two uints, two voxel intensities and a dict to which it adds g(v1, v2)."
        if not key1 == key2:
            key = (min(key1, key2), max(key1, key2))
            if not key == (1, 2): return
            dic[(1,2)].append(abs(v1 - v2))
                                                  
    # vectorize the function to achieve a speedup
    vaddition = scipy.vectorize(addition)
    
    # iterate over each dimension
    dic = {(1,2): []}
    for dim in range(label_image.ndim):
        slices_x = []
        slices_y = []
        for di in range(label_image.ndim):
            slices_x.append(slice(None, -1 if di == dim else None))
            slices_y.append(slice(1 if di == dim else None, None))
        vaddition(label_image[slices_x].flat,
                  label_image[slices_y].flat,
                  gradient_image[slices_x].flat,
                  gradient_image[slices_y].flat,
                  dic)

    return dic 

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
    parser = argparse.ArgumentParser(description="Temporary script for an experiment that can parse a certain time output file and an evaluation file to add them combined as a line to another file.")
    parser.add_argument('original')
    parser.add_argument('mask')
    parser.add_argument('fg')
    parser.add_argument('bg')
    return parser    

if __name__ == "__main__":
    main()
    