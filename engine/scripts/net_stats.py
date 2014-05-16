from itertools import combinations
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
## from rpy2.robjects.numpy2ri import numpy2ri
import rpy2.robjects.numpy2ri
rpy2.robjects.numpy2ri.activate()
from rpy2.robjects.vectors import DataFrame
from random import randrange
import rpy2.rinterface as ri
import numpy as np
import os.path
import csv
import json
# numpy2ri.activate()

class Net_Stats:
    
    def __init__ (self, reslist, weight=True):
        """
        Initialize the statistic class of python
        """
        self.adj = np.array(reslist)
        
        self.igraph = importr('igraph')
        self.gadj = self.igraph.graph_adjacency
        direct = 'directed'
        
        # Check if the matrix is symmetric
        ck = (np.triu(self.adj).transpose() - np.tril(self.adj))
        if not ck.all():
            direct = 'undirected'
            tmp = np.triu(self.adj)
        else:
            tmp = self.adj
        
        # Apply thresholding
        try:
            thr = np.percentile(tmp[tmp > 0.0], 100-perc)
        except:
            thr = 0.0
        
        
        # Create the graph object
        self.g = self.gadj(reslist, mode=direct, weighted=weight, diag=False)
        # self.gp = igraph.Graph.Weighted_Adjacency(tmp.tolist())
        
        # Check for weights attribute
        self.ww = ri.NULL
        if weight:
            self.ww = self.igraph.get_edge_attribute(self.g, "weight")
        
    
    def compute_modularity(self, mod_meth = 'spinglass'):
        """
        Compute network modularity
        """
        
        # Initialize communities to 0
        mm = [0 for j in xrange(self.adj.shape[0])]
        
        # Get communities 
        try:
            gmm = self.igraph.spinglass_community(self.g, weights=self.ww)
            mm = self.igraph.membership(gmm)
        except:
            print 'Ciao'
            
        self.mm = mm
        
        return self.mm


    def degree (self):
        tmp = self.igraph.graph_strength(self.g)
        return tmp

        
    def degree_by_community(self):
        # Get node degree by community
        comdeg = np.empty(len(self.mm))
        for m in np.unique(self.mm):
            idxtmp = np.where(self.mm == m)[0]
            tmps = self.adj[:,idxtmp][idxtmp,:]
            comdeg[idxtmp] = tmps.sum(axis=1)
            
        return comdeg

    def pgrank(self):
        """
        Return pagerank by
        """
        tmp = self.igraph.page_rank(self.g)[0]
        
        return tmp
        
    
    def pgrank_by_community(self):
        """
        Get node degree by community
        """
        compg = np.empty(self.adj.shape[0])
        ## rmat = robjects.r['matrix']
        for m in np.unique(self.mm):

            idxtmp = np.where(self.mm == m)[0]
            tmps = self.adj[:,idxtmp][idxtmp,:]
            ## nr, nc = tmps.shape
            # tmpsr = robjects.FloatVector(tmps)
            ## print nc, nr
            ## tmpr = rmat(tmps,nrow=nc, ncol=nr, byrow=True)
            ## print tmpr
            gp = self.gadj(tmps,mode="undirected", weighted=True, diag=False)
            compg[idxtmp] = self.igraph.page_rank(gp)[0]
            
        return compg
    
    def eccentricity (self):
        return self.igraph.eccentricity(self.g)

    def ecc_by_community (self):
        compg = np.empty(self.adj.shape[0])
        
        for m in np.unique(self.mm):
            idxtmp = np.where(self.mm == m)[0]
            tmps = self.adj[:,idxtmp][idxtmp,:]
            gp = self.gadj(tmps,mode="undirected", weighted=True, diag=False)
            compg[idxtmp] = self.igraph.eccentricity(gp)[0]
        
        return compg


    def radius (self):
        return self.igraph.radius(self.g)
    
    def alphac (self, comm=True):
        
        return self.igraph.alpha_centrality(self.g)
    
    def alphac_by_community (self, comm=True):
        
        tmp = np.empty(self.adj.shape[0])
        for m in np.unique(self.mm):
            idxtmp = np.where(self.mm == m)[0]
            tmps = self.adj[:,idxtmp][idxtmp,:]
            gp = self.gadj(tmps,mode="undirected", weighted=True, diag=False)
            tmp[idxtmp] = self.igraph.alpha_centrality(gp)
                
        return tmp

    def evcent (self):
        
        return self.igraph.evcent(self.g)[0]#, weights=self.ww)
    
    def evcent_by_community (self, comm=True):
        
        tmp = np.empty(self.adj.shape[0])
        for m in np.unique(self.mm):
            idxtmp = np.where(self.mm == m)[0]
            ww = np.empty(len(idxtmp))
            tmps = self.adj[:,idxtmp][idxtmp,:]
            gp = self.gadj(tmps,mode="undirected", weighted=True, diag=False)
            tmp[idxtmp] = self.igraph.evcent(gp)[0]
                
        return tmp
            
