import logging

import scipy
from nibabel.loadsave import load, save

from medpy.core import Logger
from medpy import graphcut
from medpy import filter
from medpy.utilities.nibabel import image_like

def main():
    # prepare logger
    logger = Logger.getInstance()
    logger.setLevel(logging.DEBUG)
    
    # input image locations
    #i = '/home/omaier/Experiments/Regionsegmentation/Evaluation_Viscous/00originalvolumes/o09.nii' # original image
    g = '/home/omaier/Experiments/Regionsegmentation/Evaluation_Viscous/01gradient/o09_gradient.nii' # gradient magnitude image
    l = '/home/omaier/Experiments/GraphCut/RegionalTerm/images/label_full.nii' # watershed label image
    fg = '/home/omaier/Experiments/GraphCut/RegionalTerm/images/fg_markers.nii'
    bg = '/home/omaier/Experiments/GraphCut/RegionalTerm/images/bg_markers.nii'
    
    # output image locations
    r = '/home/omaier/Experiments/GraphCut/BoundaryTerm/graphcut_full.nii' # liver mask
    
    # load images
    #i_i = load(i)
    g_i = load(g)
    l_i = load(l)
    fg_i = load(fg)
    bg_i = load(bg) 
    
    # extract and prepare image data
    #i_d = scipy.squeeze(i_i.get_data())
    g_d = scipy.squeeze(g_i.get_data())
    l_d = scipy.squeeze(l_i.get_data())
    fg_d = scipy.squeeze(fg_i.get_data())
    bg_d = scipy.squeeze(bg_i.get_data())
    
    # crop input images to achieve faster execution
    #crop = [slice(50, -100),
    #        slice(50, -100),
    #        slice(50, -100)]
    #g_d = g_d[crop]
    #l_d = l_d[crop]
    #fg_d = fg_d[crop]
    #bg_d = bg_d[crop]       
    
    # recompute the label ids to start from id
    logger.info('Relabel input image...')
    l_d =  filter.relabel(l_d)

    # generate graph
    logger.info('Preparing graph...')
    gr = graphcut.graph_from_labels(l_d, fg_d, bg_d, boundary_term = graphcut.boundary_stawiaski, boundary_term_args = g_d)
    #inconsistent = gr.inconsistent()
    #if inconsistent:
    #    logger.error('The created graph contains inconsistencies: {}'.format('\n'.join(inconsistent)))

    # build graph cut graph from graph
    logger.info('Generating BK_MFMC C++ graph...')
    gcgraph = graphcut.GraphDouble(len(gr.get_nodes()), len(gr.get_nweights()))
    gcgraph.add_node(len(gr.get_nodes()))
    for node, weight in gr.get_tweights().items():
        gcgraph.add_tweights(int(node - 1), weight[0], weight[1])
    for edge, weight in gr.get_nweights().items():
        gcgraph.add_edge(int(edge[0] - 1), int(edge[1] - 1), weight[0], weight[1])    
    
    # execute min-cut
    logger.info('Executing min-cut...')
    maxflow = gcgraph.maxflow()
    logger.debug('Maxflow is {}'.format(maxflow))
    
    # collect
    logger.info('Applying results...')
    l_d = filter.relabel_map(l_d, gcgraph.what_segment, lambda fun, rid: 0 if gcgraph.termtype.SINK == fun(int(rid) - 1) else 1)
                
    logger.info('Saving images resulting mask...')
    # save resulting mask
    l_d = l_d.astype(scipy.bool_)
    save(image_like(l_d, fg_i), r)

    logger.info('Done!')

if __name__ == "__main__":
    main()