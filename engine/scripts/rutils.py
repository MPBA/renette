from itertools import combinations
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.numpy2ri import numpy2ri
from rpy2.robjects.vectors import DataFrame
import numpy as np
import os.path
import csv
import json

def write_Sw (Sw, filename='Sw.csv'):
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
    links = combinations(xrange(Sw.shape[0]),2)
    for j,l in zip(range(Sw.shape[0]),links):
        ll = list(l)
        # Set 1 based index
        ll = [x + 1 for x in ll]
        if (Sw[j,:].mean() != 0.0):
            Swval = (Sw[j,:].max() - Sw[j,:].min()) / Sw[j,:].mean()
        else:
            Swval = 0.0
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


def export_graph(reslist, i, filepath='.',format='gml'):
    """
    Export to the desired graph format
    """
    igraph = importr('igraph')
    gadj = igraph.graph_adjacency
    wgraph = igraph.write_graph
    
    #for i,r in enumerate(reslist):
    myfname = 'graph_' + str(i) + '.%s' % format  
    g = gadj(reslist, mode='undirected', weighted=True)
    wgraph(g, file=os.path.join(filepath,myfname), format=format)
        
    return myfname

def export_to_json(reslist, i, filepath=".", perc=10):
    """
    Create the json for d3js visualization
    """
    
    # Write a graph file for each result
    #for i,r in enumerate(reslist):
    response = {'nodes': [], 'links': []}
    tmp = np.triu(np.array(reslist))
    thr = np.percentile(tmp[tmp>0.0],100-perc)
        
        # Write nodes specifications
    for n in range(tmp.shape[1]):
        response['nodes'].append({'name': str(n), 'group':0})
            
    # Write links specifications
    N = tmp.shape[1]
    for n in range(tmp.shape[1]):
        for j in range(n+1,N):
            if (tmp[n,j] >= thr):
                ## print 'n %d, j%d' % (n,j)
                response['links'].append({'source': n, 
                                          'target': j, 
                                          'values': tmp[n,j]})
                
    # Write json file for d3js
    try:
        myfname = 'graph_' + str(i) + '.json'
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

    
