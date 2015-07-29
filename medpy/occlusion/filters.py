'''
Created on July 27, 2015
@package medpy.occlusion.filters

@author: kleinfeld

@version 1.0.0
@since 2015-07-27
@status
'''


# build-in modules
from scipy.ndimage.morphology import binary_dilation
from scipy.ndimage.measurements import label

# third-party modules
import numpy
import multiprocessing

# own modules
from medpy.filter.image import sum_filter

# code

def gap_closing(vesselness, centerline, original_centerline, voxelspacing, logger):
    'Closes gaps in 3D-skeleton data by using the vesselnessimage'
    
    region_size = 20
    tmp_comp_image = numpy.zeros(centerline.shape, numpy.bool)
    switch = 1
    
    #preparing multiprocessing
    try:
        cpus = multiprocessing.cpu_count()
    except NotImplementedError:
        cpus = 2
    cpus = min(cpus, 8)

    lock = multiprocessing.Lock()
  
    
    while switch:
        
        message_queue = multiprocessing.Queue()
        result01_queue = multiprocessing.Queue()
        result02_queue = multiprocessing.Queue()
        
        tmp_fill_image = numpy.zeros(centerline.shape, numpy.bool)
        result01_queue.put( tmp_fill_image )
     
        tmp_out_cen = centerline.copy()
        
        endpoints_of_branches = numpy.nonzero(1 == count_neighbor(centerline , numpy.ones((3, 3, 3))))
        endpoints_of_branches = zip( endpoints_of_branches[0], endpoints_of_branches[1], endpoints_of_branches[2] )
            
        point_queue = multiprocessing.Queue()
        for point in endpoints_of_branches:
            point_queue.put(point)
                
        process_store = []
        for _ in range(cpus):
            p = multiprocessing.Process( target = gap_closing_process, args=(vesselness, centerline, region_size,  voxelspacing, original_centerline, tmp_comp_image, lock, point_queue, result01_queue, result02_queue, message_queue))
            process_store.append(p)
            p.start()
            
        for _ in range(cpus):
            message_queue.get()


        tmp_fill_image = result01_queue.get()
        tmp_comp_image = result02_queue.get()
        
        centerline = centerline | tmp_fill_image
        centerline = centerline | original_centerline
        centerline = component_size_label( centerline, numpy.ones( (3,3,3) ) )
        centerline [ centerline <= 4 ] = 0
        centerline = centerline.astype( numpy.bool )
        
        if ( centerline == tmp_out_cen ).all():
            switch = 0

        for i in process_store:
            if i.is_alive():
                i.terminate()
             
    return centerline

def gap_closing_process(vesselness, centerline, region_size, voxelspacing, original_centerline, tmp_comp_image, lock, point_queue, result01_queue, result02_queue, message_queue):

    while True:
    
        lock.acquire()
        
        if point_queue.qsize():
            tmp_point = point_queue.get(False)
            lock.release()

        else:  
            result02_queue.put(tmp_comp_image)
            message_queue.put(1)
            lock.release()
            break

        potential_points_image = numpy.zeros(centerline.shape, numpy.bool)
       
        if tmp_comp_image[tmp_point[0], tmp_point[1], tmp_point[2]] == True:
            continue
        
        list_of_branchpoints = give_branch_points(centerline , tmp_point, 5)
       
        if 2 >= len(list_of_branchpoints):
            continue
 
        threshold = 0.3 * numpy.mean( return_value(list_of_branchpoints, vesselness) )
        
        end_point = numpy.asarray( tmp_point )
        initial_direction = calc_direction( list_of_branchpoints[-1], list_of_branchpoints[0], voxelspacing )
        
        slicers = [ slice(max(p, region_size) - region_size, p + region_size) for p in end_point ]
        tmp_slice_image = numpy.zeros(centerline.shape, numpy.bool)
        tmp_slice_image[ slicers ] = 1
        
        #searching potential points of the centerline as continuation point
        potential_points = numpy.nonzero(original_centerline * tmp_slice_image) 
        potential_points = zip(potential_points[0], potential_points[1], potential_points[2])
        
        for potential_point in potential_points:
            
            if not (end_point == potential_point).all():
            
                    potential_vector = calc_direction( end_point, potential_point, voxelspacing )
  
                    if 60 >= calc_angle(initial_direction, potential_vector)\
                    and 5 >= dist(end_point, potential_point, voxelspacing):
                        potential_points_image[potential_point[0]][potential_point[1]][potential_point[2]] = True
        
        #trying to fill gap
        if numpy.max( potential_points_image ):

            potential_points = numpy.nonzero( potential_points_image )
            potential_points = zip( potential_points[0], potential_points[1], potential_points[2] )
            
            potential_points2 = potential_points

            filled = 0

            for _ in potential_points:
                tmp_end_point = numpy.asarray(tmp_point)
                
                if 0 == len(potential_points2):
                    image_gapclosing_points = numpy.zeros(centerline.shape, numpy.bool)
                    break              
     
                nearest_point = nearest_neigbor(tmp_end_point, potential_points2, voxelspacing)
                potential_points2.remove(nearest_point)     
                image_gapclosing_points = numpy.zeros(centerline.shape, numpy.bool) 
                
                switch=1
                while switch:

                    direction = calc_direction(tmp_end_point, nearest_point, voxelspacing)
                    
                    slicer = [ slice(max(p, 1) - 1, p + 2) for p in tmp_end_point ]
                    tmp_image2 = numpy.zeros(centerline.shape, numpy.bool)
                    tmp_image2[ slicer ] = 1
                    tmp_max_vessel = tmp_image2 * vesselness
                    tmp_max_vessel[tmp_end_point[0],tmp_end_point[1],tmp_end_point[2]]=0
                  
                    while True:
                        
                        tmp_vessel_max_value = numpy.max(tmp_max_vessel)
                        
                        if not tmp_vessel_max_value:
                            switch = 0
                            set_point = 0
                            break
                        
                        next_possible_point = numpy.nonzero( numpy.max(tmp_max_vessel) == tmp_max_vessel )
                        next_possible_point = [ next_possible_point[0][0], next_possible_point[1][0], next_possible_point[2][0] ]
                        
                        if tmp_max_vessel[next_possible_point[0], next_possible_point[1], next_possible_point[2]] > threshold \
                        and ( 60 >= calc_angle( direction, calc_direction(tmp_end_point, next_possible_point, voxelspacing) )  \
                        or( direction == calc_direction(tmp_end_point, next_possible_point, voxelspacing) ).all() ):
                            
                            slicer = [ slice(max(p, 1) - 1, p + 2) for p in next_possible_point ]

                            if 1 > numpy.count_nonzero( image_gapclosing_points[ slicer ] ):
                            
                                set_point = next_possible_point
                                break

                        tmp_max_vessel[ next_possible_point[0], next_possible_point[1], next_possible_point[2] ] = 0
                    
                    
                    if set_point:
                        tmp_end_point = set_point                    
                        image_gapclosing_points[tmp_end_point[0]][tmp_end_point[1]][tmp_end_point[2]] = True
                    
                    #checking if gap is filled
                    if check_neighbor_list( tmp_end_point, potential_points ) or check_if_nachbar( tmp_end_point,nearest_point ):
                        filled = 1
                        break
                 
                if filled:
                    break             
           
            if filled:      
                lock.acquire()
                image_closingpoints = result01_queue.get() 
                image_closingpoints = image_closingpoints | image_gapclosing_points
                result01_queue.put( image_closingpoints )  
                lock.release()         
    
    return 0

def occlusion_detection(vesselness, centerline, segmentation, voxelspacing, logger):
    'Searches potential occlusions in MRA-data by using four different criteria'
    
    occlusion_counter = 0
    # image with marked occlusions
    image_occlusion = numpy.zeros(centerline.shape, numpy.bool)
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
    print 'To be checked number of branches: {}'.format(len(endpoints_of_branches))

    # preparing multiprocessing 
    try:
        cpus = multiprocessing.cpu_count()
    except NotImplementedError:
        cpus = 2
    cpus = min(cpus, 8)
    
    lock = multiprocessing.Lock()
    message_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()
    
    point_queue = multiprocessing.Queue()
    for point in endpoints_of_branches:
        point_queue.put(point)
        
    process_store = []
    for _ in range(cpus):
        p = multiprocessing.Process(target=occlusion_calc_process, args=(centerline, vesselness, voxelspacing, lock, result_queue, point_queue, message_queue))
        process_store.append(p)
        p.start()
    
    for _ in range(cpus):
        message_queue.get()
        
    for _ in range(cpus):
        a, b, c, d, e, f, g, h = result_queue.get()
        list_inside_branch_point += a
        list_inside_branch_values += b
        all_values_inside_vessel += c
        all_max_gradients += d
        list_outside_branch_point += e
        list_outside_branch_values += f
        list_tmp_point += g
        dict_of_inner_branch_points.update( h )

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
            occlusion_counter += 1 
            print 'detected occlusion at: {}'.format(tmp_point)
    print 'number of detected occlusions: {}'.format(occlusion_counter)

    image_occlusion = binary_dilation(image_occlusion, iterations=5, mask=segmentation) + image_occlusion
    
    
    for i in process_store:
        if i.is_alive():
            i.terminate()
    
    
    return image_occlusion

def occlusion_calc_process(centerline, vesselness, voxelspacing, lock, result_queue, point_queue, message_queue):
    
    number_of_points = 10

    list_inside_branch_point = []
    list_inside_branch_values = []
    all_values_inside_vessel = []
    all_max_gradients = []
    list_outside_branch_point = []
    list_outside_branch_values = []
    list_tmp_point = []
    dict_of_inner_branch_points = {}
    
    while True:
        
        lock.acquire()
        
        if point_queue.qsize():
            tmp_point = point_queue.get(False)
            lock.release()
        else:
            result_queue.put([list_inside_branch_point, list_inside_branch_values, all_values_inside_vessel, all_max_gradients, \
                       list_outside_branch_point, list_outside_branch_values, list_tmp_point, dict_of_inner_branch_points ])
            message_queue.put(1)
            lock.release()
            break
             
        # calculating vesselness-values along a branch
        tmp_image = numpy.zeros(centerline.shape, numpy.bool)
        tmp_compare_image = numpy.zeros(centerline.shape, numpy.bool)
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
            for _ in range(0, 2 * number_of_points):
                
                if not check_border(centerline, list_of_branch_points[0]):
                    break
              
                next_point = give_branch_extension(thin_for_extension, vesselness, list_of_branch_points, tmp_second_point, voxelspacing)
                
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
    return 0

def dist(x, y, pixel_spacing):
    pixel_spacing = numpy.asarray( pixel_spacing )
    x = x * pixel_spacing
    y = y * pixel_spacing    
       
    return numpy.sqrt( numpy.sum( (x-y)**2 ) )

def nearest_neigbor(end_point, all_points_list, pixel_spacing):
    nearest_point = all_points_list[0]
    for index in all_points_list:        
        if dist(end_point,nearest_point,pixel_spacing) > dist(end_point,index,pixel_spacing):
            nearest_point = index
    return nearest_point

def check_neighbor_list(punkt, liste):
    for i in liste:
        if check_if_nachbar(punkt, i):
            return True
    return False

def check_if_nachbar(point1, point2):
    max_value = numpy.max([point1[0]-point2[0], point1[1]-point2[1] , point1[2]-point2[2]])
    min_value = numpy.min([point1[0]-point2[0], point1[1]-point2[1] , point1[2]-point2[2]]) 
    
    if max_value >= 2 or min_value <=-2:
        return False
    else:
        return True

def remove_short_branches( centerline, vesselness, minimal_branch_length, logger):
    'Removes short branches of skeleton by using vesselness data based on two different criteria'

    enhanced_centerline = numpy.copy( centerline )
        
    image_neighbor = count_neighbor( centerline, numpy.ones((3,3,3)) )

    intersection_points = numpy.nonzero( 3 <= image_neighbor ) 
    intersection_points = zip(intersection_points[0], intersection_points[1], intersection_points[2])
    logger.info(('To be checked number of intersection_points: {}').format(len(intersection_points)))

    try:
        cpus = multiprocessing.cpu_count()
    except NotImplementedError:
        cpus = 2
    cpus = min(cpus, 8)
    
    lock = multiprocessing.Lock()
    
    result_queue = multiprocessing.Queue()  
    result_queue.put(enhanced_centerline)
    
    point_queue = multiprocessing.Queue()
    message_queue = multiprocessing.Queue()

    for point in intersection_points:
        point_queue.put(point)
    
    process_store = []
    for _ in range(cpus):
        p = multiprocessing.Process(target=remove_short_branch_process, args=( centerline, vesselness, image_neighbor, minimal_branch_length, lock, result_queue, point_queue, message_queue ))
        p.start()
        process_store.append(p)

    for _ in range(cpus):
        message_queue.get()
    
    result = result_queue.get(False)
        
    for i in process_store:
        if i.is_alive():
            i.terminate()
    return result
            
def remove_short_branch_process( centerline, vesselness, image_neighbor, minimal_branch_length, lock, result_queue, point_queue, message_queue):
    
    while True:
        
        lock.acquire()
        if point_queue.qsize():
            tmp_intersection = point_queue.get(False)
            lock.release()
        else:
            message_queue.put(1)
            lock.release()
            break
    
        list_short_branches = give_short_surrounding_branches( centerline, image_neighbor, tmp_intersection, 10 )

        for iterator in range( len( list_short_branches ) ):
            # checking if branch is to short
            if len( list_short_branches [ iterator ]) <= minimal_branch_length:
         
         
                enhanced_centerline = result_queue.get()
                for tmp_nbr in range( len( list_short_branches [ iterator ] )):
                    enhanced_centerline[ list_short_branches [ iterator ][ tmp_nbr ] ] = 0
                
                result_queue.put(enhanced_centerline)
           
    
            else:
                # checking if vesselness of current branch is high enough
                mean_vesselness_endpoints = []
                
                for index in range(-3,0):
                    mean_vesselness_endpoints.append( vesselness[ list_short_branches [ iterator ][ index ] ] )
                
                mean_vesselness_endpoints = numpy.mean( mean_vesselness_endpoints ) 
                               
                
                main_branch = numpy.zeros( centerline.shape, numpy.bool)
                #main_branch[ zip(*tmp_intersection) ] = 1
                
                main_branch[tmp_intersection[0]][tmp_intersection[1]][tmp_intersection[2]]=1
                
                main_branch = binary_dilation(main_branch, structure=numpy.ones((3,3,3)), iterations=5, mask=centerline,)
                
                for index4 in range( len( list_short_branches [ iterator ] )):
                    main_branch[ list_short_branches [ iterator ][ index4 ] ] = 0
                
                values = main_branch * vesselness

                mean_vesselness_mainbranch = 0
                mean_vesselness_mainbranch = numpy.mean( values[ numpy.nonzero( values ) ] )


                if ((not mean_vesselness_mainbranch == 0) and (mean_vesselness_mainbranch*(0.3) >= mean_vesselness_endpoints)):

                    
                    enhanced_centerline = result_queue.get()
                    for tmp_nbr in range( len( list_short_branches [ iterator ] )):
                        enhanced_centerline[ list_short_branches [ iterator ][ tmp_nbr ] ] = 0
                        
                    result_queue.put(enhanced_centerline)
    return 0

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
    
    for _ in range(length - 1):
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

def calc_direction(point1, point2, voxelspacing):
    'calculates the direction between the given points, returns a vector'
    point1 = numpy.asarray(point1)
    point2 = numpy.asarray(point2)
    return (point2 - point1) * voxelspacing 

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
      
def give_branch_extension(skeleton, vesselness, list_of_branch_points, tmp_point, voxelspacing):
    'gives the next point of a extended branch'
    tmp_point = [tmp_point[0], tmp_point[1], tmp_point[2]]
    last_point = list_of_branch_points[ 0 ] 
    initial_direction = calc_direction(tmp_point, last_point, voxelspacing) 
   
    slicers = [ slice(max(p, 1) - 1, p + 2) for p in last_point ]
    tmp_image = numpy.zeros(skeleton.shape)
    tmp_image[ slicers ] = 1
    tmp_image[ last_point[0], last_point[1], last_point[2] ] = 0     
    tmp_vesselness = vesselness * tmp_image

    while numpy.max(tmp_vesselness):        
          
        potential_point = numpy.nonzero(numpy.max(tmp_vesselness) == tmp_vesselness)
        potential_point = [potential_point[0][0], potential_point[1][0], potential_point[2][0]]

        if 60 >= calc_angle(initial_direction, calc_direction(last_point, potential_point, voxelspacing)) \
            and number_of_neighbors(skeleton, potential_point) <= 1 \
            and not check_if_neigbor(potential_point, list_of_branch_points[ 1 ]):

                return potential_point   
        
        else:
            tmp_vesselness[ potential_point[0], potential_point[1], potential_point[2] ] = 0
   
    return 0
    
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
    
def component_size_label(image, structure):
    'returns image where all connected binary objects are labeled with the size of its region'

    labeled_array, num_features = label( image, structure )
    temp = labeled_array.copy()

    for i in range( 1, num_features+1 ):
        labeled_array[ numpy.nonzero( temp == i ) ] = ( numpy.count_nonzero( temp == i ) )

    return labeled_array
    
    
    
    
    