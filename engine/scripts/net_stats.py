import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.numpy2ri import numpy2ri
import rpy2.rinterface as ri
import numpy as np
from rpy2.rinterface._rinterface import RRuntimeError
robjects.conversion.py2ri = numpy2ri

class Net_Stats:

    def __init__ (self, reslist, weight=True):
        """
        Initialize the statistic class of python
        """
        # Import R functions
        names = robjects.r['colnames']
        nn = names(reslist)
        rlist = robjects.r['list']
        # Create numpy array from R matrix
        self.adj = np.array(reslist)

        # Select only variables with a variance != 0
        adjvar = self.adj.var(axis=0)
        idx = 1 - np.isclose(adjvar,0)
        idx = idx.astype('bool')
        self.adj = self.adj[:,idx][idx,:]
        idxtmp = np.where(idx)[0] + 1
        self.nn = nn.rx(idxtmp)
        
        # Set matrix names
        colnames = ri.StrSexpVector(self.nn)
        rownames = ri.StrSexpVector(self.nn)
        adj = robjects.r.matrix(self.adj, nrow=self.adj.shape[0])
        adj.do_slot_assign("dimnames", rlist(
            ri.StrSexpVector(colnames),
            ri.StrSexpVector(rownames)
        ))

        # Import igraph package from R
        # NB think on using python igraph package
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
        perc = 0.0
        try:
            thr = np.percentile(tmp[tmp > 0.0], 100-perc)
        except:
            thr = 0.0

        # Create the graph object
        self.g = self.gadj(adj, mode=direct, weighted=weight, diag=False )
                
        # Check for weights attribute
        self.ww = ri.NULL
        if weight:
            self.ww = self.igraph.get_edge_attribute(self.g, "weight")

    def ret_names (self):
        """
        Return names of the matrix after cutting out variables with zero variance
        """
        return self.nn
        
    def compute_modularity(self, mod_meth = 'spinglass'):
        """
        Compute network modularity
        """
        
        # Initialize communities to 0
        mm = [1 for j in xrange(self.adj.shape[0])]
        # Get communities
        try:
            gmm = self.igraph.spinglass_community(self.g, weights=self.ww)
            mm = self.igraph.membership(gmm)
            self.comm = True
        except UnboundLocalError, e:
            self.comm = True
        except RRuntimeError, e:
            self.comm = True

        self.mm = mm
                
        return self.mm

    def modularity(self):
        if self.comm:
            return self.igraph.modularity(self.g, self.mm)
        else:
            return False

    def degree (self):
        tmp = self.igraph.graph_strength(self.g)
        return tmp

    def degree_by_community(self):
        # Get node degree by community
        if self.comm:
            comdeg = np.empty(len(self.mm))
            for m in np.unique(self.mm):
                idxtmp = np.where(self.mm == m)[0]
                tmps = self.adj[:,idxtmp][idxtmp,:]
                comdeg[idxtmp] = tmps.sum(axis=1)
            
            return comdeg
        else:
            return False

    def pgrank(self):
        """
        Return pagerank
        """
        tmp = self.igraph.page_rank(self.g)[0]
        
        return tmp
        
    
    def pgrank_by_community(self):
        """
        Get page rank by community
        """
        if self.comm:
            compg = np.empty(self.adj.shape[0])

            for m in np.unique(self.mm):
                idxtmp = np.where(self.mm == m)[0]
                tmps = self.adj[:,idxtmp][idxtmp,:]
                gp = self.gadj(tmps,mode="undirected", weighted=True, diag=False)
                compg[idxtmp] = self.igraph.page_rank(gp)[0]

            return compg
        else:
            return False

    def eccentricity (self):
        """
        Return eccentricity
        """
        return self.igraph.eccentricity(self.g)

    def ecc_by_community (self):
        """
        Return eccentricity for each community in the graph
        """
        if self.comm:
            compg = np.empty(self.adj.shape[0])
            
            for m in np.unique(self.mm):
                idxtmp = np.where(self.mm == m)[0]
                tmps = self.adj[:,idxtmp][idxtmp,:]
                gp = self.gadj(tmps,mode="undirected", weighted=True, diag=False)
                compg[idxtmp] = self.igraph.eccentricity(gp)[0]
            
            return compg
        else:
            return False

    def radius (self):
        """
        Compute the radius of the graph
        """
        
        return self.igraph.radius(self.g)
        
    def density (self):
        """
        Compute the density of the graph
        """
        
        return self.igraph.graph_density(self.g)

    def alphac (self, comm=True):
        """
        Compute the alpha centrality for the given graph
        """
        
        return self.igraph.alpha_centrality(self.g)
    
    def alphac_by_community (self, comm=True):
        """
        Compute the alpha centrality for each community
        """

        if self.comm:
            tmp = np.empty(self.adj.shape[0])
            for m in np.unique(self.mm):
                idxtmp = np.where(self.mm == m)[0]
                tmps = self.adj[:,idxtmp][idxtmp,:]
                gp = self.gadj(tmps,mode="undirected", weighted=True, diag=False)
                tmp[idxtmp] = self.igraph.alpha_centrality(gp)
            
            return tmp
        else:
            return False

    def evcent (self):
        """
        Compute the eigenvalue centrality
        """
        return self.igraph.evcent(self.g)[0]#, weights=self.ww)
    
    def evcent_by_community (self, comm=True):
        """
        Compute the eigenvalue centrality for each community
        """
        
        if self.comm:
            tmp = np.empty(self.adj.shape[0])
            for m in np.unique(self.mm):
                idxtmp = np.where(self.mm == m)[0]
                ww = np.empty(len(idxtmp))
                tmps = self.adj[:,idxtmp][idxtmp,:]
                gp = self.gadj(tmps,mode="undirected", weighted=True, diag=False)
                tmp[idxtmp] = self.igraph.evcent(gp)[0]
                
            return tmp
        else:
            return False
