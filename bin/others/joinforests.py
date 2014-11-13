#!/usr/bin/python

"""
Join the trees of a number of forest into a common ensemble classifier.

arg1: the (max) number of trees to pick per forest
arg2: the target forest
arg3+: the input forests
"""

import sys
import pickle

def main():
    ntrees = int(sys.argv[1])
    target = sys.argv[2]
    sources = sys.argv[3:]
    
    print('Combining forests...')
    rdf = pickle.load(open(sources[0], 'r'))
    rdf.estimators_[:ntrees]
    nfeatures =  rdf.n_features_
    nclasses = rdf.n_classes_
    for source in sources[1:]:
        rdf_ = pickle.load(open(source, 'r'))
        if not nfeatures ==  rdf_.n_features_:
            raise Exception('Forest {} has incompatible number of features {} with first forest.'.format(source, rdf_.n_features_))
        if not nclasses ==  rdf_.n_classes_:
            raise Exception('Forest {} has incompatible number of classes {} with first forest.'.format(source, rdf_.n_classes_))
        rdf.estimators_.extend(rdf_.estimators_[:ntrees])
    rdf.n_estimators = len(rdf.estimators_)
    print('done.')
       
    #rdf.n_estimators
    #rdf.n_features_
    #rdf.n_classes_
    
    print('Saving resulting forest...')
    pickle.dump(rdf, open(target, 'w'))
    print('done.')
    
    print('Warning: The parameters reflected by the resulting forests will not be valid!')
    
if __name__ == "__main__":
    main()

        
    
        
        