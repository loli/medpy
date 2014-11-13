# DEVELOPMENT PUT ON HOLD
# The results obtained with a full WS are not that good, the reduced map neither
# Implementing a k-region watershed from this turned out more complicated that originally anticipated

import logging

import scipy
from nibabel.loadsave import load, save

from medpy.core import Logger
from medpy.utilities.nibabel import image_like

def main():
    # prepare logger
    logger = Logger.getInstance()
    logger.setLevel(logging.DEBUG)
    
    # input image locations
    #i = '/home/omaier/Experiments/Regionsegmentation/Evaluation_Viscous/00originalvolumes/o09.nii' # original image
    #i = '/home/omaier/Temp/test.nii' # original image
    #i = '/home/omaier/Temp/o09_smoothed_i4.0_c0.1_t0.0625.nii'
    i = '/home/omaier/Experiments/GraphCut/BoundaryTerm/Stawiaski/01gradient/o09_gradient.nii'
    
    # output image locations
    r = '/home/omaier/Temp/result_gradient.nii' # result mask
    
    # load images
    i_i = load(i)
 
    # extract and prepare image data
    i_d = scipy.squeeze(i_i.get_data())
    
    # crop input images to achieve faster execution
    crop = [slice(50, -200),
            slice(50, -150),
            slice(50, -100)]
    #i_d = i_d[crop]   
    
    i_d = scipy.copy(i_d)
    
    # !TODO: Test if input image is of size 0
    
    logger.debug('input image shape={},ndims={},dtype={}'.format(i_d.shape, i_d.ndim, i_d.dtype))

    result = watershed8(i_d, logger)

    logger.info('Saving resulting region map...')
    result_i = image_like(result, i_i)
    result_i.get_header().set_data_dtype(scipy.int32)
    save(result_i, r)

    logger.info('Done!')

def watershed8(i_d, logger):
    # compute neighbours
    logger.info('Computing differences / edges...')
    #nbs = compute_neighbours_max_border(i_d)
    nbs = compute_neighbours_max_border_gradient(i_d)
    
        # compute min altitude map
    logger.info('Computing minimal altitude map...')
    minaltitude = nbs[0]
    for nb in nbs[1:]:
        minaltitude = scipy.minimum(minaltitude, nb)
    
    logger.info('Prepare neighbours list...')
    neighbours = [[[set() for _ in range(i_d.shape[2])] for _ in range(i_d.shape[1])] for _ in range(i_d.shape[0])]
        
    # compute relevant neighbours
    def test(x, y, z, shape):
        if x<0: print("x<0", x, y, z)
        if y<0: print("y<0", x, y, z)
        if z<0: print("z<0", x, y, z)
        if x >= shape[0]: print("x>={}".format(shape[0]), x, y, z)
        if y >= shape[1]: print("y>={}".format(shape[1]), x, y, z)
        if z >= shape[2]: print("z>={}".format(shape[2]), x, y, z)
    
    logger.info('Computing relevant neighbours through masks...')
    # down (x-1) # up (x+1) # left (y-1) # right (y+1) # into (z-1) # out (z+1)
    offsets = ((-1,0,0), (1,0,0), (0,-1,0), (0,1,0), (0,0,-1), (0,0,1)) 
    for nb, (xo, yo, zo) in zip(nbs, offsets):
        for x, y, z in scipy.transpose(scipy.nonzero(nb == minaltitude)):
            #test(x+xo,y+yo,z+zo,nb.shape)
            neighbours[x][y][z].add((x+xo,y+yo,z+zo))
    
    c = [0,0,0,0,0,0]
    for x in range(minaltitude.shape[0]):
        for y in range(minaltitude.shape[1]):
            for z in range(minaltitude.shape[2]):
                c[len(neighbours[x][y][z]) - 1] += 1
    print("Distribution of relevant neighbours (1,2,3,4,5,6):", c)
                  
                
    # watershed
    logger.info('Watershed \w minaltitude and relevant neighbours as list pre-computation...')
    result = scipy.zeros(i_d.shape, dtype=scipy.int_)
    nb_labs = 0
    for x in range(result.shape[0]):
        for y in range(result.shape[1]):
            for z in range(result.shape[2]):
                if result[x,y,z] == 0:
                    L, lab = stream_neighbours2_set(i_d, result, minaltitude, neighbours, (x, y, z))
                    if -1 == lab:
                        nb_labs += 1
                        for p in L:
                            result[p] = nb_labs
                    else:
                        for p in L: 
                            result[p] = lab
                        
    return result

def watershed7(i_d, logger):
    # compute neighbours
    logger.info('Computing differences / edges...')
    nbs = compute_neighbours_max_border(i_d)
    
        # compute min altitude map
    logger.info('Computing minimal altitude map...')
    minaltitude = nbs[0]
    for nb in nbs[1:]:
        minaltitude = scipy.minimum(minaltitude, nb)
    
    logger.info('Prepare neighbours list...')
    neighbours = [[[[] for _ in range(i_d.shape[2])] for _ in range(i_d.shape[1])] for _ in range(i_d.shape[0])]
        
    # compute relevant neighbours
    logger.info('Computing relevant neighbours...')
    for i, min_value in scipy.ndenumerate(minaltitude):
        nbs_idx = get_nbs_idx3(i) # do not care about borders, their value is set to max
        for idx, nb in nbs_idx:
            if nbs[idx][i] == min_value:
                neighbours[i[0]][i[1]][i[2]].append(nb)
                
    # watershed
    logger.info('Watershed \w minaltitude and relevant neighbours as list pre-computation...')
    result = scipy.zeros(i_d.shape, dtype=scipy.uint32)
    nb_labs = 0
    for x in range(result.shape[0]):
        for y in range(result.shape[1]):
            for z in range(result.shape[2]):
                if result[x,y,z] == 0:
                    L, lab = stream_neighbours3_set(i_d, result, minaltitude, neighbours, (x, y, z))
                    if -1 == lab:
                        nb_labs += 1
                        for p in L:
                            result[p] = nb_labs
                    else:
                        for p in L: 
                            result[p] = lab
                        
    return result

def watershed6(i_d, logger):
    # compute neighbours
    logger.info('Computing differences / edges...')
    nbs = compute_neighbours_max_border(i_d)
    
        # compute min altitude map
    logger.info('Computing minimal altitude map...')
    minaltitude = nbs[0]
    for nb in nbs[1:]:
        minaltitude = scipy.minimum(minaltitude, nb)
    
    logger.info('Prepare neighbours list...')
    neighbours = [[[set() for _ in range(i_d.shape[2])] for _ in range(i_d.shape[1])] for _ in range(i_d.shape[0])]
        
    # compute relevant neighbours
    logger.info('Computing relevant neighbours...')
    for i, min_value in scipy.ndenumerate(minaltitude):
        nbs_idx = get_nbs_idx3(i) # do not care about borders, their value is set to max
        for idx, nb in nbs_idx:
            if nbs[idx][i] == min_value:
                neighbours[i[0]][i[1]][i[2]].add(nb)
                
    # watershed
    logger.info('Watershed \w minaltitude and relevant neighbours as list pre-computation...')
    result = scipy.zeros(i_d.shape, dtype=scipy.int_)
    nb_labs = 0
    for x in range(result.shape[0]):
        for y in range(result.shape[1]):
            for z in range(result.shape[2]):
                if result[x,y,z] == 0:
                    L, lab = stream_neighbours2_set(i_d, result, minaltitude, neighbours, (x, y, z))
                    if -1 == lab:
                        nb_labs += 1
                        for p in L:
                            result[p] = nb_labs
                    else:
                        for p in L: 
                            result[p] = lab
                        
    return result

def watershed5(i_d, logger):
    # compute neighbourslocal_min = (filters.minimum_filter(arr, size=3)==arr)
    logger.info('Computing differences / edges...')
    nbs = compute_neighbours_max_border(i_d)
    
        # compute min altitude map
    logger.info('Computing minimal altitude map...')
    minaltitude = nbs[0]
    for nb in nbs[1:]:
        minaltitude = scipy.minimum(minaltitude, nb)
        
    logger.info('Swapping axes...')   
    nbs = scipy.swapaxes(nbs, 0, 1)
    nbs = scipy.swapaxes(nbs, 1, 2)
    nbs = scipy.swapaxes(nbs, 2, 3)
        
    # compute relevant neighbours
    logger.info('Computing relevant neighbours...')
    neighbours = []
    for x in range(i_d.shape[0]):
        x_list = []
        neighbours.append(x_list)
        nbs_x = nbs[x]
        for y in range(i_d.shape[1]):
            y_list = []
            x_list.append(y_list)
            nbs_y = nbs_x[y]
            for z in range(i_d.shape[2]):
                z_set = set()
                y_list.append(z_set)
                nbs_z = nbs_y[z]
                nbs_idx = get_nbs_idx3((x,y,z)) # do not care about borders, their value is set to max
                min_value = minaltitude[x, y, z]
                for idx, nb in nbs_idx:
                    if nbs_z[idx] == min_value:
                        z_set.add(nb)
                
    # watershed
    logger.info('Watershed \w minaltitude and relevant neighbours as list pre-computation...')
    result = scipy.zeros(i_d.shape, dtype=scipy.uint16)
    nb_labs = 0
    for x in range(result.shape[0]):
        for y in range(result.shape[1]):
            for z in range(result.shape[2]):
                if result[x,y,z] != 0: continue # 10%
                L, lab = stream_neighbours2_set(i_d, result, minaltitude, neighbours, (x, y, z)) # 90%
                if -1 == lab:
                    nb_labs += 1
                    for p in L:
                        result[p] = nb_labs
                else:
                    for p in L: 
                        result[p] = lab
                        
    return result

def watershed4(i_d, logger):
    # compute neighbours
    logger.info('Computing differences / edges...')
    nbs = compute_neighbours_max_border(i_d)
    
    # compute min altitude map
    logger.info('Computing minimal altitude map...')
    minaltitude = nbs[0]
    for nb in nbs[1:]:
        minaltitude = scipy.minimum(minaltitude, nb)
        
    # compute relevant neighbours
    logger.info('Computing relevant neighbours...')
    neighbours = []
    for x in range(0, i_d.shape[0]):
        x_list = []
        neighbours.append(x_list)
        for y in range(0, i_d.shape[1]):
            y_list = []
            x_list.append(y_list)
            for z in range(0, i_d.shape[2]):
                z_set = set()
                y_list.append(z_set)
                nbs_idx = get_nbs_idx3((x,y,z)) # do not care about borders, their value is set to max
                min_value = minaltitude[x, y, z]
                for nb_idx, nb in nbs_idx:
                    if nbs[nb_idx][x][y][z] == min_value:
                        z_set.add(nb)
                
    # watershed
    logger.info('Watershed \w minaltitude and relevant neighbours as list pre-computation...')
    result = scipy.zeros(i_d.shape, dtype=scipy.uint16)
    nb_labs = 0
    for x in range(result.shape[0]):
        for y in range(result.shape[1]):
            for z in range(result.shape[2]):
                if not 0 == result[x,y,z]: continue # 10%
                L, lab = stream_neighbours2_set(i_d, result, minaltitude, neighbours, (x, y, z)) # 90%
                if -1 == lab:
                    nb_labs += 1
                    for p in L:
                        result[p] = nb_labs
                else:
                    for p in L: 
                        result[p] = lab
                        
    return result

def stream_neighbours3_set(original, result, minaltitude, neighbours, x):
    l_pos = set((x,))
    l_neg = set((x,))
    while 0 != len(l_neg):
        y = l_neg.pop()
        y_nbs = set(neighbours[y[0]][y[1]][y[2]])
        y_nbs -= l_pos
        #y_min = minaltitude[y] # pre-querying makes no sense, as barley used
        for nb in y_nbs:
            # three choices
            if 0 != result[nb]:
                return l_pos, result[nb]
            elif minaltitude[nb] < minaltitude[y]:
                l_pos.add(nb)
                l_neg = set((nb,))
            else:
                l_pos.add(nb)
                l_neg.add(nb)
    return l_pos, -1

def stream_neighbours2_set(original, result, minaltitude, neighbours, x):
    l_pos = set((x,))
    l_neg = set((x,))
    while 0 != len(l_neg):
        y = l_neg.pop()
        y_nbs = neighbours[y[0]][y[1]][y[2]]
        y_nbs -= l_pos
        #y_min = minaltitude[y] # pre-querying makes no sense, as barley used
        for nb in y_nbs:
            # three choices
            if result[nb] != 0:
                return l_pos, result[nb]
            elif minaltitude[nb] < minaltitude[y]:
                l_pos.add(nb)
                l_neg = set((nb,))
            else:
                l_pos.add(nb)
                l_neg.add(nb)
    return l_pos, -1

def watershed3(i_d, logger):
    # compute neighbours
    logger.info('Computing differences / edges...')
    nbs = compute_neighbours(i_d)
    
    # compute min altitude map
    logger.info('Computing minimal altitude map...')
    minaltitude = nbs[0]
    for nb in nbs[1:]:
        minaltitude = scipy.minimum(minaltitude, nb)
        
    # compute relevant neighbours
    logger.info('Computing relevant neighbours...')
    neighbours = scipy.zeros((i_d.shape[0], i_d.shape[1], i_d.shape[2], 6, 3))
    for x in range(i_d.shape[0]):
        for y in range(i_d.shape[1]):
            for z in range(i_d.shape[2]):
                nbs_idx = get_nbs_idx2((x,y,z), i_d.shape)
                min_value = minaltitude[x, y, z]
                neighbours_slice = neighbours[x,y,z]
                i = 0
                for nb_idx, nb in nbs_idx:
                    if nbs[nb_idx][x][y][z] == min_value:
                        neighbours_slice[i] = nb
                        i += 1
                neighbours_slice[i] = (-1,-1,-1)
                
    # watershed
    logger.info('Watershed \w minaltitude and relevant neighbours pre-computation...')
    result = scipy.zeros(i_d.shape, dtype=scipy.uint16)
    nb_labs = 0
    for x in range(result.shape[0]):
        for y in range(result.shape[1]):
            for z in range(result.shape[2]):
                if not 0 == result[x,y,z]: continue # 10%
                L, lab = stream_neighbours_set(i_d, result, minaltitude, neighbours, (x, y, z)) # 90%
                if -1 == lab:
                    nb_labs += 1
                    for p in L:
                        result[p] = nb_labs
                else:
                    for p in L: 
                        result[p] = lab
                        
    return result           
             
def stream_neighbours_set(original, result, minaltitude, neighbours, x):
    l_pos = set((x,))
    l_neg = set((x,))
    while 0 != len(l_neg):
        y = l_neg.pop()
        y_nbs = set()
        for p in neighbours[y]:
            if p[0] == -1:
                break
            y_nbs.add(tuple(p))
        y_nbs -= l_pos
        #y_min = minaltitude[y] # pre-querying makes no sense, as barley used
        for nb in y_nbs: # use eventually sets here
            # three choices
            if 0 != result[nb]:
                return l_pos, result[nb]
            elif minaltitude[nb] < minaltitude[y]:
                l_pos.add(nb)
                l_neg = set((nb,))
            else:
                l_pos.add(nb)
                l_neg.add(nb)
    return l_pos, -1
           
def get_nbs_idx3(point):
    return (((0, (point[0] + 1, point[1], point[2]))),
            ((1, (point[0] - 1, point[1], point[2]))),
            ((2, (point[0], point[1] + 1, point[2]))),
            ((3, (point[0], point[1] - 1, point[2]))),
            ((4, (point[0], point[1], point[2] + 1))),
            ((5, (point[0], point[1], point[2] - 1))))
                    
def get_nbs_idx2(point, shape):
    ret = []
    if point[0] + 1 < shape[0]: ret.append((0, (point[0] + 1, point[1], point[2])))
    if point[0] - 1 > 0: ret.append((1, (point[0] - 1, point[1], point[2])))
    if point[1] + 1 < shape[1]: ret.append((2, (point[0], point[1] + 1, point[2])))
    if point[1] - 1 > 0: ret.append((3, (point[0], point[1] - 1, point[2])))
    if point[2] + 1 < shape[2]: ret.append((4, (point[0], point[1], point[2] + 1)))
    if point[2] - 1 > 0: ret.append((5, (point[0], point[1], point[2] - 1)))
    return ret             
             
def get_rel_nbs_ids(point, shape):
    ret = []
    if point[0] + 1 < shape[0]: ret.append(0)
    if point[0] - 1 > 0: ret.append(1)
    if point[1] + 1 < shape[1]: ret.append(2)
    if point[1] - 1 > 0: ret.append(3)
    if point[2] + 1 < shape[2]: ret.append(4)
    if point[2] - 1 > 0: ret.append(5)
    return ret

def watershed2(i_d, logger):
    # compute neighbours
    logger.info('Computing differences...')
    nbs = compute_neighbours(i_d)

    # compute min altitude map
    logger.info('Computing minimal altitude map...')
    minaltitude = nbs[0]
    for nb in nbs[1:]:
        minaltitude = scipy.minimum(minaltitude, nb)
    
    # watershed
    logger.info('Watershed \w minaltitude and edge pre-computation...')
    result = scipy.zeros(i_d.shape, dtype=scipy.uint16)
    nb_labs = 0
    for x in range(result.shape[0]):
        for y in range(result.shape[1]):
            for z in range(result.shape[2]):
                if not 0 == result[x,y,z]: continue # 10%
                L, lab = stream_edges_set2(i_d, result, minaltitude, nbs, (x, y, z)) # 90%
                if -1 == lab:
                    nb_labs += 1
                    for p in L:
                        result[p] = nb_labs
                else:
                    for p in L: 
                        result[p] = lab
                        
    return result

def watershed(i_d, logger):
    # compute neighbours
    logger.info('Computing differences...')
    nbs = compute_neighbours(i_d)

    # compute min altitude map
    logger.info('Computing minimal altitude map...')
    minaltitude = nbs[0]
    for nb in nbs[1:]:
        minaltitude = scipy.minimum(minaltitude, nb)
    
    # watershed
    logger.info('Watershed \w minaltitude pre-computation...')
    result = scipy.zeros(i_d.shape, dtype=scipy.uint16)
    nb_labs = 0
    for x in range(result.shape[0]):
        for y in range(result.shape[1]):
            for z in range(result.shape[2]):
                if result[x,y,z] != 0: continue # 10%
                L, lab = stream_set(i_d, result, minaltitude, (x, y, z)) # 90%
                if -1 == lab:
                    nb_labs += 1
                    for p in L:
                        result[p] = nb_labs
                else:
                    for p in L: 
                        result[p] = lab
                        
    return result

def stream_edges_set2(original, result, minaltitude, edges, x):
    l_pos = set((x,))
    l_neg = set((x,))
    while 0 != len(l_neg):
        y = l_neg.pop()
        y_min = minaltitude[y]        
        y_nbs = get_nbs_idx_set(y, original.shape)
        for idx, nb in y_nbs:
            if nb in l_pos: del y_nbs[idx]
            elif edges[idx][nb] != y_min: del y_nbs[idx]
        for idx, nb in y_nbs: # use eventually sets here
            # three choices
            if 0 != result[nb]:
                return l_pos, result[nb]
            elif minaltitude[nb] < y_min:
                l_pos.add(nb)
                l_neg = set((nb,))
            else:
                l_pos.add(nb)
                l_neg.add(nb)
    return l_pos, -1

def stream_edges_set(original, result, minaltitude, edges, x):
    l_pos = set((x,))
    l_neg = set((x,))
    while 0 != len(l_neg):
        y = l_neg.pop()
        y_min = minaltitude[y]        
        y_nbs = get_nbs_idx_set(y, original.shape)
        for idx, nb in y_nbs: # use eventually sets here
            if nb in l_pos:
                continue
            elif edges[idx][nb] != y_min:
                continue            
            # three choices
            if 0 != result[nb]:
                return l_pos, result[nb]
            elif minaltitude[nb] < y_min:
                l_pos.add(nb)
                l_neg = set((nb,))
            else:
                l_pos.add(nb)
                l_neg.add(nb)
    return l_pos, -1

def stream_set(original, result, minaltitude, x): # slightly faster, since l_ sets do not get very long
    l_pos = set((x,))
    l_neg = set((x,))
    while 0 != len(l_neg):
        y = l_neg.pop()
        y_val = original[y]
        y_min = minaltitude[y]        
        y_nbs = get_nbs_set(y, original.shape) - l_pos
        for nb in y_nbs: # use eventually sets here
            if abs(original[nb] - y_val) != y_min:
                continue
            # three choices
            if 0 != result[nb]:
                return l_pos, result[nb]
            elif minaltitude[nb] < y_min:
                l_pos.add(nb)
                l_neg = set((nb,))
            else:
                l_pos.add(nb)
                l_neg.add(nb)
    return l_pos, -1

def stream(original, result, minaltitude, x):
    l_pos = [x]
    l_neg = [x]
    while 0 != len(l_neg):
        y = l_neg.pop()
        y_val = original[y]
        y_min = minaltitude[y]
        y_nbs = get_nbs(y, original.shape)
        for nb in y_nbs: # use eventually sets here
            if nb in l_pos:
                continue
            elif abs(original[nb] - y_val) != y_min:
                continue
            # three choices
            if 0 != result[nb]:
                return l_pos, result[nb]
            elif minaltitude[nb] < y_min:
                l_pos.append(nb)
                l_neg = [nb]
            else:
                l_pos.append(nb)
                l_neg.append(nb)
    return l_pos, -1
    
def compute_neighbours(image):
    down = scipy.concatenate((scipy.zeros_like(image[slice(True)]), abs(image[1:] - image[:-1])), 0)
    up = scipy.concatenate((abs(image[:-1] - image[1:]), scipy.zeros_like(image[slice(True)])), 0)
    left = scipy.concatenate((scipy.zeros_like(image[:,slice(True)]), abs(image[:,1:] - image[:,:-1])), 1)
    right = scipy.concatenate((abs(image[:,:-1] - image[:,1:]), scipy.zeros_like(image[:,slice(True)])), 1)
    into = scipy.concatenate((scipy.zeros_like(image[:,:,slice(True)]), abs(image[:,:,1:] - image[:,:,:-1])), 2)
    out = scipy.concatenate((abs(image[:,:,:-1] - image[:,:,1:]), scipy.zeros_like(image[:,:,slice(True)])), 2)
    return down, up, left, right, into, out

def compute_neighbours_max_border(image):
    int16_max = 32767
    down = scipy.concatenate((scipy.zeros_like(image[slice(True)]) + int16_max, abs(image[1:] - image[:-1])), 0)
    up = scipy.concatenate((abs(image[:-1] - image[1:]), scipy.zeros_like(image[slice(True)]) + int16_max), 0)
    left = scipy.concatenate((scipy.zeros_like(image[:,slice(True)]) + int16_max, abs(image[:,1:] - image[:,:-1])), 1)
    right = scipy.concatenate((abs(image[:,:-1] - image[:,1:]), scipy.zeros_like(image[:,slice(True)]) + int16_max), 1)
    into = scipy.concatenate((scipy.zeros_like(image[:,:,slice(True)]) + int16_max, abs(image[:,:,1:] - image[:,:,:-1])), 2)
    out = scipy.concatenate((abs(image[:,:,:-1] - image[:,:,1:]), scipy.zeros_like(image[:,:,slice(True)]) + int16_max), 2)
    return down, up, left, right, into, out

def compute_neighbours_max_border_gradient(image):
    int16_max = 32767
    down = scipy.concatenate((scipy.zeros_like(image[slice(True)]) + int16_max, scipy.maximum(image[1:], image[:-1])), 0)
    up = scipy.concatenate((scipy.maximum(image[:-1], image[1:]), scipy.zeros_like(image[slice(True)]) + int16_max), 0)
    left = scipy.concatenate((scipy.zeros_like(image[:,slice(True)]) + int16_max, scipy.maximum(image[:,1:], image[:,:-1])), 1)
    right = scipy.concatenate((scipy.maximum(image[:,:-1], image[:,1:]), scipy.zeros_like(image[:,slice(True)]) + int16_max), 1)
    into = scipy.concatenate((scipy.zeros_like(image[:,:,slice(True)]) + int16_max, scipy.maximum(image[:,:,1:], image[:,:,:-1])), 2)
    out = scipy.concatenate((scipy.maximum(image[:,:,:-1], image[:,:,1:]), scipy.zeros_like(image[:,:,slice(True)]) + int16_max), 2)
    return down, up, left, right, into, out

def get_nbs(point, shape):
    ret = []
    if point[0] - 1 > 0: ret.append((point[0] - 1, point[1], point[2]))
    if point[1] - 1 > 0: ret.append((point[0], point[1] - 1, point[2]))
    if point[2] - 1 > 0: ret.append((point[0], point[1], point[2] - 1))
    if point[0] + 1 < shape[0]: ret.append((point[0] + 1, point[1], point[2]))
    if point[1] + 1 < shape[1]: ret.append((point[0], point[1] + 1, point[2]))
    if point[2] + 1 < shape[2]: ret.append((point[0], point[1], point[2] + 1))
    return ret

def get_nbs_idx(point, shape):
    ret = []
    if point[0] + 1 < shape[0]: ret.append((0, (point[0] + 1, point[1], point[2])))
    if point[0] - 1 > 0: ret.append((1, (point[0] - 1, point[1], point[2])))
    if point[1] + 1 < shape[1]: ret.append((2, (point[0], point[1] + 1, point[2])))
    if point[1] - 1 > 0: ret.append((3, (point[0], point[1] - 1, point[2])))
    if point[2] + 1 < shape[2]: ret.append((4, (point[0], point[1], point[2] + 1)))
    if point[2] - 1 > 0: ret.append((5, (point[0], point[1], point[2] - 1)))
    return ret

def get_nbs_set(point, shape):
    ret = set()
    if point[0] - 1 > 0: ret.add((point[0] - 1, point[1], point[2]))
    if point[1] - 1 > 0: ret.add((point[0], point[1] - 1, point[2]))
    if point[2] - 1 > 0: ret.add((point[0], point[1], point[2] - 1))
    if point[0] + 1 < shape[0]: ret.add((point[0] + 1, point[1], point[2]))
    if point[1] + 1 < shape[1]: ret.add((point[0], point[1] + 1, point[2]))
    if point[2] + 1 < shape[2]: ret.add((point[0], point[1], point[2] + 1))
    return ret

def get_nbs_idx_set(point, shape):
    ret = []
    if point[0] + 1 < shape[0]: ret.append((0, (point[0] + 1, point[1], point[2])))
    if point[0] - 1 > 0: ret.append((1, (point[0] - 1, point[1], point[2])))
    if point[1] + 1 < shape[1]: ret.append((2, (point[0], point[1] + 1, point[2])))
    if point[1] - 1 > 0: ret.append((3, (point[0], point[1] - 1, point[2])))
    if point[2] + 1 < shape[2]: ret.append((4, (point[0], point[1], point[2] + 1)))
    if point[2] - 1 > 0: ret.append((5, (point[0], point[1], point[2] - 1)))
    return ret

def get_nbs_set2(point, shape): # in theory (and with %timeit) faster, but in practise slower
    ret = set()
    p = point[0] - 1
    if p > 0: ret.add((p, point[1], point[2]))
    p = point[1] - 1
    if p > 0: ret.add((point[0], p, point[2]))
    p = point[2] - 1
    if p > 0: ret.add((point[0], point[1], p))
    p = point[0] + 1
    if p < shape[0]: ret.add((p, point[1], point[2]))
    p = point[1] + 1
    if p < shape[1]: ret.add((point[0], p, point[2]))
    p = point[2] + 1
    if p < shape[2]: ret.add((point[0], point[1], p))
    return ret
             

if __name__ == "__main__":
    main()