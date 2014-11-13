#!/usr/bin/python

# build-in modules
import logging

# third-party modules
import scipy
from medpy import filter
from nibabel.loadsave import load, save
from medpy.core import Logger
from medpy.utilities.nibabel import image_like
from medpy.features.texture import running_total, tamura

# path changes

# own modules

# code
def main():
    # prepare logger
    a = [[[1,2,3,4,5],
          [1,2,3,4,5],
          [1,2,3,4,5],
          [1,2,3,4,5]],
         [[1,2,3,4,5],
          [1,2,3,4,5],
          [1,2,3,4,5],
          [1,2,3,4,5]],
         [[1,2,3,4,5],
          [1,2,3,4,5],
          [1,2,3,4,5],
          [1,2,3,4,5]]]
    
    b = [[[1,2,3,4,3],
          [3,1,2,1,4],
          [3,1,4,2,2],
          [2,2,1,3,3],
          [4,3,1,2,1]]]
    
    c = [[[1,2,3,4],
          [5,6,7,8],
          [9,1,2,3]],
         [[4,5,6,7],
          [8,9,1,2],
          [3,4,5,6]]]
    
    a = scipy.asarray(a)
    b = scipy.asarray(b)
    c = scipy.asarray(c)
    
    original_image_n = '/home/omaier/Experiments/Regionsegmentation/Evaluation_Viscous/00originalvolumes/o09.nii'
    original_image = load(original_image_n)
    original_image_d = scipy.squeeze(original_image.get_data())
    
    original_image_d = original_image_d[0:50, 0:50, 0:50]
    
    dir = scipy.zeros(original_image_d.shape).ravel()
    oir = original_image_d.ravel()
    for i in range(len(dir)):
        dir[i] = oir[i]
    dir = dir.reshape(original_image_d.shape)
    
    coa, con, dir = tamura(dir, 5)
    
    for i in range(5):
        print("k=", i+1, " with ", len((coa == i).nonzero()[0]))
    
if __name__ == "__main__":
    main()       