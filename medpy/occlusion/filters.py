'''
Created on Aug 25, 2014
@package medpy.occlusion.filters

@author: kleinfeld

@version 0.1.1
@since 2014-08-25
@status
'''


# build-in modules
import pylab
from scipy.ndimage.measurements import label, histogram
from scipy.ndimage.morphology import binary_dilation
from copy import deepcopy

# third-party modules
import numpy

# own modules
from medpy.filter.image import sum_filter
from medpy.metric.binary import __surface_distances


# code
from medpy.io import save

def close_gaps(labeled_cen, av, pixel_spacing, vesselness_image, ori_cen, zwischenspeicher,cen_h):
    
    '''
       input:
           labeled_cen: centerline of largest component
           av: Anzahl der Punkte, welche die Groesse der Box definieren, die am um das Ende der Arterienarme erzeugt wird
               In dieer Box befindet sich der Kegel, der vom letzten Punkt des Arterienastes aus geht und der umliegende Aterienpunkte sucht
        pixel_spacing: pixelspacing of the mra, image
        vesselness_image: vesselness of the mra image
        ori_cen: original centerline, die moegliche Weiterfuehrungsaeste beinhaltet 
    '''
    
    #Ermitteln aller Endpunkte der Centerline
    all_endboints = numpy.nonzero(1 == count_neighbor(labeled_cen ,numpy.ones((3,3,3))))
    
    return_image = numpy.zeros(labeled_cen.shape, numpy.bool) 
    image_gapclosing_points = numpy.zeros(labeled_cen.shape, numpy.bool) 
    
    return_cone_image = numpy.zeros(labeled_cen.shape, numpy.bool) 
    
    
    #Ueber alle Endpunkte iterieren 
    for tmp in range( numpy.size(all_endboints[0]) ):
        
        end_point = (all_endboints[0][tmp],all_endboints[1][tmp],all_endboints[2][tmp]) #aktuell zu bearbeitender Endpunkt
        
        if zwischenspeicher[end_point[0]][end_point[1]][end_point[2]] == 1:
   
            return_image = return_image | ori_cen
            continue
        
        
        list_of_branchpoints = last_n_points_of_branch(labeled_cen , end_point, 5)   #die letzten 5 Punkte des Aterienastes (maximal 5 Punkte)
    
        #Berechnung der initialen Richtung, wenn der zu bearbeitende Arterienast aus mehr als zwei Punkten besteht
        if 2 >= len(list_of_branchpoints):
            continue
        initial_direction = calc_direction(list_of_branchpoints[-1], list_of_branchpoints[0])
        
        cone_image = numpy.zeros(labeled_cen.shape, numpy.bool) 
        end_point = numpy.asarray(end_point)
       
        #Erzeugung der Box um den letzten Arterienpunkt     
        for i in range(max(0, end_point[0]-av), min(labeled_cen.shape[0] - 1, end_point[0]+av+1)):
            for j in range(max(0, end_point[1]-av), min(labeled_cen.shape[1] - 1, end_point[1]+av+1)):
                for k in range(max(0, end_point[2]-av), min(labeled_cen.shape[2] - 1, end_point[2]+av+1)):
       
                    potential_point = numpy.asarray((i, j, k))
                    
                    if not (end_point == potential_point).all():
                        potential_vector = potential_point - end_point
  
                        if 60 >= calc_angle(initial_direction, potential_vector)\
                        and 5 >= dist(end_point, potential_point, pixel_spacing):
                            cone_image[potential_point[0]][potential_point[1]][potential_point[2]] = True
        return_cone_image = return_cone_image + cone_image
        
        
        
        zwischenspeicher[end_point[0]][end_point[1]][end_point[2]] = 1
        #Suche nach Fortsetzungspunkten fuer moegliche Lueckenfuellung
        if numpy.max(cone_image & ori_cen):
            next_points = numpy.nonzero(cone_image & ori_cen)
            nearest_point = numpy.asarray((next_points[0][0],next_points[1][0],next_points[2][0]))
            
            
            alle_punkte = []
            
            #suche den dichtesten Punkt
            for index in range(numpy.size(next_points[0])):
                test_point = numpy.asarray((next_points[0][index],next_points[1][index],next_points[2][index]))
                
                alle_punkte.append((next_points[0][index],next_points[1][index],next_points[2][index]))
                
                if dist(end_point,nearest_point,pixel_spacing) > dist(end_point,test_point,pixel_spacing):
                    nearest_point = test_point
            
            #while schleife die solange laeuft bis einer der next_points erreicht wird und entlang der vesselness in eine bestimmte richtung geht
            #diese richtung wird aus dem zuletzt gesetzten punkt und dem Punkt (nearest_point) ermittelt

            while not (end_point.tolist() in alle_punkte) and not check_ob_nachbar(end_point,nearest_point) :
          
                #Berechnung des naechsten Punktes
                
                vesselness = 0
                direction = calc_direction(end_point,nearest_point)
                
                for x in range(-1,2):
                    for y in range(-1,2):
                        for z in range(-1,2):
                            if not(0==x and 0==y and 0==z):
                                
                                next_possible_point = numpy.asarray((end_point[0]+x, end_point[1]+y, end_point[2]+z))
                                if check_inside(vesselness_image, next_possible_point):
                                    if vesselness <= vesselness_image[next_possible_point[0]][next_possible_point[1]][next_possible_point[2]]\
                                    and 60 >= calc_angle( direction, calc_direction(end_point, next_possible_point) ):
                                        
                                        vesselness = vesselness_image[next_possible_point[0]][next_possible_point[1]][next_possible_point[2]]
                                        set_point = next_possible_point
         
                #diese Zeile muss so sein... =) 
                end_point = set_point                    
               
                #punkt setzten        

                image_gapclosing_points[end_point[0]][end_point[1]][end_point[2]] = True
                return_image = return_image | image_gapclosing_points
            
            return_image = return_image | ori_cen
            
    return return_image, zwischenspeicher

def check_inside(image, point):
    #checks if point is in image
    for i in range(3):
        if( (point[i] < 0) | (point[i] >= image.shape[i]) ):
            return 0
    return 1

def component_size_label(image, structure):
#returns image where all connected binary objects (structure like in function label) are labeled with the size of its component
    labeled_array, num_features = label(image,structure)
    temp = labeled_array.copy()
    counter=0
    print num_features
    for i in range(1,num_features+1):
        labeled_array[ numpy.nonzero( temp == i )] = ( numpy.count_nonzero( temp == i ))
        print counter
        counter=counter+1

    return labeled_array
     
def branch_extension_initial(thin, vessel, anzahl_verlaengerung):
    endpoints_of_branches = numpy.nonzero(1 == count_neighbor(thin ,numpy.ones((3,3,3))))

    for tmp in range(0,numpy.size(endpoints_of_branches[0])):
        point = (endpoints_of_branches[0][tmp],endpoints_of_branches[1][tmp],endpoints_of_branches[2][tmp])
        liste_branchend = last_n_points_of_branch(thin , point, 3)
        
        if 2 < numpy.shape(liste_branchend)[0]:
            initiale_richtung = calc_direction(liste_branchend[1], liste_branchend[0]) 
        
        for i in range(0,anzahl_verlaengerung):
            if check_border(liste_branchend[0], thin) and 2 < numpy.shape(liste_branchend)[0]:
                next_point = branch_extension(thin, vessel, initiale_richtung,liste_branchend)
                if next_point==0:
                    continue
                
                thin[next_point[0]][next_point[1]][next_point[2]] = 1
                liste_branchend = liste_branchend.tolist()
                liste_branchend.insert(0, next_point)
                liste_branchend = numpy.asarray(liste_branchend)
    return thin          
      
def branch_extension( thin, vessel, initiale_richtung, liste_branchend):
    
    last_point = liste_branchend[0]
    vorgaenger = liste_branchend[1]
    value = 0
    next_point=0                   
    for i in range(-1,2):
        for j in range(-1,2):
            for k in range(-1,2):
                if not(i==0 and j==0 and k==0):
                    potential_punkt = (last_point[0]+i, last_point[1]+j, last_point[2]+k)
                    vector_last_point_and_potential_punkt = calc_direction(last_point, potential_punkt)
                
                    if value <= vessel[potential_punkt[0]][potential_punkt[1]][potential_punkt[2]]\
                    and not check_ob_nachbar(potential_punkt,vorgaenger)\
                    and 61 >= calc_angle(initiale_richtung, vector_last_point_and_potential_punkt):
                        if number_of_neighbors(thin,potential_punkt,1) < 1 :
                            
                            value = vessel[last_point[0]+i][last_point[1]+j][last_point[2]+k]
                            next_point = (last_point[0]+i, last_point[1]+j, last_point[2]+k)
    
    return next_point

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

def dist(x,y,pixel_spacing):
    pixel_spacing = numpy.asarray(pixel_spacing)
    x = x*pixel_spacing
    y = y*pixel_spacing    
       
    return numpy.sqrt(numpy.sum((x-y)**2))

def calc_angle(vector1, vector2):
    x_mod = numpy.sqrt((vector1*vector1).sum())
    y_mod = numpy.sqrt((vector2*vector2).sum())
    

    cos_angle = numpy.dot(vector1, vector2) / x_mod / y_mod 
    
    if cos_angle > 1:
        cos_angle = 1
    if cos_angle < -1:
        cos_angle = -1
    
    angle = numpy.arccos(cos_angle) 

    return angle * 360 / 2 / numpy.pi

def check_ob_nachbar(point1, point2):
    max_value = numpy.max([point1[0]-point2[0], point1[1]-point2[1] , point1[2]-point2[2]])
    min_value = numpy.min([point1[0]-point2[0], point1[1]-point2[1] , point1[2]-point2[2]]) 
    
    if max_value >= 2 or min_value <=-2:
        return False
    else:
        return True
   
def gradient_branch(thin, value, number_of_points, seg, brainmask, voxelspacing, occlusionpoint=0):
    endpoints_of_branches = numpy.nonzero(1 == count_neighbor(thin ,numpy.ones((3,3,3)))) #alle Endpunkte ermitteln

    alle_vesselness_aufsummiert = 0
    gesamtanzahl_der_punkte = 0
    
    
    occlusion_image = numpy.zeros(thin.shape)
    speicher=[]
    
    #calculating skin of mask
    maskskin=count_neighbor(brainmask, numpy.ones((3,3,3)))
    maskskin[maskskin>=26]=0
    maskskin[maskskin>=1]=1
    
    for tmp1 in range(numpy.size(endpoints_of_branches[0])):

        point = (endpoints_of_branches[0][tmp1],endpoints_of_branches[1][tmp1],endpoints_of_branches[2][tmp1])
        
        branch_points = last_n_points_of_branch(thin , point, number_of_points) #alle Astpunkte vom Ende bis maximale Anzahl oder bis inklusive Kreuzpunkt
        branch_values = return_value(branch_points,value)
        
        gra = numpy.diff(branch_values)
        speicher.append(max(gra))

       
        
        if occlusionpoint in branch_points.tolist():
            print 'Occlusionpoints'
            print branch_values
       
       
        if not check_border(branch_points[0], thin): #wenn am Rand des Bildes die Punkte liegen, dann soll nicht weiter gerechnet werden
            continue

        alle_vesselness_aufsummiert += numpy.sum(branch_values)
        gesamtanzahl_der_punkte += len(branch_values)
        #print numpy.sum(branch_values)
    durchschnittliche_vesselness = alle_vesselness_aufsummiert/gesamtanzahl_der_punkte #Problem?: hier werden auch die Vesselwerte ausserhalb der Arterie beruecksichtigt
    
    #print ''
    schwellwert=numpy.mean(speicher)
    print 'meangra: {}'.format(numpy.mean(speicher))
    print 'Anzahl vorher: {}'.format(numpy.size(endpoints_of_branches[0]))
    #print 'Durchschnittliche Vesselness aller Endbranches ohne Randkandidaten {}'.format( durchschnittliche_vesselness )
    #print ''
    ######################################
    a=0
    b=0
    c=0
    d=0
    m=0
    high_ves=0

    liste_mean_values=[]    

    for tmp2 in range(numpy.size(endpoints_of_branches[0])):

        point = (endpoints_of_branches[0][tmp2],endpoints_of_branches[1][tmp2],endpoints_of_branches[2][tmp2])
    
        branch_points = last_n_points_of_branch(thin , point, number_of_points) #alle Astpunkte vom Ende bis maximale Anzahl oder bis inklusive Kreuzpunkt
        branch_values = return_value(branch_points,value)
        
      
        liste_mean_values.append(numpy.mean(branch_values))
        
        
        #check if point in mask
        if not check_border(branch_points[0], thin):
            continue
        
        
        if not check_inside_mask(branch_points,brainmask):
            continue
        
        
        distance = 2
        if not check_distance_mask(branch_points[0], maskskin, voxelspacing, distance):
            continue
        
        

        
        #Gradientbestimmung
        if len(branch_values) <= 11:
            print ''
            print len(branch_values)
            print branch_points[0]
            print ''
            continue        
        
        insidevalues=(branch_values[-1]+branch_values[-2]+branch_values[-3]+branch_values[-4]+branch_values[-5]+branch_values[-6])/6
        outsidevalues=(branch_values[0]+branch_values[1])/2
        differ = insidevalues - outsidevalues

        
        gra = numpy.diff(branch_values)

        #gra=numpy.delete(gra,-1)
        #gra=numpy.delete(gra,-1)
        
        if outsidevalues <= insidevalues*0.3 \
            and durchschnittliche_vesselness*2/3.<= numpy.mean(branch_values) \
            and max(gra)>=3/2.*schwellwert \
            and check_durchmesser(seg,branch_points[-1]):
            #and min(gra)>-15:
            arg=branch_points[0]
            occlusion_image[arg[0]-3:arg[0]+4,arg[1]-3:arg[1]+4,arg[2]-3:arg[2]+4]=1
            
            if occlusionpoint in branch_points.tolist():
                print '#######'
                print 'Occlusion'
                print '#######'
            
            print branch_points[0]
            print branch_values
            
            d=d+1
    
    
    print 'Anzahl Okklusionskandidaten: {}'.format(d)
    print''
    return occlusion_image
    #print punktr
    #print high_ves
    
    #liste_branches=[]
     

        ############
        
    '''
    c=0
    for tmp in range(0,numpy.size(endpoints_of_branches[0])):
        point = (endpoints_of_branches[0][tmp],endpoints_of_branches[1][tmp],endpoints_of_branches[2][tmp])
        branch_points = last_n_points_of_branch(thin , point, number_of_points)
        branch_values = return_value(branch_points,value)

        if (126, 167, 74) in branch_points:
            print 'Occlusionpoints'
            print return_value(branch_points,value)
            print numpy.mean(return_value(branch_points,value))
 
        #Gradientbestimmung

        
        if check_border(branch_points[0], thin):
            
            if numpy.mean(branch_values) >= 0.7*numpy.mean(liste_mean_values2):
                
                branch_values = numpy.asarray(branch_values)
                gra = numpy.diff(branch_values)
                #print 'Gradient: {}'.format(gra)
                #print 'Points: {}'.format(branch_points)
                c=c+1

    print c
       '''
def check_durchmesser(seg, point):
    if 26 <= number_of_neighbors(seg,point,1): #bei 26 werden in den ersten Datensaetzen die Okklusionen nicht erkannt
        return True
    else:    
        return False
    
def check_inside_mask(branchpoints, mask):
    'Returns False, if points of branch are not inside mask'
    for i in range(0,len(branchpoints)):
        if not 1 <= mask[branchpoints[i][0]][branchpoints[i][1]][branchpoints[i][2]]:
            return False
    return True

def check_distance_mask(branch_point, brainmask, voxelspacing, distance):
    #Kantenlaenge des Kastens um die Branchpoints
    box = 4
    
    image = numpy.zeros(brainmask.shape)
    imagepoint = numpy.zeros(brainmask.shape)
    imagepoint[branch_point[0]][branch_point[1]][branch_point[2]] = 1
    
    for i in range(max(0, branch_point[0]-box), min(brainmask.shape[0] - 1, branch_point[0]+box+1)):
        for j in range(max(0, branch_point[1]-box), min(brainmask.shape[1] - 1, branch_point[1]+box+1)):
            for k in range(max(0, branch_point[2]-box), min(brainmask.shape[2] - 1, branch_point[2]+box+1)):
                image[i][j][k] = 1
                    
    image2 = image * brainmask

    if 0 == numpy.max(image2):
        return True
    

    if __surface_distances(imagepoint, image2, voxelspacing, 1).min() >= distance:      
        #Weiterhin Okklusionskadidat
        return True
    
    else:
        #Zu dicht am Rand, kein Okklusionskadidat
        print 'Zu dicht am Maskenrand'
        print branch_point
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
 
def calc_direction(point1, point2):
    point1=numpy.asarray(point1)
    point2=numpy.asarray(point2)
    return point2 - point1 
   
def check_border(point, image):
    if numpy.min(point) <= 4 or point[0]>=image.shape[0]-5 or point[1]>=image.shape[1]-5 or point[2]>=image.shape[2]-5 :
        #outside image or on the border of the image
        return False
    else:
        #inside image
        return True

def count_neighbor(image, structure):
    image = image.astype(numpy.bool)
    sumimage = sum_filter(image, footprint = structure, mode="constant", cval=0.0, output=numpy.uint)
    sumimage[~image] = 0
    return sumimage - image

def largest_connected_component(image, structure):
    'returns image with the largest connected components, labeled with 1'
    
    image, liste = label(image,structure)
    hist = histogram( image, 1, numpy.max(image), numpy.max(image) )
    
    return_image = numpy.zeros(image.shape, image.dtype)
    
    return_image[ image == 1 + numpy.where( hist == hist.max() )[0][0] ] = 1
    
    return return_image

def largest_n_components(cen, n):
    return_image = numpy.zeros(cen.shape, numpy.bool) 
    for i in range(n):
        cen, cen_label = label(cen, numpy.ones((3,3,3)))
        hist = histogram( cen, 1, numpy.max(cen),numpy.max(cen))
        return_image[cen == 1 + numpy.where( hist == hist.max() )[0][0]] = 1
        cen[cen == 1 + numpy.where( hist == hist.max() )[0][0]] = 0
    return return_image

def last_n_points_of_branch(thinned_image,branch_endpoint,length):
    'returns a list with the last points of a branch (maximal as long as length, inclusive intersection point), needed input: thinned image and last branchpoint' 
    pointlist=[branch_endpoint]
    tmp_point=branch_endpoint
    
    for i in range(0,length-1):
        tmp_neighbor = return_neighbor(thinned_image, tmp_point, 1)
        if 2 == tmp_neighbor.__len__() or 1 == tmp_neighbor.__len__() :
            if tmp_neighbor[0] not in pointlist:
                pointlist.append(tmp_neighbor[0])
                tmp_point=tmp_neighbor[0]
            elif 1 < tmp_neighbor.__len__():
                pointlist.append(tmp_neighbor[1])
                tmp_point=tmp_neighbor[1]
            else:
                return numpy.asarray(pointlist)
        else:
            return numpy.asarray(pointlist)
    return numpy.asarray(pointlist)

def return_neighbor(image, point, width):
#returns a list with points of surrounding, excluding the original point
    if not width:
        return 0
    else:
        liste = []
        for i in range(-width, width+1):
            for j in range(-width, width+1):
                for k in range(-width, width+1):
                    if check_inside( image, [point[0]+i,point[1]+j,point[2]+k])\
                    and image[point[0]+i,point[1]+j,point[2]+k]\
                    and not (i==0 and j==0 and k==0):
                        liste.append((point[0]+i,point[1]+j,point[2]+k))
    return liste

def return_value(listed_points, value_image):
    
    value_list = []
    for i in range(0,listed_points.__len__()):
        point = listed_points[i]
        value_list.append( pylab.round_( value_image[ point[0] ][ point[1] ][ point[2] ] ) )
    return value_list        

def remove_short_branch_vesselness(thinned_image, vesselness, branches_shorter_than):
    #ueberpruefung der centerline auf datentyp
    if thinned_image.max != 1 or thinned_image.dtype == numpy.bool: 
        thinned_image = numpy.asarray(thinned_image, dtype=numpy.bool)
        thinned_image = numpy.asarray(thinned_image, dtype=numpy.int)


    thinned_image2 = deepcopy(thinned_image)
    #Bild mit Anzahl der Nachbarpunkte
    image_neighbor = count_neighbor( thinned_image, numpy.ones((3,3,3)) )

    #Liste alles Punkte, die eine Abzweigung beinhalten
    kreuzungspunkte = numpy.nonzero( image_neighbor >= 3 )
    
    #ueber alle kreuzungspunkte iterieren
    for iterate_branches in range(0,numpy.size(kreuzungspunkte,1)): 
        temp_kreuzungspunkt = ( kreuzungspunkte[0][iterate_branches] , kreuzungspunkte[1][iterate_branches] , kreuzungspunkte[2][iterate_branches])
        #Liste die die einzelnen, abzwigenden Arme beinhaltet
        gelistete_seitenarme = return_short_branches( thinned_image , image_neighbor , temp_kreuzungspunkt , 4*branches_shorter_than )

        #ueber die moeglichen Seitenarme iterieren
        for temp_seitenarme in range(0, len( gelistete_seitenarme ) ):
            #wenn die Minimallaenge unterschritten wird, dann wird auf jeden fall geloescht
            if len( gelistete_seitenarme [ temp_seitenarme ]) <= branches_shorter_than:
                for number_of_branchpoints in range(0, len( gelistete_seitenarme [ temp_seitenarme ] )):
                    thinned_image2[ gelistete_seitenarme [ temp_seitenarme ][ number_of_branchpoints ] ] = 0
            #sonst ueberpruefe die Vesselness vom Seitenarme und den anderen Armen, die vom gleichen Kreuzungspunkt ausgehen
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

                if ((not vesselvalue2 == 0) and vesselvalue2*(1/2.) >= vesselvalue1):
                    #print 'ES WIRD GELOESCHTTTTTT'
                    #print list_branch_points [ number_of_branches ]
                    if (296,168,42) in gelistete_seitenarme [ temp_seitenarme ]:
                        print 'es wird geloescht'
                    print 'es wird geloescht'
                    for number_of_branchpoints in range(0, len( gelistete_seitenarme [ temp_seitenarme ] )):
                        thinned_image2[ gelistete_seitenarme [ temp_seitenarme ][ number_of_branchpoints ] ] = 0
                
    return thinned_image2


def remove_short_branch(thinned_image, branches_shorter_than):
    
    if thinned_image.max != 1 or thinned_image.dtype == numpy.bool: 
        thinned_image = numpy.asarray(thinned_image, dtype=numpy.bool)
        thinned_image = numpy.asarray(thinned_image, dtype=numpy.int)
    
    image_neighbor = count_neighbor( thinned_image, numpy.ones((3,3,3)) )

    branch_points = numpy.nonzero( image_neighbor >= 3 )
  
    for iterate_branches in range(0,numpy.size(branch_points,1)): #ueber alle kreuzungspunkte iterieren
        temp_branch_point = ( branch_points[0][iterate_branches] , branch_points[1][iterate_branches] , branch_points[2][iterate_branches])
        list_branch_points = return_short_branches( thinned_image , image_neighbor , temp_branch_point , branches_shorter_than )
        
        for number_of_branches in range(0, len( list_branch_points ) ): #Punkte loeschen
            for number_of_branchpoints in range(0, len( list_branch_points [ number_of_branches ] )):
                thinned_image[ list_branch_points [ number_of_branches ][ number_of_branchpoints ] ] = 0
                
    return thinned_image

def return_short_branches(thinned_image, image_neighbor, branch_point, max_branch_length):
    '''
    gibt eine Liste zurueck, die mehrere Listen mit den jeweiligen Astpunkten beinhaltet, die hoechstens so lang wie max_branch_length sind
    '''
    next_neighbors = return_neighbor(thinned_image, branch_point, 1)
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
        
def give_branch(thinned_image, image_neighbor, list_point, next_point, max_branch_length):
    
    list_point.append(next_point)
        
    if(1 == max_branch_length):
        #wenn keine Schritte mehr, dann wird Suche beendet
        list_point.pop(0)
        return list_point
           
    else:
        if(2 == image_neighbor[next_point]):#wenn nur zwei nachbarn, dann ist alles gut und es geht los
        
            nachbarn = return_neighbor(thinned_image, next_point, 1)
            
            
            if(nachbarn[0] not in list_point):
                return give_branch(thinned_image, image_neighbor, list_point, nachbarn[0], max_branch_length-1)
                  
            elif(nachbarn[1] not in list_point):
                return give_branch(thinned_image, image_neighbor, list_point, nachbarn[1], max_branch_length-1)
            
            else:
                #Ring detektiert, oder?!
                return
    
        else:
            list_point.pop(0)
            return list_point