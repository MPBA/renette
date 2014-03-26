from itertools import combinations
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.numpy2ri import numpy2ri
from rpy2.robjects.vectors import DataFrame
from random import randrange
import numpy as np
import os.path
import csv
import json



def write_Sw (Sw, N, filename='Sw.csv'):
    """
    Write file for edge stability indicator
    """
    try:
        f = open(filename, 'wb')
        fw = csv.writer(f, delimiter='\t', lineterminator='\n')
    except IOError, e:
        print '%s' % e
        return False
        
    fw.writerow(['from', 'to', 'Sw'])
    # Create link combinations
    links = combinations(range(N),2)
    
    for j,l in zip(range(Sw.shape[0]),links):
        ll = list(l)
        # Set 1 based index
        ll = [x + 1 for x in ll]
        Swval = Sw[j,:].mean()
        # use np.allclose()
        if (not np.isclose(Swval,0.0)):
            Swval = (Sw[j,:].max() - Sw[j,:].min()) / Sw[j,:].mean()
        
        ll.append(Swval)
        fw.writerow(ll)
    f.close()
        
    return True

def write_Sd(Sd, filename='Sd.csv'):
    """
    Write degree stability indicator file
    """
    try:
        f = open(filename, 'w')
        fw = csv.writer(f, delimiter='\t', lineterminator='\n')
    except IOError, e:
        print '%s' % e
        return False


    fw.writerow(['node', 'Sd'])
    for j in xrange(Sd.shape[1]):
        try:
            Sdval = (Sd[:,j].max() - Sd[:,j].min()) / Sd[:,j].mean()
        except:
            Sdval = 0.0
        # write 1-based index
        fw.writerow([j+1,Sdval])
    
    f.close()
    
    return True


def export_graph(reslist, i, filepath='.',format='gml',  prefix='graph_',  weight=True):
    """
    Export to the desired graph format
    """
    igraph = importr('igraph')
    gadj = igraph.graph_adjacency
    wgraph = igraph.write_graph
    
    myfname = prefix + str(i) + '.%s' % format  
    g = gadj(reslist, mode='undirected', weighted=weight)
    wgraph(g, file=os.path.join(filepath,myfname), format=format)
    
    return myfname
    
def export_to_json(reslist, i, filepath='.', perc=10, prefix='graph_', weight=True ):
    """
    Create the json for d3js visualization
    """
    
    igraph = importr('igraph')
    gadj = igraph.graph_adjacency
    direct = 'directed'
    
    # Write a graph file for each result
    response = {'nodes': [], 'edges': []}
    tmpr = np.array(reslist)
    
    # Check if the matrix is symmetric
    ck = (np.triu(tmpr).transpose() - np.tril(tmpr))
    if not ck.all():
        direct = 'undirected'
        tmp = np.triu(tmpr)
    else:
        tmp = tmpr
    
    # Apply thresholding
    try:
        thr = np.percentile(tmp[tmp > 0.0], 100-perc)
    except:
        thr = 0.0
    
    # Create the graph object
    g = gadj(reslist, mode=direct, weighted=weight, diag=False)
    
    # Check for weights attribute
    if weight:
        ww = igraph.get_edge_attribute(g, "weight")
    else:
        ww = ri.NULL
    
    # Get x-y coords for graph visualization
    # Set the limit given by the sigmajs constrains
    minx = [0 for i in xrange(tmp.shape[0])]
    maxx = [i + 1100 for i in minx]
    maxy = [i + 600 for i in minx]
    gcoord = igraph.layout_fruchterman_reingold(g, weights=ww, 
                                                minx=minx, maxx=maxx,
                                                miny=minx, maxy=maxy)
    gcoorda = np.array(gcoord)
    
    # Get communities 
    gmm = igraph.spinglass_community(g, weights=ww)
    mm = igraph.membership(gmm)
    cm = np.empty(len(mm), dtype='S8')
    
    # Assign color to each community
    for m in np.unique(mm):
        cc = "#%s" % "".join([hex(randrange(0, 255))[2:] for i in range(3)])
        cm[mm==m] = cc
    
    # Write nodes specifications
    for n in range(tmp.shape[1]):
        try:
            mynode = reslist.colnames[n]
        except:
            mynode = n
        
        response['nodes'].append({'label': 'Degree = %.3f\nCluster = %d' % (tmpr[n,:].sum(), mm[n]), 
                                  'id': 'n%d' % n,
                                  'size': '%.2f' % tmpr[n,:].sum(), 
                                  'x': gcoorda[n,0],
                                  'y': gcoorda[n,1],
                                  'cluster': mm[n],
                                  'color': cm[n]})
    
    # Write links specifications
    N = tmp.shape[1]
    for n in xrange(tmp.shape[1]):
        if direct == "undirected":
            start = n + 1
        else:
            start = 1
        for j in xrange(start,N):
            if (tmp[n,j] >= thr):
                response['edges'].append({
                                          'id': 'e%d-%d' % (n, j),
                                          'source':  'n%d' % n,
                                          'target':  'n%d' % j,
                                          'weights': tmp[n, j]})
    
    # Write json file for sigmajs
    try:
        myfname = prefix + str(i) + '.json'
        f = open(os.path.join(filepath, myfname),'w')
        json.dump(response,f,ensure_ascii=False)
        f.close()
    except IOError, e:
        print "Error writing the file %s" % e
            
    return myfname

    
def csv2graph(csvfiles, seplist=[], param={},filepath='.', graph_format='gml'):
    """
    Utility to convert from csv file to igraph format file
    """
    
    igraph = importr('igraph')
    gadj = igraph.graph_adjacency
    wgraph = igraph.write_graph
    
    if len(seplist) != len(csvfiles):
        raise IOError('Not enought separators')
        
    for i,f in enumerate(csvfiles):
        myfname = f + ".%s" % format
        tmpdata = DataFrame.from_csvfile(f,
                                         sep=seplist[i],
                                         header=param['header'] if param.has_key('header') else True,
                                         as_is=True,
                                         row_names=param['row.names'] if param.has_key('row_names') else False)
        g = gadj(reslist, mode='undirected', weighted=True)
        wgraph(g, file=os.path.join(filepath,myfname), format=format)
        
    return True

    
def plot_mds (results, i, filepath='.', prefix='mds_'):
    """
    Plot the mds of the distances
    """
    grdevices = importr('grDevices')
    asdist = robjects.r['as.dist']
    
    myfname = prefix + str(i) + '.png'
    
    mm = robjects.r.cmdscale(asdist(results),eig=True)
    mmp = mm[0]
    
    print "MDS %s" % filepath
    
    grdevices.png(file=os.path.join(filepath, myfname), width=512, height=512)
    robjects.r.plot(mmp.rx(True,1),mmp.rx(True,2), type="n", col='red',
                    ylab='Coord. 2', xlab='Coord. 1', main='Multi-Dimensional Scaling plot')
    robjects.r.text(mmp.rx(True,1),mmp.rx(True,2), mmp.rownames)
    grdevices.dev_off()
    
    return myfname
        

def igraph_layout (adjmat):
    """
    """
    igraph = importr('igraph')
    
    
    
def plot_degree_distrib(adj_mat, i, filepath='.', prefix='ddist_'):
    """
    Compute degree distribution and plot using lattice
    """
    
    lattice = importr('lattice')
    grdevices = importr('grDevices')
    xyplot = lattice.xyplot
    rprint = robjects.globalenv.get("print")
    
    deg = robjects.r.rowSums(adj_mat)
    degdens = robjects.r.density(deg)
    
    myf = robjects.Formula('y ~ x')
    myf.getenvironment()['x'] = degdens.rx2['x']
    myf.getenvironment()['y'] = degdens.rx2['y']
    p = xyplot(myf, type='l', lwd=3, 
               xlab='Node Degree', ylab='Density',
               main='Node degree distribution')
    
    myfname = prefix + str(i) + '.png'
    grdevices.png(file=os.path.join(filepath, myfname), width=512, height=512)
    rprint(p)
    grdevices.dev_off()
    
    return myfname


def plot_edge_distrib(adj_mat, i, filepath='.', prefix='edist_'):
    """
    Compute degree distribution and plot using lattice
    """
    
    lattice = importr('lattice')
    grdevices = importr('grDevices')
    xyplot = lattice.densityplot
    uptri = robjects.r['upper.tri']
    rprint = robjects.globalenv.get("print")
    
    idx = robjects.r.c(uptri(adj_mat))
    
    deg = robjects.r.c(adj_mat.rx(idx))
    p = xyplot(deg, type='l', lwd=3, 
               xlab='Edge Degree', ylab='Density',
               main='Edge weight degree distribution', **{'plot.points':False})
    
    myfname = prefix + str(i) + '.png'
    grdevices.png(file=os.path.join(filepath, myfname), width=512, height=512)
    rprint(p)
    grdevices.dev_off()
    
    return myfname

def plot_degree_stab(dstab, i, myd, filepath=".", prefix='dstab_'):
    """
    Plot degree stability over resamplings
    """
    
    lattice = importr('lattice')
    grdevices = importr('grDevices')
    levelplot = lattice.levelplot
    rprint = robjects.globalenv.get("print")
    
    mat = dstab/myd - 1
    p = levelplot(numpy2ri(mat), 
                  xlab='Resamplings', ylab='Nodes', 
                  main='Variation of node degree across resamplings',
                  aspect='xy'
    )
    
    myfname = prefix + str(i) + '.png'
    grdevices.png(file=os.path.join(filepath, myfname), width=512, height=512)
    rprint(p)
    grdevices.dev_off()
    
    return myfname

def get_hubs (adj_mat, i, quart=90, stab_mat=[], stab_mat_all=[], filepath=".", prefix="hubs"):
    
    """
    Find hubs in an adjacency matrix
    NB Suppose matrices are weighted and undirected
    """
    
    names = robjects.r['colnames']
    grdevices = importr('grDevices')
    rprint = robjects.globalenv.get("print")
    boxplot = robjects.r['boxplot']
    points = robjects.r['points']
    
    adjmat = np.array(adj_mat)
    deg = adjmat.sum(axis=1)
    
    ## Set hub percentile to 90 [1,100]
    thr = np.percentile(deg, quart)
    
    idx = np.where(deg>=thr)[0]
    ii = np.argsort(deg[idx])[::-1]
    
    try:
        nn = names(adj_mat)
    except:
        nn = []
        
    myfname = '%s_%d.tsv' % (prefix, i)
    filename = os.path.join(filepath, myfname)
    
    try:
        f = open(filename, 'wb')
        fw = csv.writer(f, delimiter='\t', lineterminator='\n')
    except IOError, e:
        print '%s' % e
    
    fw.writerow(['Node Id', 'Node Degree', 'Stability' if stab_mat else None])

    for j in ii:
        fw.writerow([nn[idx[j]] if nn else idx[j], deg[idx[j]], 
                     stab_mat[idx[j]] if stab_mat else None])
    f.close()
    if stab_mat_all:
        ridx = robjects.IntVector(idx[ii] + 1) # NB R indexing starts from 1
        pname = '%s_%d.png' % (prefix, i)
        bnames = names(stab_mat_all)
        if not bnames:
            bnames = robjects.StrVector(['Node_%d' % n for n in (idx[ii] + 1)])

        ## Plotting hubs stability
        grdevices.png(file=os.path.join(filepath,pname), width=512, height=512)
        boxplot(stab_mat_all.rx(True, ridx), names=bnames, col='grey80')
        points(robjects.IntVector(np.arange(len(ii)) + 1), 
               robjects.FloatVector(deg[idx[ii]]), pch=19)
        grdevices.dev_off()
        myfname = [myfname, pname]
        
    return myfname
