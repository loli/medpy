'''
Created on Aug 25, 2014
@package medpy.occlusion.filters

@author: kleinfeld

@version 0.1.1
@since 2014-08-25
@status
'''


# build-in modules

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
    ##################################################
    counter=0
    ##################################################
    
    #Ermitteln aller Endpunkte der Centerline
    all_endboints = numpy.nonzero(1 == count_neighbor(labeled_cen ,numpy.ones((3,3,3))))
    
    return_image = numpy.zeros(labeled_cen.shape, numpy.bool) 
        
    return_cone_image = numpy.zeros(labeled_cen.shape, numpy.bool) 
    
    #Ueber alle Endpunkte iterieren 
    for tmp in range( numpy.size(all_endboints[0]) ):
        
        end_point = (all_endboints[0][tmp],all_endboints[1][tmp],all_endboints[2][tmp]) #aktuell zu bearbeitender Endpunkt
        end_point_speicher = end_point
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
        
        #Berechnung des Vesselschwellwertes
        
        schwellwert = return_value(list_of_branchpoints, vesselness_image)
        schwellwert = 0.3*numpy.mean(schwellwert)
        
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

            alle_punkte = []
            
            #suche den dichtesten Punkt
            for index1 in range(numpy.size(next_points[0])):
                alle_punkte.append((next_points[0][index1],next_points[1][index1],next_points[2][index1]))
            alle_punkte2=alle_punkte
            #FUNKTION SCHREIBEN solange wie punkte in nearest_point wird gesucht, jedoch nur solange, wie image_gapclosing_points ueberall null ist
            for index in alle_punkte2:
                end_point = end_point_speicher
                end_point = numpy.asarray(end_point)
                if 0 == len(alle_punkte2):
                    image_gapclosing_points = numpy.zeros(labeled_cen.shape, numpy.bool)
                    break                
                nearest_point = nearest_neigbor(end_point, alle_punkte2,pixel_spacing)
                
            
            #while schleife die solange laeuft bis einer der next_points erreicht wird und entlang der vesselness in eine bestimmte richtung geht
            #diese richtung wird aus dem zuletzt gesetzten punkt und dem Punkt (nearest_point) ermittelt
                image_gapclosing_points = numpy.zeros(labeled_cen.shape, numpy.bool) 
                
                while (not check_nachbar_list(end_point, alle_punkte)) and (not check_ob_nachbar(end_point,nearest_point)) :
              
                    #Berechnung des naechsten Punktes
                    
                    vesselness = 0
                    direction = calc_direction(end_point,nearest_point)
                    
                    for x in range(-1,2):
                        for y in range(-1,2):
                            for z in range(-1,2):
                                if not(0==x and 0==y and 0==z):
                                    
                                    next_possible_point = numpy.asarray((end_point[0]+x, end_point[1]+y, end_point[2]+z))
                                    if check_inside(vesselness_image, next_possible_point):
                                        if vesselness <= vesselness_image[next_possible_point[0]][next_possible_point[1]][next_possible_point[2]]:
                                            
                                            #print direction
                                            #print calc_direction(end_point, next_possible_point)
                                            
                                            if (direction == calc_direction(end_point, next_possible_point)).all() \
                                            or (direction == calc_direction(next_possible_point,end_point)).all() :
                                                vesselness = vesselness_image[next_possible_point[0]][next_possible_point[1]][next_possible_point[2]]
                                                set_point = next_possible_point
                                            elif 60 >= calc_angle( direction, calc_direction(end_point, next_possible_point) ):
                                                vesselness = vesselness_image[next_possible_point[0]][next_possible_point[1]][next_possible_point[2]]
                                                set_point = next_possible_point

             
                    #diese Zeile muss so sein... =) 
                    end_point = set_point                    
                   
                    #punkt setzten        
    
                    image_gapclosing_points[end_point[0]][end_point[1]][end_point[2]] = True
                
                #schwellwert_image = schwellwert_image | image_gapclosing_points
            
            #Vesselschwellwertkontrolle
                if image_gapclosing_points.max():#Absicherung, dass was in image_gapclosing_points auf TRUE ist
                    schwellwert_points = numpy.nonzero(image_gapclosing_points)
                    min_schwellwert = numpy.min(vesselness_image[schwellwert_points])
                
                    if min_schwellwert < schwellwert:
                        image_gapclosing_points = numpy.zeros(labeled_cen.shape, numpy.bool)
                        alle_punkte2.remove(nearest_point)
                        
                        #print 'zu kleiner Schwellwert: '
                        #print schwellwert_points
                        continue
                    else:
                        #print 'es wird gefuellt: '
                        zwischenspeicher[nearest_point[0]][nearest_point[1]][nearest_point[2]] = 1
                        #print schwellwert_points
                        
                        ##################################################
                        counter = counter+1
                        ##################################################
                        
                        break
                else:
                    image_gapclosing_points = numpy.zeros(labeled_cen.shape, numpy.bool)
                    alle_punkte2.remove(nearest_point)
                    #print 'Anderes esle'
                    continue
            return_image = return_image | image_gapclosing_points
            return_image = return_image | ori_cen
            
    return return_image, zwischenspeicher, counter

def check_nachbar_list(punkt, liste):
    for i in liste:
        if check_ob_nachbar(punkt, i):
            return True
    return False

def nearest_neigbor(end_point,alle_punkte,pixel_spacing):
    nearest_point = alle_punkte[0]
    for index in alle_punkte:        
        if dist(end_point,nearest_point,pixel_spacing) > dist(end_point,index,pixel_spacing):
            nearest_point = index
    return nearest_point
    
    
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
    #print num_features
    for i in range(1,num_features+1):
        labeled_array[ numpy.nonzero( temp == i )] = ( numpy.count_nonzero( temp == i ))
        #print counter
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
      
def branch_extension( thin, vessel, brainmask, initiale_richtung, liste_branchend):
    
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
                    
                    #if not brainmask[potential_punkt[0]][potential_punkt[1]][potential_punkt[2]]:
                    #    continue
                    if value <= vessel[potential_punkt[0]][potential_punkt[1]][potential_punkt[2]]\
                    and not check_ob_nachbar(potential_punkt,vorgaenger)\
                    and 60 >= calc_angle(initiale_richtung, vector_last_point_and_potential_punkt):
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
   
def gradient_branch(thin, value, number_of_points, seg, brainmask, voxelspacing, out2, occlusionpoint=0):
    endpoints_of_branches = numpy.nonzero(1 == count_neighbor(thin ,numpy.ones((3,3,3)))) #alle Endpunkte ermitteln
    
    f = open(str(out2)+'/Okklusion.txt','w')
    f.write(str(out2))
    f.write('\n')
    f.write('\n')
    f.write('Anzahl vorher: {}\n'.format(len(endpoints_of_branches[0])))
    f.write('\n')
    print 'Anzahl vorher: {}'.format(len(endpoints_of_branches[0]))
    
    liste_branch_values_innen = []
    liste_branch_values_aussen = []
    all_values_innen = []
    
    
    return_thin_for_extension = numpy.zeros(thin.shape)
    occlusion_image = numpy.zeros(thin.shape)
    
    all_max_gra=[]
    all_max_gra_with_points = []
    
    
    anzahl_gradient=0
    anzahl_median=0
    anzahl_mean=0
    anzahl_durchmesser=0
    
    lange=len(endpoints_of_branches[0])
    gradient_array = numpy.zeros(lange)
    median_array = numpy.zeros(lange)
    mean_array = numpy.zeros(lange)
    durchmesser_array = numpy.zeros(lange)
    
    
    
    #for tmp1 in range(3):
    for tmp1 in range(numpy.size(endpoints_of_branches[0])):
        #print tmp1
        
        tmp_point = (endpoints_of_branches[0][tmp1],endpoints_of_branches[1][tmp1],endpoints_of_branches[2][tmp1])

        
        
        #Suche der letzten "number_of_points" inneren Astpunkte
        bild_armpunkt = numpy.zeros(thin.shape)
        vergleichs_bild = numpy.zeros(thin.shape)
        bild_armpunkt[tmp_point[0]][tmp_point[1]][tmp_point[2]]=1

        while (number_of_points > numpy.count_nonzero(bild_armpunkt) and not (vergleichs_bild == bild_armpunkt).all()):
            vergleichs_bild = bild_armpunkt
            bild_armpunkt = binary_dilation(bild_armpunkt, structure=numpy.ones((3,3,3)), iterations=1, mask=thin)

        #print 'Anzahl der inneren Astpunkte: {}'.format(numpy.count_nonzero(bild_armpunkt))
        
        branch_values_innen = (value[numpy.nonzero(bild_armpunkt)] )
        liste_branch_values_innen.append(tmp_point)
        liste_branch_values_innen.append(branch_values_innen) #Alle Vesselwerte mit zugehoerigem Punkt davor
        all_values_innen.extend(branch_values_innen) #Alle Vesselwerte ueber alle inneren Voxelpunkte
        
        #Verlaengerung des Arms um number_of_points
        liste_branchend = last_n_points_of_branch(thin , tmp_point, number_of_points) #alle Astpunkte vom Ende bis maximale Anzahl oder bis inklusive Kreuzpunkt

        
        laenge_vorher = len(liste_branchend) #Laenge des Armes vor der Extention
        thin_for_extension = deepcopy(thin)

            
        if 2 <= len(liste_branchend):
            initiale_richtung = calc_direction(liste_branchend[1], liste_branchend[0]) 
        
            for i in range(0,2*number_of_points):
       

                if not check_border(liste_branchend[0], thin):
                    #print 'check border'
                    #print 'Randpunkt: {}'.format(liste_branchend[0])
                    break
                
                
                next_point = branch_extension(thin_for_extension, value,brainmask, initiale_richtung,liste_branchend)
                if next_point==0:
                    break
                
                thin_for_extension[next_point[0]][next_point[1]][next_point[2]] = 1
                liste_branchend = liste_branchend.tolist()
                liste_branchend.insert(0, next_point)
                liste_branchend = numpy.asarray(liste_branchend)
        return_thin_for_extension = return_thin_for_extension + thin_for_extension
        zwischenspeicher=[]
        if 0 < len(liste_branchend)-laenge_vorher: #wenn es eine Verlaengerung gab, sonst wenn keine Verlaengerung moeglich, dann keine weitere Betrachtung
            liste_branch_values_aussen.append(tmp_point)
            branch_values = return_value(liste_branchend,value)
            for index1 in range (0,len(liste_branchend)-laenge_vorher):
                zwischenspeicher.append(branch_values[index1])
            liste_branch_values_aussen.append(zwischenspeicher)
            
            

            gra = numpy.diff(branch_values)
            all_max_gra.append(max(gra))
        
            all_max_gra_with_points.append(tmp_point)
            all_max_gra_with_points.append([max(gra),-1,-1])

        
        
    d=0

    mean_all_values_innen = numpy.mean(all_values_innen)   
    mean_gra = numpy.mean(all_max_gra)
    
    
    
    #for tmp2 in range(3):
    for tmp2 in range(numpy.size(endpoints_of_branches[0])):
        

        tmp_point = (endpoints_of_branches[0][tmp2],endpoints_of_branches[1][tmp2],endpoints_of_branches[2][tmp2])
        
        
        if 1 == liste_branch_values_innen.count(tmp_point):
            point_index1 = liste_branch_values_innen.index(tmp_point)
            insidevalues= liste_branch_values_innen[point_index1 + 1]
            
        else:
            continue
        
        if 1 == liste_branch_values_aussen.count(tmp_point):
            point_index2 = liste_branch_values_aussen.index(tmp_point)
            outsidevalues = liste_branch_values_aussen[point_index2 + 1]
            
        else:
            #print 'Fehler aussen: {}'.format(tmp_point)
            #print liste_branch_values_aussen.count(tmp_point)
            continue
        

        if 1 == all_max_gra_with_points.count(tmp_point):
            point_index3 = all_max_gra_with_points.index(tmp_point)
            tmp_max_gra = all_max_gra_with_points[point_index3 + 1]
            tmp_max_gra = tmp_max_gra[0]
             
        else:
            continue
        
        #############################################################
        if numpy.median(outsidevalues) <= numpy.median(insidevalues)*0.3:
            anzahl_median=anzahl_median+1
            median_array[tmp2]=1
            
        if mean_all_values_innen <= numpy.mean(insidevalues):      
            anzahl_mean=anzahl_mean+1
            mean_array[tmp2]=1
            
        if tmp_max_gra >= mean_gra:
            anzahl_gradient=anzahl_gradient+1
            gradient_array[tmp2]=1
            
        branch_points = last_n_points_of_branch(thin , tmp_point, number_of_points)
        zaehler = 0
        cou=0.0
        
        if len(branch_points)>=2:
            for index5 in range(0,len(branch_points)-1):
                zaehler = zaehler + checkrechtwinkel(branch_points[index5+1],branch_points[index5], seg,2)     #   continue
                cou=cou+1.0
        else:
            print 'len low'       
        if cou > 0.0:
            zaehler=zaehler/cou
        else:
            print 'counter low'
        if zaehler < 4.0:
            anzahl_durchmesser=anzahl_durchmesser+1
            durchmesser_array[tmp2]=1
            
        if numpy.median(outsidevalues) <= numpy.median(insidevalues)*0.3 \
            and mean_all_values_innen <= numpy.mean(insidevalues) \
            and tmp_max_gra >= mean_gra:
            

            if zaehler < 4.0:
                continue
            #and mean_all_values_innen*2/3.<= numpy.mean(insidevalues) 
            #and check_durchmesser(seg,branch_points[-1]):
            #and min(gra)>-15:
        

            

            #else: 
            
            #    continue
            
           
            #MARKIERUNG DER OKKLUSION
            tempocc = numpy.zeros(occlusion_image.shape)
            for bpoin in last_n_points_of_branch(thin , tmp_point, 20):
                tempocc[bpoin[0]][bpoin[1]][bpoin[2]]=1
            tempocc = binary_dilation(tempocc, iterations=5, mask=seg)
            
            occlusion_image[tempocc >= 1] = 1

            #if occlusionpoint in branch_points.tolist():
            #    print '#######'
            #    print 'Occlusion'
            #    print '#######'
                
            
            
            print 'Okklusion bei: {}'.format(tmp_point)
                        
            print 'numpy.median(outsidevalues): {}'.format(numpy.median(outsidevalues))
            print 'numpy.median(insidevalues)*0.2: {}'.format(numpy.median(insidevalues)*0.2)
            
            print 'mean_all_values_innen: {}'.format(mean_all_values_innen)
            print 'numpy.mean(insidevalues): {}'.format(numpy.mean(insidevalues))
            
            print 'tmp_max_gra: {}'.format(tmp_max_gra)
            print '1.0*mean_gra: {}'.format(mean_gra)
            
            
            print 'zaehler: {}'.format(zaehler)
            print ''
            
            f.write('outsidevalues: {}\n'.format(outsidevalues))
            f.write('insidevalues: {}\n'.format(insidevalues))
            
            
            f.write('Okklusion bei: {}\n'.format(tmp_point))
            f.write('numpy.median(outsidevalues): {}\n'.format(numpy.median(outsidevalues)))
            f.write('numpy.median(insidevalues)*0.3: {}\n'.format(numpy.median(insidevalues)*0.3))
            f.write('mean_all_values_innen: {}\n'.format(mean_all_values_innen))
            f.write('numpy.mean(insidevalues): {}\n'.format(numpy.mean(insidevalues)))
            f.write('tmp_max_gra: {}\n'.format(tmp_max_gra))
            f.write('mean_gra: {}\n'.format(mean_gra))
            f.write('Nachbarschaftsdurchschnitt: {}\n'.format(zaehler))
            f.write(' \n')
            
            
            d=d+1
        else:
            kgfd=0
            #print 'sonst {} Points: {}'.format(stage, branch_points[0])
    
    print 'Anzahl Okklusionskandidaten: {}'.format(d)
    print''
    f.write('Anzahl Okklusionskandidaten: {}\n'.format(d))
    print 'Anzahl vorher: {}\n'.format(len(endpoints_of_branches[0]))
    print 'Anzahl der Okklusionen durch Gradienten: {}\n'.format(anzahl_gradient)
    print 'Anzahl der Okklusionen durch Median: {}\n'.format(anzahl_median)
    print 'Anzahl der Okklusionen durch Mean: {}\n'.format(anzahl_mean)
    print 'Anzahl der Geloeschten durch Durchmesser: {}\n'.format(anzahl_durchmesser)
    
    f.write('Anzahl vorher: {}\n'.format(len(endpoints_of_branches[0])))
    f.write('Anzahl der Okklusionen durch Gradienten: {}\n'.format(anzahl_gradient))
    f.write('Anzahl der Okklusionen durch Median: {}\n'.format(anzahl_median))
    f.write('Anzahl der Okklusionen durch Mean: {}\n'.format(anzahl_mean))
    f.write('Anzahl der Geloeschten durch Durchmesser: {}\n'.format(anzahl_durchmesser))
    
    f.close()
    
    numpy.save(str(out2)+'/01_gradient.npy', gradient_array)
    numpy.save(str(out2)+'/02_median.npy', median_array)
    numpy.save(str(out2)+'/03_mean.npy', mean_array)
    numpy.save(str(out2)+'/04_durchmesser.npy', durchmesser_array)
    
    return occlusion_image,return_thin_for_extension
     
       
def check_durchmesser(seg, point):
    if 19 <= number_of_neighbors(seg,point,1): #bei 26 werden in den ersten Datensaetzen die Okklusionen nicht erkannt
        return True
    else:    
        return False

def checkrechtwinkel(point1,point2,seg,iterations):
    x = numpy.array(point1)
    y = numpy.array(point2)
    
    vektor = y-x

    vektoren=[]
    if not (numpy.asarray(numpy.cross(vektor, [1,0,0])) == [0, 0, 0]).all():
        vektoren.append(numpy.cross(vektor, [1,0,0]))
        vektoren.append(numpy.cross([1,0,0],vektor))
    elif not (numpy.asarray(numpy.cross(vektor, [0,1,0])) == [0, 0, 0]).all():
        vektoren.append(numpy.cross(vektor, [0,1,0]))
        vektoren.append(numpy.cross([0,1,0],vektor))
    else:
        vektoren.append(numpy.cross(vektor, [0,0,1]))
        vektoren.append(numpy.cross([0,0,1],vektor))
    
    vektoren.append(numpy.cross(vektor, vektoren[0]))
    vektoren.append(numpy.cross(vektoren[0],vektor))
    
    counter=0
    for itera in range(1,iterations+1):
        for i in vektoren:
            point=point1+(i*itera)
            if check_inside(seg, point) and seg[point[0]][point[1]][point[2]]:
                counter+=1

    return counter
    
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
        #print 'Zu dicht am Maskenrand'
        #print branch_point
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
        value_list.append(( value_image[ point[0] ][ point[1] ][ point[2] ] ) )
    return value_list        

def remove_short_branch_vesselness(thinned_image, vesselness, branches_shorter_than):
    #ueberpruefung der centerline auf datentyp
    
    unter4=0
    unter10=0
    
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
        gelistete_seitenarme = return_short_branches( thinned_image , image_neighbor , temp_kreuzungspunkt , 10 )

        #ueber die moeglichen Seitenarme iterieren

        for temp_seitenarme in range(0, len( gelistete_seitenarme ) ):
            #wenn die Minimallaenge unterschritten wird, dann wird auf jeden fall geloescht
            if len( gelistete_seitenarme [ temp_seitenarme ]) <= branches_shorter_than:
                unter4=unter4+1
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

                if ((not vesselvalue2 == 0) and (vesselvalue2*(0.3) >= vesselvalue1)):
                    #print 'ES WIRD GELOESCHTTTTTT'
                    #print list_branch_points [ number_of_branches ]
                    unter10=unter10+1
                    
                    for number_of_branchpoints in range(0, len( gelistete_seitenarme [ temp_seitenarme ] )):
                        thinned_image2[ gelistete_seitenarme [ temp_seitenarme ][ number_of_branchpoints ] ] = 0
                
    return thinned_image2, unter4, unter10


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