#!/usr/bin/python

#
# COMPUTING OF FUZZY HISTOGRAM
#

# build-in modules

# third-party modules
import scipy
import math
import time
from medpy.features.histogram import fuzzy_histogram, triangular_membership, trapezoid_membership, gaussian_membership, sigmoidal_difference_membership

# path changes

# own modules

# code
__NARROW = ['triangular', 'trapezoid'] # 1, 1
__WIDE = ['gaussian', 'sigmoid', 'bell'] # 3, 100,  

def main():
    # set parameters
    min = 0
    max = 100
    val = 1000
    bins = 10
    values = scipy.random.randint(min, max, val)
    
    rang = (values.min(), values.max())
    binw = (rang[1] - rang[0]) / float(bins)
    b = scipy.asarray([i * binw + rang[0] for i in range(bins + 1)])
    
    print values[:10]
    print binw, b
    
    for i in range(1, 11):
        bins2 = bins + 2 * i
        rang2 = (rang[0] - 1 * i * binw, rang[1] + 1 * i * binw)
        #i = 1./i
        #bins2 = bins + 2
        #rang2 = (rang[0] - 1*binw, rang[1] + 1*binw)
        h, b = fuzzy_histogram(values, bins=10, normed=False, membership='trapezoid', guarantee = True)
        print i, sum(h), val-0.001*val
        print b
        #print 1./i, sum(h), val-0.000335237595304423*val
    
    # gauss \w s=1
    
    
#    
#    print "22222222222222222222222222"
#    #print h[10:20], b[10:20]
#
#    mb1 = triangular_membership(-2, 1, 0.5)
#    mb2 = triangular_membership(-1, 1, 0.5)
#    mb3 = triangular_membership(0, 1, 0.5)
#    mb4 = triangular_membership(1, 1, 0.5)
#    mb5 = triangular_membership(2, 1, 0.5)
#    v = -0.5
#    for _ in range(0, 11):
#        print mb1(v), mb2(v), mb3(v), mb4(v), mb5(v)
#        print mb1(v) + mb2(v) + mb3(v) + mb4(v) + mb5(v)
#        v += 1./10
#    
#    mb2 = trapezoid_membership(-1, 1, 0.25)
#    mb3 = trapezoid_membership(0, 1, 0.25)
#    mb4 = trapezoid_membership(1, 1, 0.25)
#    print mb2(v), mb3(v), mb4(v)
#    print mb2(v) + mb3(v) + mb4(v)
#    
#    print v, ":", mb(v)
#    mb2 = gaussian_membership(-1, 1, 1)
#    mb3 = gaussian_membership(0, 1, 1)
#    mb4 = gaussian_membership(1, 1, 1)
#    mb5 = gaussian_membership(2, 1, 1.75)
#    print mb1(0), mb2(0), mb3(0), mb4(0), mb5(0)
#    print mb1(0) + mb2(0) + mb3(0) + mb4(0) + mb5(0)
    
#    for s in range(1, 11):
#        print "Smoothness:", s
#        mb1 = triangular_membership(-2, 1, s)
#        mb2 = triangular_membership(-1, 1, s)
#        mb3 = triangular_membership(0, 1, s)
#        mb4 = triangular_membership(1, 1, s)
#        mb5 = triangular_membership(2, 1, s)
#        v = -0.5
#        for _ in range(0, 11):
#            print v, ":", mb1(v) + mb5(v) + mb2(v) + mb3(v) + mb4(v), ":", mb2(v), mb3(v), mb4(v), mb1(v), mb5(v)
#            v += 1./10

#    for s in range(1, 11):
#        #s = 1./s
#        print "Smoothness:", s
#        mb = triangular_membership(0, 1, s)
#        v = int(math.ceil(s)) + 0.5
#        print v, ":", mb(v)
#        print 0, ":", mb(0)
#        print -v, ":", mb(-v)
    
#
#    mb1 = sigmoidal_difference_membership(-2, 1, 1.75)
#    mb2 = sigmoidal_difference_membership(-1, 1, 1.75)
#    mb3 = sigmoidal_difference_membership(0, 1, 1.75)
#    mb4 = sigmoidal_difference_membership(1, 1, 1.75)
#    mb5 = sigmoidal_difference_membership(2, 1, 1.75)
#    print mb1(0), mb2(0), mb3(0), mb4(0), mb5(0)
#    print mb1(0) + mb2(0) + mb3(0) + mb4(0) + mb5(0) 
    
    
    
    #mfuns = __NARROW + __WIDE
    #for mfun in mfuns:
    #    print mfun, ":"
    #    t1 = time.time()
    #    h, b = fuzzy_histogram(values, bins=bins, normed=True, membership=mfun)
    #    
    #    t2 = time.time()
    #    print "Took:", t2 - t1
    #    print "Results:"
    #    print h
    #    print b
    #    print ""
    
    print "All done."

if __name__ == "__main__":
    main()  