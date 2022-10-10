# Tile-pattern Kullback-Leibler Divergence algorithm
# from Lucas and Volz https://arxiv.org/pdf/1905.05077.pdf
# Values closer to 0 mean more similar to training set - further = more different

import math
import os
import random
import sys
import numpy as np

#generic function
#create a the tile pattern probability dictionary from a level set
def getTPProb(levels,size=2):
    tpd = {}
    #get patterns from each level by using a sliding window (assume square level)
    for l in levels:
        for i in range(np.prod(l.shape)):
            c = i % l.shape[0]
            r = math.floor(i / l.shape[0])
            
            #check if out of bounds
            if((r+size)>l.shape[0] or (c+size)>l.shape[1]):
                continue
            
            #get the tile window set
            twin = l[r:r+size,c:c+size]
            twin_flat = "".join([hex(x).replace('0x','') for x in twin.flatten()])
            #twin_flat = str(twin.flatten())
            if twin_flat not in tpd:
                tpd[twin_flat] = 0
            tpd[twin_flat]+=1
    return tpd

#C(x) = # tile patterns (x) | C = total # tile patterns
#P'(x)/Q'(x) formula = [C(x)+e]/[(C+e)(1+e)]
def probDist(cx,C,eps):
    return (cx+eps)/((C+eps)*(1+eps))
            
#calculate the tile-pattern kl divergence fitness for a given map and given tile pattern dictionary
def tp_fitness(m,tpd,EPSILON=1e-6,WEIGHT=0.5,WINDOW=2):
    mtp = getTPProb([m],WINDOW)        #tile patterns for the input map
    Q = sum(list(tpd.values())) #total # of tile patterns for q set (training set)
    P = sum(list(mtp.values())) #total # of tile patterns for p set (test map)
    
    #DKL(P||Q) = sum[all tile pattern in set P => x](P'(x)log[P'(x)/Q'(x))]
    
    #input set in training set (p||q)
    dkl_p = 0
    for x in mtp.keys():
        #for each pattern in input set calculate and add value
        pcx = mtp[x] if x in mtp else 0
        qcx = tpd[x] if x in tpd else 0
        px = probDist(pcx,P,EPSILON)
        qx = probDist(qcx,Q,EPSILON)

        dkl_p += px*math.log(px/qx)
            
    #training set in input set (q||p)
    dkl_q = 0
    for x in tpd.keys():
        #for each pattern in input set calculate and add value
        pcx = mtp[x] if x in mtp else 0
        qcx = tpd[x] if x in tpd else 0
        px = probDist(pcx,P,EPSILON)
        qx = probDist(qcx,Q,EPSILON)

        dkl_q += qx*math.log(qx/px)
        
    #print(f"P:{dkl_p} | Q:{dkl_q}")
    
    #calculate fitness
    #fitness = -[w*(DKL(P||Q)) + (1-w)*(DKL(Q||P))]
    return -(WEIGHT*dkl_p + (1-WEIGHT)*dkl_q)


# GET A LEVELS SET'S LIST OF TILE PATTERNS AS 2D ARRAYS
def getPatternList2d(levels,size=2):
    #get the tile patterns and cts (as <string:int> dictionary)
    tp_patts = getTPProb(levels,size)

    #export tile patterns to 2d array subsets
    patt2d = np.array([np.array([int(i,16) for i in list(x)]).reshape(size,size) for x in tp_patts.keys()])

    return patt2d

# GET A LEVELS SET'S LIST OF TILE PATTERNS AS 2D ARRAYS SORTED BY HIGHEST PROBABILITY
def getPatternList2dSorted(levels,size=2):
    #get the tile patterns and cts (as <string:int> dictionary)
    tp_patts = getTPProb(levels,size)

    # sort by value (high to low)
    pats = sorted(tp_patts, key=tp_patts.get,reverse=True)  

    #export tile patterns to 2d array subsets
    patt2d = np.array([np.array([int(i,16) for i in list(x)]).reshape(size,size) for x in pats])
    return patt2d
    
   

