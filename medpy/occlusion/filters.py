'''
Created on Aug 25, 2014
@package medpy.occlusion.filters

@author: kleinfeld

@version 0.2.1
@since 2014-08-25
@status
'''


# build-in modules
from scipy.ndimage.measurements import label, histogram
from scipy.ndimage.morphology import binary_dilation


# third-party modules
import numpy
import multiprocessing
# own modules
from medpy.filter.image import sum_filter
from medpy.metric.binary import __surface_distances


# code
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
        d = queue2.get()
        endpoints_of_branches = queue2.get()

        if endpoints_of_branches:
            tmp_point = endpoints_of_branches[0]
            endpoints_of_branches.remove(tmp_point)
            
            d += 1
            print 'number: {}'.format(d)
            
            queue2.put(d)
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
            
            queue2.put(d) 
            queue2.put(endpoints_of_branches) 
            
            lock.release()
            switch = 0

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
    queue2.put(0)
    queue2.put(endpoints_of_branches)
  
    precess_store = []
    for i in range(cpus):
        p = multiprocessing.Process(target=occlusion_calc_process, args=(centerline, vesselness, lock, queue, queue2))
        p.start()
        precess_store.append(p)
    '''
    switch = 1
    while switch:
        for i in range(cpus):
            a = precess_store[i]
            if not a. is_alive():
                switch = 0
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

    
    # Counter of detected occlusions    
    occlusion_counter = 0
    
    a = 0
    b = 0
    c = 0
    d = 0
 
     
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

        # check diameter of vessel
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

        
        if numpy.median(outsidevalues) <= numpy.median(insidevalues) * 0.3:
            a = a + 1
            print 'median'
            print tmp_point
        if mean_all_values <= numpy.mean(insidevalues):
            b = b + 1
            print 'mean'
            print tmp_point
        if tmp_max_gra >= mean_gra:
            c = c + 1
            print 'gra'
            print tmp_point
        if vesselthickness > 4.0:
            d = d + 1
            print 'thickness'
            print tmp_point
            
        if numpy.median(outsidevalues) <= numpy.median(insidevalues) * 0.3 \
            and mean_all_values <= numpy.mean(insidevalues) \
            and tmp_max_gra >= mean_gra:
      
            if vesselthickness < 4.0:
                continue
       
            # marking the potential occlusion
            for point in dict_of_inner_branch_points[ tmp_point ]:
                image_occlusion[point[0]][point[1]][point[2]] = 1
 
            occlusion_counter += 1
            print 'occlusion at: {} \n'.format(tmp_point)
            
    print 'number of possible occlusions: {} \n\n'.format(occlusion_counter)
    print a
    print b
    print c
    print d
    
    image_occlusion = binary_dilation(image_occlusion, iterations=5, mask=segmentation)
    return image_occlusion


def count_neighbor(image, structure):
    'returns image, where the current voxelvalue is the number of its neigbors'
    image = image.astype(numpy.bool)
    sumimage = sum_filter(image, footprint=structure, mode="constant", cval=0.0, output=numpy.uint)
    sumimage[~image] = 0
    return sumimage - image

def give_branch_points(thinned_image, branch_endpoint, length):
    'returns a list with the last points of a branch (maximal as long as length, inclusive intersection point) needed input: thinned image and last point of current branch' 
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

def number_of_neighbors(image, point):
    
    slicers = [ slice(max(p, 1) - 1, p + 2) for p in point ]
    tmp_image = numpy.zeros(image.shape)
    tmp_image[ slicers ] = 1
    tmp_image[ point[0], point[1], point[2]] = 0
    return numpy.count_nonzero(image * tmp_image) 

def give_branch_extension(skeleton, vesselness, list_of_branch_points, tmp_point):
    
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





def close_gaps(labeled_cen, av, pixel_spacing, vesselness_image, ori_cen, zwischenspeicher, cen_h):
    
    '''
       input:
           labeled_cen: centerline of largest component
           av: Anzahl der Punkte, welche die Groesse der Box definieren, die am um das Ende der Arterienarme erzeugt wird
               In dieer Box befindet sich der Kegel, der vom letzten Punkt des Arterienastes aus geht und der umliegende Aterienpunkte sucht
        pixel_spacing: pixelspacing of the mra, image
        vesselness_image: vesselness of the mra image
        ori_cen: original centerline, die moegliche Weiterfuehrungsaeste beinhaltet 
    '''
    ##################################################
    counter = 0
    ##################################################
    
    # Ermitteln aller Endpunkte der Centerline
    all_endboints = numpy.nonzero(1 == count_neighbor(labeled_cen , numpy.ones((3, 3, 3))))
    
    return_image = numpy.zeros(labeled_cen.shape, numpy.bool) 
        
    return_cone_image = numpy.zeros(labeled_cen.shape, numpy.bool) 
    
    # Ueber alle Endpunkte iterieren 
    for tmp in range(numpy.size(all_endboints[0])):
        
        end_point = (all_endboints[0][tmp], all_endboints[1][tmp], all_endboints[2][tmp])  # aktuell zu bearbeitender Endpunkt
        end_point_speicher = end_point
        if zwischenspeicher[end_point[0]][end_point[1]][end_point[2]] == 1:
   
            return_image = return_image | ori_cen
            continue
        
        list_of_branchpoints = give_branch_points(labeled_cen , end_point, 5)  # die letzten 5 Punkte des Aterienastes (maximal 5 Punkte)
    
        # Berechnung der initialen Richtung, wenn der zu bearbeitende Arterienast aus mehr als zwei Punkten besteht
        if 2 >= len(list_of_branchpoints):
            continue
        initial_direction = calc_direction(list_of_branchpoints[-1], list_of_branchpoints[0])
        
        cone_image = numpy.zeros(labeled_cen.shape, numpy.bool) 
        end_point = numpy.asarray(end_point)
        
        # Berechnung des Vesselschwellwertes
        
        schwellwert = return_value(list_of_branchpoints, vesselness_image)
        schwellwert = 0.3 * numpy.mean(schwellwert)
        
        # Erzeugung der Box um den letzten Arterienpunkt     
        for i in range(max(0, end_point[0] - av), min(labeled_cen.shape[0] - 1, end_point[0] + av + 1)):
            for j in range(max(0, end_point[1] - av), min(labeled_cen.shape[1] - 1, end_point[1] + av + 1)):
                for k in range(max(0, end_point[2] - av), min(labeled_cen.shape[2] - 1, end_point[2] + av + 1)):
       
                    potential_point = numpy.asarray((i, j, k))
                    
                    if not (end_point == potential_point).all():
                        potential_vector = potential_point - end_point
  
                        if 60 >= calc_angle(initial_direction, potential_vector)\
                        and 5 >= dist(end_point, potential_point, pixel_spacing):
                            cone_image[potential_point[0]][potential_point[1]][potential_point[2]] = True
        return_cone_image = return_cone_image + cone_image
        
        
        
        zwischenspeicher[end_point[0]][end_point[1]][end_point[2]] = 1
        # Suche nach Fortsetzungspunkten fuer moegliche Lueckenfuellung
        if numpy.max(cone_image & ori_cen):

            next_points = numpy.nonzero(cone_image & ori_cen)

            alle_punkte = []
            
            # suche den dichtesten Punkt
            for index1 in range(numpy.size(next_points[0])):
                alle_punkte.append((next_points[0][index1], next_points[1][index1], next_points[2][index1]))
            alle_punkte2 = alle_punkte
            # FUNKTION SCHREIBEN solange wie punkte in nearest_point wird gesucht, jedoch nur solange, wie image_gapclosing_points ueberall null ist
            for index in alle_punkte2:
                end_point = end_point_speicher
                end_point = numpy.asarray(end_point)
                if 0 == len(alle_punkte2):
                    image_gapclosing_points = numpy.zeros(labeled_cen.shape, numpy.bool)
                    break                
                nearest_point = nearest_neigbor(end_point, alle_punkte2, pixel_spacing)
                
            
            # while schleife die solange laeuft bis einer der next_points erreicht wird und entlang der vesselness in eine bestimmte richtung geht
            # diese richtung wird aus dem zuletzt gesetzten punkt und dem Punkt (nearest_point) ermittelt
                image_gapclosing_points = numpy.zeros(labeled_cen.shape, numpy.bool) 
                
                while (not check_nachbar_list(end_point, alle_punkte)) and (not check_if_neigbor(end_point, nearest_point)) :
              
                    # Berechnung des naechsten Punktes
                    
                    vesselness = 0
                    direction = calc_direction(end_point, nearest_point)
                    
                    for x in range(-1, 2):
                        for y in range(-1, 2):
                            for z in range(-1, 2):
                                if not(0 == x and 0 == y and 0 == z):
                                    
                                    next_possible_point = numpy.asarray((end_point[0] + x, end_point[1] + y, end_point[2] + z))
                                    if check_inside(vesselness_image, next_possible_point):
                                        if vesselness <= vesselness_image[next_possible_point[0]][next_possible_point[1]][next_possible_point[2]]:
                                            
                                            # print direction
                                            # print calc_direction(end_point, next_possible_point)
                                            
                                            if (direction == calc_direction(end_point, next_possible_point)).all() \
                                            or (direction == calc_direction(next_possible_point, end_point)).all() :
                                                vesselness = vesselness_image[next_possible_point[0]][next_possible_point[1]][next_possible_point[2]]
                                                set_point = next_possible_point
                                            elif 60 >= calc_angle(direction, calc_direction(end_point, next_possible_point)):
                                                vesselness = vesselness_image[next_possible_point[0]][next_possible_point[1]][next_possible_point[2]]
                                                set_point = next_possible_point

             
                    # diese Zeile muss so sein... =) 
                    end_point = set_point                    
                   
                    # punkt setzten        
    
                    image_gapclosing_points[end_point[0]][end_point[1]][end_point[2]] = True
                
                # schwellwert_image = schwellwert_image | image_gapclosing_points
            
            # Vesselschwellwertkontrolle
                if image_gapclosing_points.max():  # Absicherung, dass was in image_gapclosing_points auf TRUE ist
                    schwellwert_points = numpy.nonzero(image_gapclosing_points)
                    min_schwellwert = numpy.min(vesselness_image[schwellwert_points])
                
                    if min_schwellwert < schwellwert:
                        image_gapclosing_points = numpy.zeros(labeled_cen.shape, numpy.bool)
                        alle_punkte2.remove(nearest_point)
                        
                        # print 'zu kleiner Schwellwert: '
                        # print schwellwert_points
                        continue
                    else:
                        # print 'es wird gefuellt: '
                        zwischenspeicher[nearest_point[0]][nearest_point[1]][nearest_point[2]] = 1
                        # print schwellwert_points
                        
                        ##################################################
                        counter = counter + 1
                        ##################################################
                        
                        break
                else:
                    image_gapclosing_points = numpy.zeros(labeled_cen.shape, numpy.bool)
                    alle_punkte2.remove(nearest_point)
                    # print 'Anderes esle'
                    continue
            return_image = return_image | image_gapclosing_points
            return_image = return_image | ori_cen
            
    return return_image, zwischenspeicher, counter

def check_nachbar_list(punkt, liste):
    for i in liste:
        if check_if_neigbor(punkt, i):
            return True
    return False

def nearest_neigbor(end_point, alle_punkte, pixel_spacing):
    nearest_point = alle_punkte[0]
    for index in alle_punkte:        
        if dist(end_point, nearest_point, pixel_spacing) > dist(end_point, index, pixel_spacing):
            nearest_point = index
    return nearest_point
     
def check_inside(image, point):
    # checks if point is in image
    for i in range(3):
        if((point[i] < 0) | (point[i] >= image.shape[i])):
            return 0
    return 1

def component_size_label(image, structure):
# returns image where all connected binary objects (structure like in function label) are labeled with the size of its component
    labeled_array, num_features = label(image, structure)
    temp = labeled_array.copy()
    counter = 0
    # print num_features
    for i in range(1, num_features + 1):
        labeled_array[ numpy.nonzero(temp == i)] = (numpy.count_nonzero(temp == i))
        # print counter
        counter = counter + 1

    return labeled_array    
      
def dist(x, y, pixel_spacing):
    pixel_spacing = numpy.asarray(pixel_spacing)
    x = x * pixel_spacing
    y = y * pixel_spacing    
       
    return numpy.sqrt(numpy.sum((x - y) ** 2))

def calc_angle(vector1, vector2):
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
    max_value = numpy.max([point1[0] - point2[0], point1[1] - point2[1] , point1[2] - point2[2]])
    min_value = numpy.min([point1[0] - point2[0], point1[1] - point2[1] , point1[2] - point2[2]]) 
    
    if max_value >= 2 or min_value <= -2:
        return False
    else:
        return True
      
def check_durchmesser(seg, point):
    if 19 <= number_of_neighbors(seg, point):  # bei 26 werden in den ersten Datensaetzen die Okklusionen nicht erkannt
        return True
    else:    
        return False
  
def check_inside_mask(branchpoints, mask):
    'Returns False, if points of branch are not inside mask'
    for i in range(len(branchpoints)):
        if not 1 <= mask[branchpoints[i][0]][branchpoints[i][1]][branchpoints[i][2]]:
            return False
    return True

def check_distance_mask(branch_point, brainmask, voxelspacing, distance):
    # Kantenlaenge des Kastens um die Branchpoints
    box = 4
    
    image = numpy.zeros(brainmask.shape)
    imagepoint = numpy.zeros(brainmask.shape)
    imagepoint[branch_point[0]][branch_point[1]][branch_point[2]] = 1
    
    for i in range(max(0, branch_point[0] - box), min(brainmask.shape[0] - 1, branch_point[0] + box + 1)):
        for j in range(max(0, branch_point[1] - box), min(brainmask.shape[1] - 1, branch_point[1] + box + 1)):
            for k in range(max(0, branch_point[2] - box), min(brainmask.shape[2] - 1, branch_point[2] + box + 1)):
                image[i][j][k] = 1
                    
    image2 = image * brainmask

    if 0 == numpy.max(image2):
        return True
    

    if __surface_distances(imagepoint, image2, voxelspacing, 1).min() >= distance:      
        # Weiterhin Okklusionskadidat
        return True
    
    else:
        # Zu dicht am Rand, kein Okklusionskadidat
        # print 'Zu dicht am Maskenrand'
        # print branch_point
        return False
    '''
    image = numpy.zeros(brainmask.shape)
    for i in range(0,len(branch_point)):
        image[branch_point[i][0]][branch_point[i][1]][branch_point[i][2]] = 1
    print __surface_distances(image, brainmask, voxelspacing, 1).min() 
    if __surface_distances(image, brainmask, voxelspacing, 1).min() >= distance:
        return True
    else:
        return False
    '''
 
def largest_connected_component(image, structure):
    'returns image with the largest connected components, labeled with 1'
    
    image, liste = label(image, structure)
    hist = histogram(image, 1, numpy.max(image), numpy.max(image))
    
    return_image = numpy.zeros(image.shape, image.dtype)
    
    return_image[ image == 1 + numpy.where(hist == hist.max())[0][0] ] = 1
    
    return return_image

def return_neighbor_old(image, point, width):
# returns a list with points of surrounding, excluding the original point
    if not width:
        return 0
    else:
        liste = []
        for i in range(-width, width + 1):
            for j in range(-width, width + 1):
                for k in range(-width, width + 1):
                    if check_inside(image, [point[0] + i, point[1] + j, point[2] + k])\
                    and image[point[0] + i, point[1] + j, point[2] + k]\
                    and not (i == 0 and j == 0 and k == 0):
                        liste.append((point[0] + i, point[1] + j, point[2] + k))
    return liste

def remove_short_branch_vesselness(thinned_image, vesselness, branches_shorter_than):
    # ueberpruefung der centerline auf datentyp
    
    unter4 = 0
    unter10 = 0
    
    if thinned_image.max != 1 or thinned_image.dtype == numpy.bool: 
        thinned_image = numpy.asarray(thinned_image, dtype=numpy.bool)
        thinned_image = numpy.asarray(thinned_image, dtype=numpy.int)


    thinned_image2 = numpy.copy(thinned_image)
    # Bild mit Anzahl der Nachbarpunkte
    image_neighbor = count_neighbor(thinned_image, numpy.ones((3, 3, 3)))

    # Liste alles Punkte, die eine Abzweigung beinhalten
    kreuzungspunkte = numpy.nonzero(image_neighbor >= 3)
    
    # ueber alle kreuzungspunkte iterieren
    for iterate_branches in range(0, numpy.size(kreuzungspunkte, 1)): 
        temp_kreuzungspunkt = (kreuzungspunkte[0][iterate_branches] , kreuzungspunkte[1][iterate_branches] , kreuzungspunkte[2][iterate_branches])
        # Liste die die einzelnen, abzwigenden Arme beinhaltet
        gelistete_seitenarme = return_short_branches(thinned_image , image_neighbor , temp_kreuzungspunkt , 10)

        # ueber die moeglichen Seitenarme iterieren

        for temp_seitenarme in range(0, len(gelistete_seitenarme)):
            # wenn die Minimallaenge unterschritten wird, dann wird auf jeden fall geloescht
            if len(gelistete_seitenarme [ temp_seitenarme ]) <= branches_shorter_than:
                unter4 = unter4 + 1
                for number_of_branchpoints in range(0, len(gelistete_seitenarme [ temp_seitenarme ])):
                    thinned_image2[ gelistete_seitenarme [ temp_seitenarme ][ number_of_branchpoints ] ] = 0
            # sonst ueberpruefe die Vesselness vom Seitenarme und den anderen Armen, die vom gleichen Kreuzungspunkt ausgehen
            else:
                # Bestimmen der Durchschnittsvesselness der letzten 3 Punkte
                vesselvalue1 = []
                for index in range(-3, 0):
                    vesselvalue1.append(vesselness[ gelistete_seitenarme [ temp_seitenarme ][ index ] ])
                # Durchschnittliche Vesselness der letzten drei Astpunkte des zu ueberpruefenden Seitenarmes
                vesselvalue1 = numpy.mean(vesselvalue1) 
                               
                
                zu_delitieren = numpy.zeros(thinned_image.shape)
                zu_delitieren[temp_kreuzungspunkt[0]][temp_kreuzungspunkt[1]][temp_kreuzungspunkt[2]] = 1
                
                zu_delitieren = binary_dilation(zu_delitieren, structure=numpy.ones((3, 3, 3)), iterations=5, mask=thinned_image,)
                
                for index4 in range(0, len(gelistete_seitenarme [ temp_seitenarme ])):
                    zu_delitieren[ gelistete_seitenarme [ temp_seitenarme ][ index4 ] ] = 0
                
                values = zu_delitieren * vesselness

                vesselvalue2 = 0
                if not 0 == numpy.count_nonzero(values):
                    vesselvalue2 = sum(sum(sum(values))) / numpy.count_nonzero(values)

                if ((not vesselvalue2 == 0) and (vesselvalue2 * (0.3) >= vesselvalue1)):
                    # print 'ES WIRD GELOESCHTTTTTT'
                    # print list_branch_points [ number_of_branches ]
                    unter10 = unter10 + 1
                    
                    for number_of_branchpoints in range(0, len(gelistete_seitenarme [ temp_seitenarme ])):
                        thinned_image2[ gelistete_seitenarme [ temp_seitenarme ][ number_of_branchpoints ] ] = 0
                
    return thinned_image2, unter4, unter10

def remove_short_branch(thinned_image, branches_shorter_than):
    
    if thinned_image.max != 1 or thinned_image.dtype == numpy.bool: 
        thinned_image = numpy.asarray(thinned_image, dtype=numpy.bool)
        thinned_image = numpy.asarray(thinned_image, dtype=numpy.int)
    
    image_neighbor = count_neighbor(thinned_image, numpy.ones((3, 3, 3)))

    branch_points = numpy.nonzero(image_neighbor >= 3)
  
    for iterate_branches in range(0, numpy.size(branch_points, 1)):  # ueber alle kreuzungspunkte iterieren
        temp_branch_point = (branch_points[0][iterate_branches] , branch_points[1][iterate_branches] , branch_points[2][iterate_branches])
        list_branch_points = return_short_branches(thinned_image , image_neighbor , temp_branch_point , branches_shorter_than)
        
        for number_of_branches in range(0, len(list_branch_points)):  # Punkte loeschen
            for number_of_branchpoints in range(0, len(list_branch_points [ number_of_branches ])):
                thinned_image[ list_branch_points [ number_of_branches ][ number_of_branchpoints ] ] = 0
                
    return thinned_image

def return_short_branches(thinned_image, image_neighbor, branch_point, max_branch_length):
    '''
    gibt eine Liste zurueck, die mehrere Listen mit den jeweiligen Astpunkten beinhaltet, die hoechstens so lang wie max_branch_length sind
    '''
    next_neighbors = return_neighbor_old(thinned_image, branch_point, 1)
    return_list = []
    
    for next_point in range(0, len(next_neighbors)):
        
        temp_branch_points = [branch_point]
        temp_branch_points = search_branch(thinned_image, image_neighbor, temp_branch_points, next_neighbors[next_point], max_branch_length)        
        
        if temp_branch_points:
            return_list.append(temp_branch_points)
   
    return return_list

def search_branch(thinned_image, image_neighbor, list_point, next_point, max_branch_length):
    
    list_point.append(next_point)
        
    if(1 == max_branch_length):
        # wenn keine Schritte mehr, dann wird Suche beendet
        if(1 == image_neighbor[next_point]):
            list_point.pop(0)
            return list_point
        else:
            return
           
    else:
        if(2 == image_neighbor[next_point]):  # wenn nur zwei nachbarn, dann ist alles gut und es geht los
        
            nachbarn = return_neighbor_old(thinned_image, next_point, 1)
            
            
            if(nachbarn[0] not in list_point):
                return search_branch(thinned_image, image_neighbor, list_point, nachbarn[0], max_branch_length - 1)
                  
            elif(nachbarn[1] not in list_point):
                return search_branch(thinned_image, image_neighbor, list_point, nachbarn[1], max_branch_length - 1)
            
            else:
                return
        
        elif(1 == image_neighbor[next_point]):
            list_point.pop(0)
            return list_point
        
        else:
            return
        
def give_branch(thinned_image, image_neighbor, list_point, next_point, max_branch_length):
    
    list_point.append(next_point)
        
    if(1 == max_branch_length):
        # wenn keine Schritte mehr, dann wird Suche beendet
        list_point.pop(0)
        return list_point
           
    else:
        if(2 == image_neighbor[next_point]):  # wenn nur zwei nachbarn, dann ist alles gut und es geht los
        
            nachbarn = return_neighbor_old(thinned_image, next_point, 1)
            
            
            if(nachbarn[0] not in list_point):
                return give_branch(thinned_image, image_neighbor, list_point, nachbarn[0], max_branch_length - 1)
                  
            elif(nachbarn[1] not in list_point):
                return give_branch(thinned_image, image_neighbor, list_point, nachbarn[1], max_branch_length - 1)
            
            else:
                # Ring detektiert, oder?!
                return
    
        else:
            list_point.pop(0)
            return list_point
