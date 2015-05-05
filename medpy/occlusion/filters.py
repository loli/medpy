'''
Created on Aug 25, 2014
@package medpy.occlusion.filters

@author: kleinfeld

@version 0.2.1
@since 2014-08-25
@status
'''


# build-in modules
from scipy.ndimage.morphology import binary_dilation

# third-party modules
import numpy
import multiprocessing

# own modules
from medpy.filter.image import sum_filter

# code

def occlusion_detection(vesselness, centerline, segmentation, voxelspacing, logger):
    "Searches potential occlusions in MRA-data by using four different criteria"
    
    # image with marked occlusions
    image_occlusion = numpy.zeros(centerline.shape)
    # list of all vesselness-values along the 'inner' centerline of all branches
    all_values_inside_vessel = []
    # list of all maximum gradients along the extended centerline
    all_max_gradients = []
    # list of all endpoints
    list_tmp_point = []
    # list of 'inner' and 'outer' vesselness-values
    list_inside_branch_point = []
    list_inside_branch_values = []
    list_outside_branch_point = []
    list_outside_branch_values = []
    # dictionairy for all inner branchpoints
    dict_of_inner_branch_points = {}

    endpoints_of_branches = numpy.nonzero(1 == count_neighbor(centerline , numpy.ones((3, 3, 3))))
    endpoints_of_branches = zip(endpoints_of_branches[0], endpoints_of_branches[1], endpoints_of_branches[2])
    logger.info(('To be checked number of branches: {}').format(len(endpoints_of_branches)))

    try:
        cpus = multiprocessing.cpu_count()
    except NotImplementedError:
        cpus = 2
    cpus = min(cpus, 8)
    
    lock = multiprocessing.Lock()
    queue = multiprocessing.Queue()
    
    queue2 = multiprocessing.Queue()
    queue2.put(endpoints_of_branches)
  
    process_store = []
    for i in range(cpus):
        p = multiprocessing.Process(target=occlusion_calc_process, args=(centerline, vesselness, lock, queue, queue2))
        p.start()
        process_store.append(p)
    
    '''
    while not 1 == sum(item.is_alive() for item in process_store):
        True
    ''' 

    for i in range(cpus):
        list_inside_branch_point += queue.get()
        list_inside_branch_values += queue.get()
        all_values_inside_vessel += queue.get()
        all_max_gradients += queue.get()
        list_outside_branch_point += queue.get()
        list_outside_branch_values += queue.get()
        list_tmp_point += queue.get()
        dict_of_inner_branch_points.update(queue.get())

    # calculating some thresholds     
    mean_all_values = numpy.mean(all_values_inside_vessel)   
    mean_gra = numpy.mean(all_max_gradients)
    # dictionary with all values inside branch
    dict_inside_values = dict(zip(list_inside_branch_point, list_inside_branch_values))
    # dictionary with all values outside branch
    dict_outside_values = dict(zip(list_outside_branch_point, list_outside_branch_values))
    # dictionary with all maximum gradients
    dict_max_gra = dict(zip(list_tmp_point, all_max_gradients))
     
    for tmp2 in range(len(endpoints_of_branches)):  

        tmp_point = endpoints_of_branches[tmp2]
        # check if tmp_point exists in all dictionaries
        if tmp_point in dict_inside_values \
            and tmp_point in dict_outside_values \
            and tmp_point in dict_max_gra:
            
            insidevalues = dict_inside_values[ tmp_point ]
            outsidevalues = dict_outside_values[ tmp_point ]
            tmp_max_gra = dict_max_gra[ tmp_point ]
        else:
            continue

        branch_points = dict_of_inner_branch_points[ tmp_point ]
        vesselthickness = 0.0

        if len(branch_points) >= 2:
            for index in range(0, len(branch_points) - 1):
                vesselthickness += thickness_of_segmentation(branch_points[ index + 1 ], branch_points[ index ], segmentation, 2) 
        else:
            continue     
        
        if len(branch_points) - 1:
            vesselthickness = vesselthickness / (len(branch_points) - 1)
        else:
            continue

        if numpy.median(outsidevalues) <= numpy.median(insidevalues) * 0.3 \
            and mean_all_values <= numpy.mean(insidevalues) \
            and tmp_max_gra >= mean_gra:
      
            if vesselthickness < 4.0:
                continue
       
            # marking the potential occlusion
            for point in dict_of_inner_branch_points[ tmp_point ]:
                image_occlusion[point[0]][point[1]][point[2]] = 1
    
    image_occlusion = binary_dilation(image_occlusion, iterations=5, mask=segmentation)
    return image_occlusion

def occlusion_calc_process(centerline, vesselness, lock, queue, queue2):
    
    number_of_points = 10

    list_inside_branch_point = []
    list_inside_branch_values = []
    all_values_inside_vessel = []
    all_max_gradients = []
    list_outside_branch_point = []
    list_outside_branch_values = []
    list_tmp_point = []
    dict_of_inner_branch_points = {}
    
    switch = 1
    
    while switch:
    
        lock.acquire()
        endpoints_of_branches = queue2.get()

        if endpoints_of_branches:
            
            tmp_point = endpoints_of_branches[0]
            endpoints_of_branches.remove(tmp_point)
            queue2.put(endpoints_of_branches)
            lock.release()
             
            # calculating vesselness-values along a branch
            tmp_image = numpy.zeros(centerline.shape)
            tmp_compare_image = numpy.zeros(centerline.shape)
            tmp_image[ tmp_point[0], tmp_point[1], tmp_point[2] ] = 1
    
            while (number_of_points > numpy.count_nonzero(tmp_image) and not (tmp_compare_image == tmp_image).all()):
                tmp_compare_image = tmp_image
                tmp_image = binary_dilation(tmp_image, structure=numpy.ones((3, 3, 3)), iterations=1, mask=centerline)
                 
            tmp_branch_values = (vesselness[ numpy.nonzero(tmp_image) ])
            list_inside_branch_point.append(tmp_point)
            list_inside_branch_values.append(tmp_branch_values) 
            all_values_inside_vessel.extend(tmp_branch_values) 
     
            # calculating extension of branch
            list_of_branch_points = give_branch_points(centerline, tmp_point, number_of_points) 
            dict_of_inner_branch_points.update({ tmp_point : list_of_branch_points })
            list_of_branch_points = list_of_branch_points.tolist()
            length_befor_extension = len(list_of_branch_points)
            thin_for_extension = numpy.copy(centerline)
    
            
            if 2 <= length_befor_extension:
                
                tmp_second_point = list_of_branch_points[1]
                for i in range(0, 2 * number_of_points):
                    
                    if not check_border(centerline, list_of_branch_points[0]):
                        break
                  
                    next_point = give_branch_extension(thin_for_extension, vesselness, list_of_branch_points, tmp_second_point)
                    
                    if (next_point == 0):
                        break
    
                    thin_for_extension[next_point[0]][next_point[1]][next_point[2]] = 1
                    list_of_branch_points.insert(0, next_point)
            else:
                break
    
            # calculating the outer values of branch
            tmp_memory = []
            
            if 0 < len(list_of_branch_points) - length_befor_extension:
                list_outside_branch_point.append(tmp_point)
                branch_values = return_value(list_of_branch_points, vesselness)
                tmp_memory = branch_values[ 0 : len(list_of_branch_points) - length_befor_extension ]
                list_outside_branch_values.append(tmp_memory)
                
                # calculating the maximum gradient
                gra = numpy.diff(branch_values)
                all_max_gradients.append(max(gra))
                list_tmp_point.append(tmp_point)
        else:        
            
            queue.put(list_inside_branch_point)
            queue.put(list_inside_branch_values)
            queue.put(all_values_inside_vessel)
            queue.put(all_max_gradients)
            queue.put(list_outside_branch_point)
            queue.put(list_outside_branch_values)
            queue.put(list_tmp_point)
            queue.put(dict_of_inner_branch_points)

            queue2.put(endpoints_of_branches) 
            
            lock.release()
            switch = 0

def count_neighbor(image, structure):
    'returns image, where the current value of the voxel is the number of its neighbors'
    image = image.astype(numpy.bool)
    sumimage = sum_filter(image, footprint=structure, mode="constant", cval=0.0, output=numpy.uint)
    sumimage[~image] = 0
    return sumimage - image

def give_branch_points(thinned_image, branch_endpoint, length):
    'returns a list with the last points of a branch (maximal as long as length, inclusive intersection point), needed input: thinned image and last point of current branch' 
    pointlist = [branch_endpoint]
    tmp_point = branch_endpoint
    
    for i in range(length - 1):
        tmp_neighbor = return_neighbor(thinned_image, tmp_point)
        if 2 == len(tmp_neighbor) or 1 == len(tmp_neighbor):
            if tmp_neighbor[0] not in pointlist:
                pointlist.append(tmp_neighbor[0])
                tmp_point = tmp_neighbor[0]
            elif 1 < tmp_neighbor.__len__():
                pointlist.append(tmp_neighbor[1])
                tmp_point = tmp_neighbor[1]
            else:
                return numpy.asarray(pointlist)
        else:
            return numpy.asarray(pointlist)

    return numpy.asarray(pointlist)

def return_neighbor(image, point):
    'returns a list with surrounding points of input-point'
    slicers = [ slice(max(p, 1) - 1, p + 2) for p in point ]
    tmp_image = numpy.zeros(image.shape)
    tmp_image[ slicers ] = 1
    tmp_image[ point[0], point[1], point[2]] = 0
    tmp_points = numpy.nonzero(image * tmp_image) 

    return zip(tmp_points[0], tmp_points[1], tmp_points[2])

def check_border(image, point):
    'checks if there is enough space to the border of the image'
    if numpy.min(point) <= 4 or point[0] >= image.shape[0] - 5 or point[1] >= image.shape[1] - 5 or point[2] >= image.shape[2] - 5 :
        return False
    else:
        return True

def return_value(listed_points, value_image):
    'returns all values of image along the listed points'
    value_list = []
    for i in range(len(listed_points)):
        point = listed_points[i]
        value_list.append((value_image[ point[0] ][ point[1] ][ point[2] ]))
    return value_list  

def calc_direction(point1, point2):
    'calculates the direction between the given points, returns a vector'
    point1 = numpy.asarray(point1)
    point2 = numpy.asarray(point2)
    return point2 - point1 

def thickness_of_segmentation(point1, point2, segmentation, iterations):
    'approximates the thickness of the segmentation'
    vector = numpy.array(point2) - numpy.array(point1)
    
    # calculating perpendicular vectors
    perp_vector = []
    if not (numpy.asarray(numpy.cross(vector, [1, 0, 0])) == [0, 0, 0]).all():
        perp_vector.append(numpy.cross(vector, [1, 0, 0]))
        perp_vector.append(numpy.cross([1, 0, 0], vector))
    
    elif not (numpy.asarray(numpy.cross(vector, [0, 1, 0])) == [0, 0, 0]).all():
        perp_vector.append(numpy.cross(vector, [0, 1, 0]))
        perp_vector.append(numpy.cross([0, 1, 0], vector))
    
    else:
        perp_vector.append(numpy.cross(vector, [0, 0, 1]))
        perp_vector.append(numpy.cross([0, 0, 1], vector))
    
    perp_vector.append(numpy.cross(vector, perp_vector[0]))
    perp_vector.append(numpy.cross(perp_vector[0], vector))
    
    counter = 0
    for itera in range(1, iterations + 1):
        for i in perp_vector:
            point = point1 + (i * itera)
            if check_inside(segmentation, point) and segmentation[point[0]][point[1]][point[2]]:
                counter += 1

    return counter

def check_inside(image, point):
    'checks if point is in image'
    for i in range(3):
        if((point[i] < 0) | (point[i] >= image.shape[i])):
            return 0
    return 1

def number_of_neighbors(image, point):
    
    slicers = [ slice(max(p, 1) - 1, p + 2) for p in point ]
    tmp_image = numpy.zeros(image.shape)
    tmp_image[ slicers ] = 1
    tmp_image[ point[0], point[1], point[2]] = 0
    return numpy.count_nonzero(image * tmp_image) 
 
def calc_angle(vector1, vector2):
    'calculates the angle between two vectors'
    x_mod = numpy.sqrt((vector1 * vector1).sum())
    y_mod = numpy.sqrt((vector2 * vector2).sum())
    
    cos_angle = numpy.dot(vector1, vector2) / x_mod / y_mod 
    
    if cos_angle > 1:
        cos_angle = 1
    if cos_angle < -1:
        cos_angle = -1
    
    angle = numpy.arccos(cos_angle) 

    return angle * 360 / 2 / numpy.pi

def check_if_neigbor(point1, point2):
    'checks if two points are neigbors'
    max_value = numpy.max([point1[0] - point2[0], point1[1] - point2[1] , point1[2] - point2[2]])
    min_value = numpy.min([point1[0] - point2[0], point1[1] - point2[1] , point1[2] - point2[2]]) 
    
    if max_value >= 2 or min_value <= -2:
        return False
    else:
        return True
      
def give_branch_extension(skeleton, vesselness, list_of_branch_points, tmp_point):
    'gives the next point of a extended branch'
    tmp_point = [tmp_point[0], tmp_point[1], tmp_point[2]]
    last_point = list_of_branch_points[ 0 ] 
    initial_direction = calc_direction(tmp_point, last_point) 
   
    slicers = [ slice(max(p, 1) - 1, p + 2) for p in last_point ]
    tmp_image = numpy.zeros(skeleton.shape)
    tmp_image[ slicers ] = 1
    tmp_image[ last_point[0], last_point[1], last_point[2] ] = 0     
    tmp_vesselness = vesselness * tmp_image

    while numpy.max(tmp_vesselness):        
          
        potential_point = numpy.nonzero(numpy.max(tmp_vesselness) == tmp_vesselness)
        potential_point = [potential_point[0][0], potential_point[1][0], potential_point[2][0]]

        if 60 >= calc_angle(initial_direction, calc_direction(last_point, potential_point)) \
            and number_of_neighbors(skeleton, potential_point) <= 1 \
            and not check_if_neigbor(potential_point, list_of_branch_points[ 1 ]):

                return potential_point   
        
        else:
            tmp_vesselness[ potential_point[0], potential_point[1], potential_point[2] ] = 0
   
    return 0


def remove_short_branches( centerline, vesselness, minimal_branch_length, logger):
   

    enhanced_centerline = numpy.copy( centerline )
        
    image_neighbor = count_neighbor( centerline, numpy.ones((3,3,3)) )

    intersection_points = numpy.nonzero( 3 <= image_neighbor ) 
    intersection_points = zip(intersection_points[0], intersection_points[1], intersection_points[2])
    logger.info(('To be checked number of intersection_points: {}').format(len(intersection_points)))

    try:
        cpus = multiprocessing.cpu_count()
    except NotImplementedError:
        cpus = 2
    cpus = min(cpus, 8) - 1
    
    lock = multiprocessing.Lock()
    
    queue = multiprocessing.Queue()  
    queue.put(enhanced_centerline)
    
    queue2 = multiprocessing.Queue()
    queue2.put(intersection_points)
      
    process_store = []
    for i in range(cpus):
        p = multiprocessing.Process(target=process_remove_short_branch, args=( centerline, vesselness, image_neighbor, minimal_branch_length, lock, queue, queue2 ))
        p.start()
        process_store.append(p)
        


    while not 1 == sum(item.is_alive() for item in process_store):
        True

    
    enhanced_centerline = queue.get()
    return enhanced_centerline
        
        
def process_remove_short_branch( centerline, vesselness, image_neighbor, minimal_branch_length, lock, queue, queue2 ):
        
        
    switch = 1
    
    while switch:
    
        lock.acquire()
        intersection_points = queue2.get()
        print len(intersection_points)
        
        if intersection_points:
            
            tmp_intersection = intersection_points[0]
            intersection_points.remove( tmp_intersection )
            queue2.put( intersection_points )
            lock.release()
    
            list_short_branches = give_short_surrounding_branches( centerline, image_neighbor, tmp_intersection, 10 )

            for iterator in range( len( list_short_branches ) ):
            
                if len( list_short_branches [ iterator ]) <= minimal_branch_length:
                    print 'remove'
                    lock.acquire()
                    enhanced_centerline = queue.get()
                    
                    for tmp_nbr in range( len( list_short_branches [ iterator ] )):
                        enhanced_centerline[ list_short_branches [ iterator ][ tmp_nbr ] ] = 0
                    
                    queue.put(enhanced_centerline) 
                    lock.release()
                    
                #sonst ueberpruefe die Vesselness vom Seitenarme und den anderen Armen, die vom gleichen Kreuzungspunkt ausgehen
                '''
                else:
                    #Bestimmen der Durchschnittsvesselness der letzten 3 Punkte
                    vesselvalue1 = []
                    for index in range(-3,0):
                        vesselvalue1.append(vesselness[ gelistete_seitenarme [ temp_seitenarme ][ index ] ])
                    #Durchschnittliche Vesselness der letzten drei Astpunkte des zu ueberpruefenden Seitenarmes
                    vesselvalue1 = numpy.mean(vesselvalue1) 
                                   
                    
                    zu_delitieren = numpy.zeros(thinned_image.shape)
                    zu_delitieren[temp_kreuzungspunkt[0]][temp_kreuzungspunkt[1]][temp_kreuzungspunkt[2]]=1
                    
                    zu_delitieren = binary_dilation(zu_delitieren, structure=numpy.ones((3,3,3)), iterations=5, mask=thinned_image,)
                    
                    for index4 in range(0, len( gelistete_seitenarme [ temp_seitenarme ] )):
                        zu_delitieren[ gelistete_seitenarme [ temp_seitenarme ][ index4 ] ] = 0
                    
                    values=zu_delitieren*vesselness
    
                    vesselvalue2 = 0
                    if not 0 == numpy.count_nonzero(values):
                        vesselvalue2 = sum(sum(sum(values)))/numpy.count_nonzero(values)
    
                    if ((not vesselvalue2 == 0) and (vesselvalue2*(0.3) >= vesselvalue1)):
                        #print 'ES WIRD GELOESCHTTTTTT'
                        #print list_branch_points [ number_of_branches ]
                        unter10=unter10+1
                        
                        for number_of_branchpoints in range(0, len( gelistete_seitenarme [ temp_seitenarme ] )):
                            thinned_image2[ gelistete_seitenarme [ temp_seitenarme ][ number_of_branchpoints ] ] = 0
                 '''   
        else:        
            queue2.put(intersection_points) 
            
            lock.release()
            switch = 0
    
def give_short_surrounding_branches(centerline, image_neighbor, tmp_intersection, max_branch_length):
    'returns a list with all branches ensuing from the temporary intersectionpoint of the centerline, which are shorter than max_branch_length'
    list_surrounding_neighbors = return_neighbor(centerline, tmp_intersection)
    return_list = []
    
    for iterator in range(len(list_surrounding_neighbors)):
        
        tmp_branch_points = [tmp_intersection]
        tmp_branch_points = search_branch( centerline, image_neighbor, tmp_branch_points, list_surrounding_neighbors[iterator], max_branch_length)        
        
        if tmp_branch_points:
            return_list.append(tmp_branch_points)
   
    return return_list
    
def search_branch( centerline, image_neighbor, list_point, next_point, max_branch_length):
    'returns a list with all branch_points if the length of the branch is shorter than max_branch_length'
    list_point.append(next_point)
        
    if(1 == max_branch_length):
        
        if(1 ==  image_neighbor[next_point]):
            list_point.pop(0)
            return list_point
        else:
            return
           
    else:
        if(2 ==  image_neighbor[next_point]):
        
            nachbarn = return_neighbor(centerline, next_point)
            
            
            if(nachbarn[0] not in list_point):
                return search_branch(centerline, image_neighbor, list_point,nachbarn[0], max_branch_length-1)
                  
            elif(nachbarn[1] not in list_point):
                return search_branch(centerline, image_neighbor, list_point,nachbarn[1], max_branch_length-1)
            
            else:
                return
        
        elif(1 ==  image_neighbor[next_point]):
            list_point.pop(0)
            return list_point
        
        else:
            return
    
    
    
    
    
    
    
    
    











from scipy.ndimage.measurements import label, histogram

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
        labeled_array[ numpy.nonzero( temp == i )] = ( numpy.count_nonzero( temp == i ))
        print counter
        counter=counter+1

    liste = []
    temp = numpy.copy(labeled_array)
    while(numpy.max(temp)):
        liste.append(numpy.max(temp))
        temp[numpy.nonzero(temp == numpy.max(temp))]=0
    #hier noch nen sort(liste)  ???
    return labeled_array, liste
    
    
    
    
    
    
    
    
    
    
    