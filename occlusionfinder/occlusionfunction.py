'''
Created on Apr 8, 2014

@author: kleinfeld
'''

import numpy as np
from scipy.ndimage.measurements import label, histogram
from copy import deepcopy
from medpy.filter.image import sum_filter
from numpy.core.numeric import count_nonzero


def check_inside(image, point):
    #checks if point is in image
    for i in range(3):
        if( (point[i] < 0) | (point[i] >= image.shape[i]) ):
            return 0
    return 1

def number_of_neighbors(image, point, width):
#returns number of neighbors
    if not width:
        return 0
    else:
        counter = -1
        for i in range(-width, width+1):
            for j in range(-width, width+1):
                for k in range(-width, width+1):
                    if check_inside( image, [point[0]+i,point[1]+j,point[2]+k]):
                        if image[point[0]+i,point[1]+j,point[2]+k]:
                            counter = counter + 1
    return counter

def count_neighbor(image, structure):
    sumimage=sum_filter(image, footprint = structure, mode="constant", cval=0.0)
    return (sumimage * image) - image

#
def largest_connected_component(image, structure):
    'returns image with the largest connected components, labeled with 1'
    
    image, liste = label(image,structure)
    hist = histogram( image, 1, np.max(image), np.max(image) )
    
    return_image = deepcopy(image)
    return_image[ return_image >= 0 ] = 0
    
    return_image[ image == 1 + np.where( hist == hist.max() )[0][0] ] = 1
    
    return return_image
    
def return_neighbor(image, point, width):
#returns a list with points of surrounding, excluding the original point
    if not width:
        return 0
    else:
        liste = []
        for i in range(-width, width+1):
            for j in range(-width, width+1):
                for k in range(-width, width+1):
                    if check_inside( image, [point[0]+i,point[1]+j,point[2]+k]):
                        if image[point[0]+i,point[1]+j,point[2]+k]:
                            if not (i==0 and j==0 and k==0):
                                liste.append((point[0]+i,point[1]+j,point[2]+k))
    return liste

def component_size_label(image, structure):
#returns image where all connected binary objects (structure like in function label) are labeled with the size of its region
    '''
    structuring element is::

            [[1,1,1],
             [1,1,1],
             [1,1,1]]
        
    np.ones((3,3,3))
    '''

    '''
    TODO eventuell noch die einzelnen Values zurueckgeben???
    '''
    labeled_array, num_features = label(image,structure)
    temp = labeled_array.copy()
    counter=0
    print num_features
    for i in range(1,num_features+1):
        labeled_array[ np.nonzero( temp == i )] = ( np.count_nonzero( temp == i ))
        print counter
        counter=counter+1

    liste = []
    temp = deepcopy(labeled_array)
    while(np.max(temp)):
        liste.append(np.max(temp))
        temp[np.nonzero(temp == np.max(temp))]=0
    #hier noch nen sort(liste)  ???
    return labeled_array, liste

def search_branch(thinned_image, image_neighbor, list_point, next_point, max_branch_length):
    
    list_point.append(next_point)
        
    if(1 == max_branch_length):
        #wenn keine Schritte mehr, dann wird Suche beendet
        if(1 ==  image_neighbor[next_point]):
            list_point.pop(0)
            return list_point
        else:
            return
           
    else:
        if(2 ==  image_neighbor[next_point]):#wenn nur zwei nachbarn, dann ist alles gut und es geht los
        
            nachbarn = return_neighbor(thinned_image, next_point, 1)
            
            
            if(nachbarn[0] not in list_point):
                return search_branch(thinned_image, image_neighbor, list_point,nachbarn[0], max_branch_length-1)
                  
            elif(nachbarn[1] not in list_point):
                return search_branch(thinned_image, image_neighbor, list_point,nachbarn[1], max_branch_length-1)
            
            else:
                return
        
        elif(1 ==  image_neighbor[next_point]):
            list_point.pop(0)
            return list_point
        
        else:
            return
            
def return_short_branches(thinned_image, image_neighbor, branch_point, max_branch_length):
    '''
    returns a list including all relevant_branches, ausgehend vom Abzweigungspunkt
    '''
    next_neighbors = return_neighbor(thinned_image, branch_point, 1)
    return_list = []
    
    for next_point in range(0, len(next_neighbors)):
        
        temp_branch_points = [branch_point]
        temp_branch_points = search_branch(thinned_image, image_neighbor, temp_branch_points, next_neighbors[next_point], max_branch_length)        
        
        if temp_branch_points:
            return_list.append(temp_branch_points)
   
    return return_list

   
def remove_short_branch(thinned_image, branches_shorter_than):
   
    image_neighbor = count_neighbor( thinned_image, np.ones((3,3,3)) )

    branch_points = np.nonzero( image_neighbor >= 3 )
  
    for iterate_branches in range(0,np.size(branch_points,1)): #ueber alle kreuzungspunkte iterieren
        temp_branch_point = ( branch_points[0][iterate_branches] , branch_points[1][iterate_branches] , branch_points[2][iterate_branches])
        list_branch_points = return_short_branches( thinned_image , image_neighbor , temp_branch_point , branches_shorter_than )
        
        for number_of_branches in range(0, len( list_branch_points ) ): #Punkte loeschen
            for number_of_branchpoints in range(0, len( list_branch_points [ number_of_branches ] )):
                thinned_image[ list_branch_points [ number_of_branches ][ number_of_branchpoints ] ] = 0
                
    return thinned_image

def return_end_branches(thinned_image, image_neighbor, endpoint):
    '''
    benoetigt den Endpunkt eines Arterienarms und findet alle zugehoerigen Armpunkte bis zur Abzweigung
    '''
    liste = [endpoint]
    next_point = return_neighbor(thinned_image, endpoint, 1)
    
    while not(1 == number_of_neighbors(thinned_image, next_point[0], 1)):
        
        liste.append(next_point[0])
        
        if(2 == number_of_neighbors(thinned_image, next_point[0], 1)):
            next_point = return_neighbor(thinned_image, next_point[0], 1)
            
            if not(next_point[0] in liste):
                next_point = [next_point[0]]
            
            else:
                next_point = [next_point[1]]

        else:
            next_point = [endpoint] #hier wird eine Abbruchbedigung geschaffen
            
    return liste

def find_all_branches(thinned_image):
    '''
    findet alle Endzweige eines Arterienbaumes
    '''
    image_neighbor = count_neighbor(thinned_image, np.ones((3,3,3)))
    endpoints = np.nonzero(image_neighbor == 1)
    
    for iterate_endpoints in range(0,np.size(endpoints,1)): #ueber alle moeglichen Arterienendpunkte iterieren
        
        temp_endpoint = (endpoints[0][iterate_endpoints], endpoints[1][iterate_endpoints], endpoints[2][iterate_endpoints])
        list_branch_points = return_end_branches(thinned_image, image_neighbor, temp_endpoint)
        print list_branch_points
    return 0
#
def last_n_points_of_branch(thinned_image,branch_endpoint,length):
    'returns a list with the last points of a branch (maximal as long as length), needed input: thinned image and last branchpoint' 
    pointlist=[branch_endpoint]
    tmp_point=branch_endpoint
    
    for i in range(0,length-1):
        tmp_neighbor = return_neighbor(thinned_image, tmp_point, 1)
        if not 2 < tmp_neighbor.__len__():
            if tmp_neighbor[0] not in pointlist:
                pointlist.append(tmp_neighbor[0])
                tmp_point=tmp_neighbor[0]
            else:
                pointlist.append(tmp_neighbor[1])
                tmp_point=tmp_neighbor[1]
        else:
            return pointlist
    return pointlist
#
def return_value(listed_points, value_image):
    
    value_list = []
    for i in range(0,listed_points.__len__()):
        value_list.append(value_image[listed_points[i]])
    return value_list               
#
def last_points_mean_value(thinned_largest_component, vessel_value_image, number_of_points, minval, maxval):
    'returns an image, where all points of endbranches are labeled with a mean_value between minval and maxval'
    
    endpoints_of_branches = np.nonzero(1 == count_neighbor(thinned_largest_component,np.ones((3,3,3)))) #alle Endpunkte ermitteln
    
    return_image = deepcopy(thinned_largest_component)
    return_image[return_image != 0] = 0 #bildkopie mit werten ueberall 0, geht vielleicht besser ?!?!
    
    for tmp in range(0,np.size(endpoints_of_branches[0])):
        point = (endpoints_of_branches[0][tmp],endpoints_of_branches[1][tmp],endpoints_of_branches[2][tmp])
        liste_branchend = last_n_points_of_branch(thinned_largest_component, point, number_of_points)
        branch_values = return_value(liste_branchend,vessel_value_image)

        if minval <= np.mean(branch_values) <= maxval:
            print liste_branchend
            print np.mean(branch_values)
            
            for voxi in range(0,branch_values.__len__()):
                return_image[liste_branchend[voxi][0]][liste_branchend[voxi][1]][liste_branchend[voxi][2]] = 1

    return return_image

def gradient_branch(thinned_largest_component, vessel_value_image, number_of_points):
    'returns an image, where all points of endbranches are labeled with a mean_value between minval and maxval'
    
    endpoints_of_branches = np.nonzero(1 == count_neighbor(thinned_largest_component,np.ones((3,3,3)))) #alle Endpunkte ermitteln
    
    return_image = deepcopy(thinned_largest_component)
    return_image[return_image != 0] = 0 #bildkopie mit werten ueberall 0, geht vielleicht besser ?!?!
    
    for tmp in range(0,np.size(endpoints_of_branches[0])):
        point = (endpoints_of_branches[0][tmp],endpoints_of_branches[1][tmp],endpoints_of_branches[2][tmp])
        liste_branchend = last_n_points_of_branch(thinned_largest_component, point, number_of_points)
        branch_values = return_value(liste_branchend,vessel_value_image)
        print 'Points: {}'.format(liste_branchend)
        print 'Values: {}'.format(branch_values)
        branch_values = np.asarray(branch_values)
        gra = np.diff(branch_values)
        print 'Gradient: {}'.format(gra)
        gra = np.abs(gra)
        print 'Absolut Gradient: {}'.format(gra)
        print 'Mean Gradient: {}'.format(np.mean(gra))
        print ''
         