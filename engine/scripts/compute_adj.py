from rpy2.rinterface._rinterface import RRuntimeError
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import DataFrame
import rpy2.rlike.container as rlc
from rpy2.robjects.numpy2ri import numpy2ri
import rpy2.rinterface as ri
import numpy as np
import os.path
import csv
import json
import rutils as ru


class Mat2Adj:
    
    def __init__(self, filelist, seplist, param={}):
        """
        Import the needed functions and packages to be available for computation
        """
        self.nfiles = len(filelist)
        self.filelist = filelist
        self.seplist = seplist
        self.results = {}
        # Check if the number of separators are equal to the numberr of file passed
        if len(self.filelist) != len(self.seplist):
            raise IOError('Not enough separators!')
            
        self.param = param
        self.mylist = rlc.TaggedList([])
        self.listname = []
        
    def loadfiles(self):
        """
        Load files into R environment
        """
        rcount = 0
        names = robjects.r['names']
        
        # Set the default parameter for reading from csv
        param = {'sep': '\t', 'header': True, 'as_is': True,
                 'row.names': ri.NULL}


        # Check the correct parameter and set the default        
        for p in param.keys():
            if p in self.param:
                if self.param[p] is not None:
                    param[p] = self.param[p]
        
        self.param.update(param)

        # Read all the files in the R-environment
        for f, s in zip(self.filelist, self.seplist):
            try:
                tmpdata = DataFrame.from_csvfile(f,
                                                 sep=str(s),
                                                 header=param['header'],
                                                 as_is=param['as_is'],
                                                 row_names=param['row.names'])
                self.mylist.append(tmpdata)
                fdir, fname = os.path.split(os.path.splitext(f)[0])
                self.listname.append(fname)
                rcount += 1
            except IOError:
                print "Can't load file %s" %f
                
        if rcount == self.nfiles:
            return True
        else:
            return False
            
    
    def compute(self):
        """
        Compute adjacency matrices using package nettools
        """
        
        nettools = importr('nettools')
        lapply = robjects.r['lapply']
        
        # Get patameter and set default
        param = {'method':'cor', 'FDR':1e-3, 'P':6, 
                 'measure':ri.NULL, 'alpha': 0.6, 'C':15, 'DP':1}
        for p in param.keys():
            if p in self.param:
                if self.param[p] is not None:
                    param[p] = self.param[p]
        
        # Compute the adjacency matrices
        try:
            self.res = lapply(self.mylist,nettools.mat2adj,
                                   method=param['method'], FDR=param['FDR'],
                                   P=param['P'],measure=param['measure'],
                                   alpha=param['alpha'],DP=param['DP'],
                                   tol=0.0)
            return_value = True
        except ValueError:
            return_value = False
        
        self.computed = return_value
        return return_value

    def get_results(self, filepath='.', export_json=True, graph_format="gml", perc=30):
        """
        Get the results and write to a file
        """

        lapply = robjects.r['lapply']
        write_table = robjects.r['write.table']
        names = robjects.r['names']
        rlist = robjects.r['list']
        rmat = robjects.r['as.matrix']

        if self.computed:
            for i in range(len(self.res)):
                myfname = os.path.join(filepath,
                                       self.listname[i] + '_adj.tsv')
                
                self.results[self.listname[i]] = {
                    'csv_files': [self.listname[i] + '_adj.tsv'],
                    'img_files': [],
                    'json_files': [],
                    'graph_files': [],
                    'desc': '%s_%s computed with %s' % (self.listname[i], 'adj.tsv', self.param['method']) ,
                    'rdata': None,
                    'messages': [],
                    'status': []
                }
                
                try:
                    len(self.res[i])
                    ll = len(self.res[i])
                    if (ll == 1):
                        colnames = False
                        rownames = False
                    else:
                        colnames = robjects.NA_Logical
                        rownames = True
                except:
                    colnames = False
                    rownames = False
                
                print colnames, rownames
                # Write files csv ; separated
                write_table(self.res[i], myfname, sep='\t',
                            quote=False,
                            **{
                                'col.names': colnames,
                                'row.names': rownames
                            })
                # Export to json
                if export_json:
                    jname = ru.export_to_json(self.res[i], i=i, filepath=filepath, 
                                              perc=perc, 
                                              prefix='%s_%s_' % (self.listname[i], self.param['method']))
                    self.results[self.listname[i]]['json_files'] += [jname]

                # Export to graph format
                if graph_format:
                    gname = ru.export_graph(self.res[i], i=i, 
                                            filepath=filepath, 
                                            format=graph_format,
                                            prefix='%s_%s_' % (self.listname[i], self.param['method']))
                    self.results[self.listname[i]]['graph_files'] += [gname]
                    
            return self.results
        else:
            print 'No adjacency matrix computed, please run the compute method before.'
            return False
    
    def save_RData(self, filepath='.', filename='adj.RData'):

        """
        Store the variables just computed in the globalenv to an RData
        """
        
        # Varname contains the names of the variables stored in the RData
        varname = ri.StrSexpVector(self.listname)
        ri.globalenv['varname'] = varname
        save_image = robjects.r['save.image']
        
        try:
            for i,f in enumerate(self.listname):
                # Register the current result to the global environment
                ri.globalenv[f] = self.res[i]
            save_image(file=os.path.join(filepath,filename))
            return True
        except IOError, e:
            print 'No results found: %s' % str(e)
            return False
        except RRuntimeError, e:
            print 'No results found: %s' % str(e)
            return False
            
    def get_results_fromRData(self, filepath=".", filename='adj.RData'):
        
        """
        Get the results from a previously stored RData
        """
        
        try: 
            robjects.r.load(os.path.join(filepath, filename))
            varname = ri.globalenv.get('varname')
            for i in varname:
                myres = ri.globalenv.get(i)
                print 'Found variable %s, with dim= %s' % (i, np.array(myres).shape)
            return True
        except IOError, e:
            print 'No objects found in the %s file' % filename
            return False
        except RRuntimeError, e:
            print 'No oject found in this %s: %s' % (filename, str(e))
            return False

    # def export_to_json(self, filepath=".", perc=90):
    #     """
    #     Create the json for d3js visualization
    #     """
    #     # Write a graph file for each result
    #     for i,r in enumerate(self.res):
    #         response = {'nodes': [], 'links': []}
    #         tmp = np.triu(np.array(self.res[i]))
    #         thr = np.percentile(tmp[tmp>0.0],100-perc)
            
    #         # Write nodes specifications
    #         for n in range(tmp.shape[1]):
    #             response['nodes'].append({'name': str(n), 'group':0})
            
    #         # Write links specifications
    #         N = tmp.shape[1]
    #         for n in range(tmp.shape[1]):
    #             for j in range(n+1,N):
    #                 if (tmp[n,j] >= thr):
    #                     ## print 'n %d, j%d' % (n,j)
    #                     response['links'].append({'source': n, 
    #                                                  'target': j, 
    #                                                  'values': tmp[n,j]})
                
    #         # Write json file for d3js
    #         try:
    #             myfname = 'graph_' + str(i) + '.json'
    #             f = open(os.path.join(filepath, myfname),'w')
    #             json.dump(response,f,ensure_ascii=False)
    #             f.close()
    #         except IOError, e:
    #             print "Error writing the file %s" % e
        
    #     return True
    
    # def export_graph(self, filepath='.',format='gml'):
    #     """
    #     Export to the desired graph format
    #     """
    #     lapply = robjects.r['lapply']
    #     igraph = importr('igraph')
    #     gadj = igraph.graph_adjacency
    #     wgraph = igraph.write_graph
        
    #     for i,r in enumerate(self.res):
    #         myfname = 'graph_' + str(i) + '.%s' % format  
    #         g = gadj(r, mode='undirected', weighted=True)
    #         wgraph(g, file=os.path.join(filepath,myfname), format=format)
    #         # tmp = np.array(r)
    #         # tmp = tmp.tolist()
    #         # ## print tmp
    #         # gg = igraph.Graph.Adjacency(tmp, mode=igraph.ADJ_UNDIRECTED)
    #         # print gg.get_adjacency()
            
    #     return 0
