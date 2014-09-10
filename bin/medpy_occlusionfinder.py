#!/usr/bin/python

"""

"""

# build-in modules
import argparse
import logging
import sys
from scipy import ndimage
from copy import deepcopy

# third-party modules


# path changes

# own modules
from medpy.core import Logger
from medpy.io import load, save
from medpy.io.header import get_pixel_spacing
from medpy.utilities.argparseu import sequenceOfIntegersGe

from medpy.occlusion.filters import *

# information
__author__ = "Albrecht Kleinfeld"
__version__ = "r0.1.0, 2014-08-25"
__email__ = "albrecht.kleinfeld@gmx.de"
__status__ = ""
__description__ = """
                      
                  Copyright (C) 2014 Albrecht Kleinfeld
                  This program comes with ABSOLUTELY NO WARRANTY;  
                  """

# code
def main():
    parser = getParser()
    args = getArguments(parser)

    # prepare logger
    logger = Logger.getInstance()
    if args.debug: logger.setLevel(logging.DEBUG)
    elif args.verbose: logger.setLevel(logging.INFO)

    # load input image
    logger.info('Loading images and preparing data.')
    
    
    #change data type
    '''
    input: needs mra-data
    '''
    if args.dtype:
        mra, mra_h = load(args.mra)
        mra = numpy.asarray(mra, dtype = numpy.uint16)
        save(mra, args.out, mra_h, args.force)
        sys.exit()
    
    #mask segmentation with brain mask
    '''
    input: 
        msk: mask of the brain
        seg: initial segmentation of vessels
    '''   
    if args.mask:
        msk, msk_h = load(args.msk)
        seg, seg_h = load(args.seg)
        msk = msk.astype(numpy.bool)
        seg = seg.astype(numpy.bool)
        seg = seg * msk
        seg = ndimage.binary_fill_holes(seg)
        seg = seg.astype(numpy.uint16)
        save(seg, args.out, seg_h, args.force)
        logger.info('Successfully terminated.')
        sys.exit()
    
    #remove components smaller than
    '''
    input: 
        com: number of the minimum size of components
    '''
    if args.delete:
        comp = int(args.com) 
        cen, cen_h = load(args.cen)
        
        return_image = component_size_label(cen, numpy.ones((3,3,3)))
        return_image[return_image<comp] = 0
        return_image[return_image>0] = 1
        save(return_image, args.out, cen_h, args.force)
        sys.exit()
    
    #calculating the n largest components
    '''
    input: 
        com: the number of the largest components
        cen: originial centerline of the image
    '''
    if args.component:
        
        comp = int(args.com) 
        cen, cen_h = load(args.cen)
   
        return_image = largest_n_components(cen, comp)
  
        save(return_image, args.out, cen_h, args.force)
        sys.exit()       


    #remove short branches
    '''
    input:
        cen: centerline
        rem: alle branches of centerline smaller than rem are deleted
    '''        
    if args.remove:
        thin, thin_h = load(args.cen)
        rem = int(args.rem)
        thin = thin.astype(numpy.bool)
        vesselness, vesselness_h = load(args.ves)
        
        vorher = numpy.zeros(thin.shape)
        counter = 0
        
        while not (vorher==thin).all():
            counter = counter + 1
            print ' '
            print 'Counter WHILE-SCHLEIFE - Remove Algorithm: {}'.format(counter)
            
            
            vorher = deepcopy(thin)
            thin = remove_short_branch_vesselness(thin, vesselness, rem)

        thin = numpy.asarray(thin, dtype=numpy.bool)
   
        save(thin, args.out, thin_h, args.force)
        sys.exit()
        
                
    #gradient ect. testfunction, uses gauss filter
    '''
    input:
        cen: centerline
        ves: vesselness of the brain
        mra: tof-mra image of the brain
        com: length of branchend
    ''' 
    if args.gradient:
        thin, thin_h = load(args.cen)
        thin = thin.astype(numpy.bool)
        value, value_h = load(args.ves)
        mra, mra_h = load(args.mra)
        seg, seg_h = load(args.seg)
        msk, msk_h = load(args.msk)
        value = ndimage.gaussian_filter(value, sigma=0.7)
        
        laenge_des_branch = int(args.com) 
        
        branchp = list(tuple(args.branchp))
        
        
        print 'Vesselness: '
        bild=gradient_branch(thin, numpy.asarray(value,numpy.float32), laenge_des_branch, seg, msk, get_pixel_spacing(mra_h), branchp)
        #print 'MRA: '
        #gradient_branch(thin, numpy.asarray(mra,value.dtype), laenge_des_branch)
        save(bild, args.out, mra_h, args.force)
        sys.exit()

    #verlaengert die Centerline am Ende der Arme
    '''
    input:
        com: Anzahl der Verlaengerungspunkte 
    '''
        
    if args.longer:
        mra, mra_h = load(args.mra)
        thin, thin_h = load(args.cen)
        thin = thin.astype(numpy.bool)
        thin = thin.astype(numpy.uint32)
        vessel, vessel_h = load(args.ves)
          
        anzahl_der_verlaengerten_pixel = int(args.com)

        thin = branch_extension_initial(thin, vessel, anzahl_der_verlaengerten_pixel)
        
        save(thin, args.out, thin_h, args.force)

        sys.exit()
        
    #Fill gaps in Centerline
    '''
    input:
        cen: centerline (with removed components smaller than "com")
        ori_cen: original centerline
        ves: vesselness image of the brain
    return: largest component with filled gaps 
    '''
    ###TODO: anzahl der Verlaengerungsschritte uebergeben lassen?! Gibt die groesse des Wuerfels um das Ende der Centerline an
    if args.fillgaps:
        cen, cen_h = load(args.cen) 
        cen = cen.astype(numpy.bool)
        cen = cen.astype(numpy.uint32)
          
        ori_cen, ori_cen_h = load(args.ori_cen)
        ori_cen == numpy.asarray(ori_cen, numpy.bool)
        ori_cen = component_size_label(ori_cen, numpy.ones((3,3,3)))
        ori_cen[ori_cen<3] = 0
        ori_cen[ori_cen>0] = 1
        
        
        
        comp = int(args.com) 
        
        vessel, vessel_h = load(args.ves)

        #koennen die nasechsten drei Zeilen weg?!
        
        #labeled_cen = component_size_label(cen, numpy.ones((3,3,3)))
        #labeled_cen=cen

        
        anzahl_verlaengerungsschritte = 20
        
        
        out_cen = cen
                
        zwischenspeicher = numpy.zeros(out_cen.shape)
        counter=0
        
        while 1:
            counter=counter+1
            print 'Counter WHILE-SCHLEIFE: {}'.format(counter)
            print ' '
            
            out_cen_zuvor = deepcopy(out_cen)
            #labeled_cen = largest_connected_component(out_cen, numpy.ones((3,3,3)))
            
            cen = component_size_label(out_cen, numpy.ones((3,3,3)))
            cen[cen<comp] = 0
            cen[cen>0] = 1 
            
            
            
            out_cen, zwischenspeicher = close_gaps(cen, anzahl_verlaengerungsschritte,  get_pixel_spacing(cen_h), vessel, ori_cen, zwischenspeicher,ori_cen_h)
            ori_cen = out_cen
            if (out_cen==out_cen_zuvor).all():
                print 'gleich'
                break
        
        
            
        out_cen = component_size_label(out_cen, numpy.ones((3,3,3)))
        out_cen[out_cen<comp] = 0
        out_cen[out_cen>0] = 1      
        
        save(out_cen, args.out, cen_h, args.force)
        
        sys.exit()
        
        
        
    if args.losch:
        seg, seg_h = load(args.seg)
        seg = numpy.asarray(seg, dtype = numpy.bool)
        seg = numpy.asarray(seg, dtype = numpy.uint32)
        
        seg = count_neighbor( seg, numpy.ones((3,3,3)) )
        seg[seg<=12]=0
        seg = numpy.asarray(seg, dtype = numpy.bool)
        save(seg, args.out, seg_h, args.force)
        sys.exit()

def getArguments(parser):
    "Provides additional validation of the arguments collected by argparse."
    args = parser.parse_args()
    if args.longer and not args.cen and not args.ves:
        parser.error('needs a centerline and vesselnessvalues')
    
    return args

def getParser():
    "Creates and returns the argparse parser object."
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument('-mra', help='The original tof-mra image.')
    parser.add_argument('-msk', help='The brain mask.')
    parser.add_argument('-seg', help='The vessel segmentation.')
    parser.add_argument('-cen', help='The centerline.')
    parser.add_argument('-ves', help='The vesselness values.')
    parser.add_argument('-com', help='Number of the n largest component or minimal size of a components, which should be not deleted.')
    parser.add_argument('-rem', help='Minimal length of branches.')
    parser.add_argument('-ori_cen', help='original centerline')
    parser.add_argument('-out', help='The target file for the created output.')

    parser.add_argument('-branchp', type=sequenceOfIntegersGe, help='The occlusiontest, supplied as comma-separated coordinates e.g. x,y,z.')
    
    parser.add_argument('-t', dest='dtype', action='store_true', help='Control of data type - uint16')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Display more information.')
    parser.add_argument('-d', dest='debug', action='store_true', help='Display debug information.')
    parser.add_argument('-f', dest='force', action='store_true', help='Overide existing output images.')
    parser.add_argument('-m', dest='mask', action='store_true', help='Brain mask to the segmentation, to eliminate the bone')
    parser.add_argument('-g', dest='gradient', action='store_true', help='First calculates the largest connected Component - Calculates the gradient of last 5 points of each branch')
    parser.add_argument('-c', dest='component', action='store_true', help='searches the n largest component of segmentation or centerline.')
    parser.add_argument('-r', dest='remove', action='store_true', help='Remove branches shorter than -rem.')
    parser.add_argument('-x', dest='delete', action='store_true', help='Remove components shorter than -com.')
    parser.add_argument('-l', dest='longer', action='store_true', help='Finds next point of branchend.')
    
    parser.add_argument('-p', dest='losch', action='store_true', help='')
    
    parser.add_argument('-z', dest='fillgaps', action='store_true', help='Close gaps. -needs centerline')
    return parser    
    

    
if __name__ == "__main__":
    main()
