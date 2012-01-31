
import logging

import scipy
from nibabel.loadsave import load, save

from medpy.core import Logger
from medpy.graphcut import graph, generate, cut, parse, energy
from medpy.utilities.nibabel import image_like

def main():
    # prepare logger
    logger = Logger.getInstance()
    logger.setLevel(logging.DEBUG)
    
    # input image locations
    i = '/home/omaier/Experiments/Regionsegmentation/Evaluation_Viscous/00originalvolumes/o09.nii' # original image
    g = '/home/omaier/Experiments/Regionsegmentation/Evaluation_Viscous/01gradient/o09_gradient.nii' # gradient magnitude image
    l = 'image.nii' # label image
    fg = 'fg_markers_full_z.nii'
    bg = 'bg_markers_full_z.nii' 
    
    # output image locations
    r = 'result.nii' # liver mask
    c = 'original.nii' # croped original image
    f = 'foreground.nii' # foreground markers
    b = 'background.nii' # background markers
    
    # load images
    i_i = load(i)
    g_i = load(g)
    l_i = load(l)
    fg_i = load(fg)
    bg_i = load(bg)
    
    # extract and prepare image data
    i_d = scipy.squeeze(i_i.get_data())
    g_d = scipy.squeeze(g_i.get_data())
    l_d = scipy.squeeze(l_i.get_data())
    fg_d = scipy.squeeze(fg_i.get_data())
    bg_d = scipy.squeeze(bg_i.get_data())
    
    # crop input images to achieve faster execution
    #crop = [slice(50, -50),
    #        slice(50, -50),
    #        slice(50, -50)]
    #i_d = i_d[crop]
    #g_d = g_d[crop]
    #l_d = l_d[crop]
    #fg_d = fg_d[crop]
    #bg_d = bg_d[crop]
    
    # recompute the label ids to start from id
    l_d =  graph.relabel(l_d)

    # create markers
#    # fg: (slightly left of center)
#    fg = scipy.zeros(i_d.shape, dtype=scipy.bool_)
#    #mid = scipy.asarray(i_d.shape)/2
#    #fg[mid[0]-50:mid[0]+50, mid[1]-10:mid[1]+10, mid[2]-10:mid[2]+10] = True
#    fg[0:40,20:-20,-40:] = True # x (down->up/0->end) , y (down->up/0->end), z (down->up/0->end)
#
#    # bg: 1px at image borders
#    bg = scipy.zeros(i_d.shape, dtype=scipy.bool_)
#    bg[80:,:,:30] = True

    # execute
    logger.info('Preparing graph...')
    gr = graph.graph_from_labels(l_d, fg_d, bg_d, boundary_term = energy.boundary_stawiaski, boundary_term_args = g_d)
    inconsistent = gr.inconsistent()
    if inconsistent:
        logger.error('The created graph contains inconsistencies: {}'.format('\n'.join(inconsistent)))

    # execute min-cut
    logger.info('Executing min-cut...')
    source_file = generate.bk_mfmc_generate(gr)
    output = cut.bk_mfmc_cut(source_file, keep=True)
    
    # parse
    logger.info('Parsing results...')
    result = parse.bk_mfmc_parse(output)
    #print result
    
    # apply results to label image
    logger.info('Applying results...')
    l_d = parse.apply_mapping(l_d, result[1])
                
    logger.info('Saving images resulting mask...')
    # save resulting mask    
    save(image_like(l_d, l_i), r)
    
    logger.info('Saving regarded original image...')
    # save cut input image
    save(image_like(i_d, i_i), c)
    
    logger.info('Saving foreground marker...')
    save(image_like(fg_d, i_i), f)
    
    logger.info('Saving background marker...')
    save(image_like(bg_d, i_i), b)
        
    logger.info('Done!')

    
if __name__ == "__main__":
    main()