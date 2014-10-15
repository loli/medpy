'''
Created on Apr 8, 2014

@author: kleinfeld
'''
from medpy.io import load, save, header

import numpy as np
import os

from genericpath import getsize
from numpy.core.fromnumeric import shape

from occlusionfinder.occlusionfunction import remove_short_branch, find_all_branches, count_neighbor, \
return_neighbor, last_n_points_of_branch, return_value, last_points_mean_value

import occlusionfinder.occlusionfunction as ocf

from medpy.filter import binary
import medpy.filter
from copy import deepcopy


from scipy.ndimage.measurements import label
import scipy.ndimage as ndimage
from numpy.core.numeric import count_nonzero
from mx.Tools.Tools import nonzero

from medpy.filter.image import sum_filter
from medpy.filter.binary import largest_connected_component
import occlusionfinder
from occlusionfinder import occlusionfunction


def main():
    '''
    # WICHTIGE FUNKTION:
   
    #Loecher in der Segmentierung vor dem Thinning fuellen
    image2 = ndimage.binary_fill_holes(image)
    
    #Groesste Komponente finden
    image = binary.largest_connected_component()
   
    #Alle kleiner als ein bestimmter Threshhold werden geloescht??? (mal testen)
    image = binary.size_threshold()
    '''
    # size_label
    '''
    image, header = load('/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Test/Thinning_filled.nii.gz')

    a,b = setGraph.size_label(image, np.ones((3,3,3)))
    print b
    
    save(a,'/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Test/Thinning_filled_sizelabel.nii.gz', header)
        '''
    # zaehlen aller Endpunkte
    '''
    image, header = load('/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Test/Thinning_filled_largestComponent.nii.gz')
    
    bild=sum_filter(image,footprint=np.ones((3,3,3)),mode="constant", cval=0.0)
    
    bild = (bild * image) - image # "-image" damit wirklich nur die nachbarn gezaehlt werden


    save(bild,'/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Test/test_labled_nach_anzahl_nachbarn.nii.gz',header)
    '''
    # Datentypen aendern von TOF Bildern
    '''
    bild, h = load('/home/kleinfeld/DataBert2Kleinfeld/Results/CaseTest03/tof_tra_mra.nii.gz')

    np.array(bild1,dtype=np.uint16)
    
    save(np.array(bild,dtype=np.uint16),'/home/kleinfeld/DataBert2Kleinfeld/Results/haha.nii.gz',h)
    '''

    #TEST fuer diverse funktionen
    '''
    image, header = load('/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Test/test_thinned_removed_branches5.nii.gz')
    maske = image>0
    image[maske]=1   
    #print np.count_nonzero(image)
    #remove_short_branch(image, 5)
    #print np.count_nonzero(image)
    #find_all_branches(image)
    '''

    #largestComponent, h1=load('/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Test/Thinning_filled_largestComponent.nii.gz')
    #vessel_values, hvalue = load('/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/SigmaTest/sigma2varianz2/Vout30001normalVar2.nii.gz')

    
    
    #save(bild,'/home/kleinfeld/DataBert2Kleinfeld/Results/voxi.nii.gz')
    
    '''
    image_neigh = occlusionfunction.count_neighbor(bild1,np.ones((3,3,3)))
    mask = image_neigh==1
    endpoints_image = np.nonzero(mask)
    
    
    bild = deepcopy(bild1)
    maskierung = bild>=0
    bild[maskierung]=0
    print np.max(bild)
    tmp=0
    for tmp in range(0,np.size(endpoints_image[0])):
        b = (endpoints_image[0][tmp],endpoints_image[1][tmp],endpoints_image[2][tmp])
        liste_branchend = occlusionfunction.last_n_points_of_branch(bild1, b, 5)
        branch_values = occlusionfunction.return_value(liste_branchend,vessel_values)
                      
        if 10<np.mean(branch_values)<20:
            print liste_branchend
            print np.mean(branch_values)
            
            for voxi in range(0,branch_values.__len__()):
                bild[liste_branchend[voxi][0]][liste_branchend[voxi][1]][liste_branchend[voxi][2]]=2000
    '''                  
    
    
    '''
    image2,liste = ocf.component_size_label(seg,np.ones((3,3,3)))
    maxvalue = np.max(image2)
    mask = image2 < maxvalue
    image2[mask]=0
    '''
    seg, thinH = load('/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Phantomtest30001/Segmentation/thinned_segmentation.nii.gz')
    
    thinned, thinH = load('/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Phantomtest30001/Segmentation/thinned_largest_component.nii.gz')
    vessel, vesselH = load('/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Phantomtest30001/Segmentation/vesselnessPhantom.nii.gz')
    originalBild, oriH = load('/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Phantomtest30001/phantomtestint.nii.gz')
    
        
    #seg = ocf.largest_connected_component(seg, np.ones((3,3,3)))

    #temp = ocf.last_points_mean_value(thinned, vessel_value_image = vessel, number_of_points = 5, minval = 30 , maxval = 50)
    temp = ocf.gradient_branch(thinned, vessel_value_image = vessel, number_of_points = 5)
    print np.count_nonzero(temp)


    '''
    bild=ocf.remove_short_branch(thinned, branches_shorter_than = 7)
    
    temp=ocf.last_points_mean_value(bild, vessel_value_image = vessel, number_of_points = 5, minval = 30 , maxval = 50)
    
    print np.count_nonzero(temp)
    '''
    
    '''
    listed_points1 = [(127, 286, 85), (127, 285, 85), (128, 284, 86), (128, 283, 86), (129, 282, 86)]
    print ocf.return_value(listed_points1, value_image=originalBild)
    
    
    listed_points2 = [(282, 181, 53), (282, 182, 53), (282, 183, 53), (282, 184, 54), (281, 185, 54)]
    print ocf.return_value(listed_points2, value_image=originalBild)
    
    
    
    print ''
    print ocf.return_value(listed_points1, value_image=vessel)
    print ocf.return_value(listed_points2, value_image=vessel)
    #save(image2,'/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Phantomtest30001/Segmentation/thinned_largest_removed5.nii.gz', thinH)
    '''
    
    
    #thinned, thinH = load('/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Phantomtest30001/Segmentation/thinned_largest_component.nii.gz')
    #vessel, vesselH = load('/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Phantomtest30001/Segmentation/vesselnessPhantom.nii.gz')
    #remo5 , remoH = load('/home/kleinfeld/DataBert2Kleinfeld/Results/Vesselness31/Phantomtest30001/Segmentation/thinned_removed_short_branches.nii.gz')

    #maskeee = ocf.last_points_mean_value(remo5, vessel, number_of_points=6, minval=30, maxval=40)


if __name__ == "__main__":
    main()



