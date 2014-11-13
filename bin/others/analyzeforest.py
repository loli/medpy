#!/usr/bin/python

"""
Performs a statistical analysis of a pickled RDF.

arg1: the pickled RDF
arg2: the feature names numpy struct
arg3: the target csv file with feature names
arg4: the target csv file with the whole feature appearances
arg5: the target csv file with the sequence grouped feature appearances
arg6: the target csv file with the feature grouped feature appearances
arg7: the feature importances
arg8: the feature importances grouped by feature
arg9: the RDF/ET usage
"""

import os
import sys
import pickle

import numpy

def main():
    rdf_file = sys.argv[1]
    
    print('Analyzing RDF {}:'.format(rdf_file))
    print('####################################################')
    rdf = pickle.load(open(rdf_file, 'r'))
    
    print('\nBase information:')
    print('\tForest type: {}'.format(type(rdf)))
    print('\tBase estimator type: {}'.format(type(rdf.base_estimator)))
    for name, value in rdf.get_params().items():
        print('\t{}: {}'.format(name, value))
    print('\tN feature: {}'.format(rdf.n_features_))
    print('\tN classes: {}'.format(rdf.n_classes_))
    print('\tN estimators: {}'.format(len(rdf.estimators_)))

    print('\nNote on max_features attribute:')
    print('\tIf int, then consider max_features features at each split.\n\t\
If float, then max_features is a percentage and int(max_features * n_features) features are considered at each split.\n\t\
If "auto", then max_features=sqrt(n_features).\n\t\
If "sqrt", then max_features=sqrt(n_features).\n\t\
If "log2", then max_features=log2(n_features).\n\t\
If None, then max_features=n_features.')

    # prepare counters
    fu = numpy.zeros((rdf.n_features_, rdf.estimators_[0].max_depth), numpy.int) # feature usage # !TODO: Dangerous if max_depth is set to None, what happens then?
    td = [] # tree depths
    ts = [] # tree sizes
    etocc = [0] * rdf.estimators_[0].max_depth
    rdfocc = [0] * rdf.estimators_[0].max_depth

    # prepare constants
    TREE_LEAF = -1 # !TODO: Use the value defined in scikit-learn here, rather than defining it by myself

    print('\nParsing trees...', end=' ')
    for no, e in enumerate(rdf.estimators_):
        t = e.tree_
        ts.append(t.node_count)

        def recursive(idx, depth):
            # break condition: reached leaf node
            if TREE_LEAF == t.children_left[idx]:
                return depth - 1
            # collect information of current node
            fu[t.feature[idx], depth] += 1
        if t.value[idx,:,0] < 0:
            etocc[depth] += 1
        else:
        rdfocc[depth] += 1
            # continue down the tree (left & right)
            ldepth = recursive(t.children_left[idx], depth + 1)
            rdepth = recursive(t.children_right[idx], depth + 1)
            # return maximum depth found
            return max(ldepth, rdepth)
            
        max_depth = recursive(0, 0) # Note: first node is considered depth level 1
        td.append(max_depth)

        print(no, end=' ')
        sys.stdout.flush()
        
    print('done.')
    
    print('Trimming results...', end=' ')
    fu = fu[:,:max(td)+1]
    print('done.')

    print('\nGeneral tree information:')
    print('\tMean/median/max/min tree depth: {} / {} / {} / {}'.format(numpy.mean(td), numpy.median(td), numpy.max(td), numpy.min(td)))
    print('\tMean/median/max/min tree size (in nodes incl leafs): {} / {} / {} / {}'.format(numpy.mean(ts), numpy.median(ts), numpy.max(ts), numpy.min(ts)))
    
    #print '\nFeature\tnode appearances:'
    #for fidx, val in enumerate(numpy.sum(fu, 1)):
    #    print '{}\t{}'.format(fidx, val)

    #print '\nFeature\thighest appearance level:'
    #for fidx, farr in enumerate(fu):
    #    nz = numpy.nonzero(farr)
    #    print '{}\t{}'.format(fidx, nz[0][0])
        
    print('Loading feature names...', end=' ')
    fn_ = numpy.load(sys.argv[2])
    fn = []
    for n in fn_:
        if not 'histogram' in n:
            fn.append(n)
        else:
            for i in range(0, 11):
                fn.append('{}_bin{}'.format(n, i))
    print('done.')
    with open(sys.argv[3], 'w') as f:
        for i, n in enumerate(fn):
            f.write('{}\t{}\n'.format(i, n))
        
        
    print('Creating full csv files...', end=' ')
    div = numpy.sum(fu, 0, dtype=numpy.float)
    rc = fu / div
    with open(sys.argv[4], 'w') as f:
        numpy.savetxt(f, rc, '%.5f', '\t', '\n', 'feature_ids X depth, val=occurences of forst {}'.format(sys.argv[1]))
    print('done.')
    
    print('Grouping by sequence...', end=' ')
    sequence_keys = []
    for n in fn:
        sequence_keys.append(n.split('.')[1])
        
    sequences_unique = numpy.unique(sequence_keys)
    grouped_by_sequence = numpy.zeros((len(sequences_unique), rc.shape[1]))
    for sk, row in zip(sequence_keys, rc):
        idx = numpy.where(sequences_unique==sk)[0][0]
        grouped_by_sequence[idx] += row
    print(sequences_unique)
    with open(sys.argv[5], 'w') as f:
        numpy.savetxt(f, grouped_by_sequence, '%.5f', '\t', '\n', 'sequences X depth, val=occurences of forst {}'.format(sys.argv[1]))
    print('done.')
    
    print('Grouping by features...', end=' ')
    feature_keys = []
    for n in fn:
        feature_keys.append('.'.join(n.split('.')[2:]))
        
    features_unique = numpy.unique(feature_keys)
    grouped_by_feature = numpy.zeros((len(features_unique), rc.shape[1]))
    for fk, row in zip(feature_keys, rc):
        idx = numpy.where(features_unique==fk)[0][0]
        grouped_by_feature[idx] += row
    print('\n'.join(features_unique))
    with open(sys.argv[6], 'w') as f:
        numpy.savetxt(f, grouped_by_feature, '%.5f', '\t', '\n', 'features X depth, val=occurences of forst {}'.format(sys.argv[1]))
    print('done.')
        
    
    print('Writing rdf feature importances...', end=' ')
    feature_importances = rdf.feature_importances_
    with open(sys.argv[7], 'w') as f:
        for n, imp in zip(fn, feature_importances):
            f.write('{}\t{}\n'.format(n, imp))
    print('done.')
            
    print('Writing rdf feature importances grouped...', end=' ')
    grouped_by_feature = [0] * len(features_unique)
    with open(sys.argv[8], 'w') as f:
        for n, imp in zip(fn, feature_importances):
            idx = 0
            for i, fu in enumerate(features_unique):
                if fu in n:
                    idx = i
                    break
            grouped_by_feature[idx] += imp
        for n, imp in zip(features_unique, grouped_by_feature):
            f.write('{}\t{}\n'.format(n, imp))
    print('done.')

    sys.exit(0)

    print('Writing rdf/et node usage...', end=' ')
    etocc = etocc[:numpy.nonzero(etocc)[0][-1]+1]
    rdfocc = rdfocc[:numpy.nonzero(rdfocc)[0][-1]+1]
    print(sys.argv[9])
    with open(sys.argv[9], 'w') as f:
    f.write('ET node occurences\t{}\n'.format('\t'.join(map(str, etocc))))
    f.write('RDF node occurences\t{}\n'.format('\t'.join(map(str, rdfocc))))
    print('done.')
    
if __name__ == "__main__":
    main()

        
    
        
        
