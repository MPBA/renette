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

class Mat2Adj:
    
    def __init__(self, filelist, param={}):

        """
        Import the needed functions and packages to be available for computation
        """
        
        self.filelist = filelist
        self.mylist = rlc.TaggedList([])
        self.nfiles = len(filelist)
        self.param = param
        
    def loadfiles(self):
        
        """
        Load files into R environment
        """
        
        self.listname = []
        rcount = 0
        names = robjects.r['names'] 
        
        # Set the default parameter for reading from csv
        param = {'sep':'\t', 'header': True, 'as_is':True, 
                 'row.names': ri.NULL}
        # Check the correct parameter and set the default        
        for p in param.keys():
            if p in self.param:
                if self.param[p] is not None:
                    param[p] = self.param[p]
        
        # Read all the files in the R-environment
        for f in self.filelist:
            try:
                tmpdata = DataFrame.from_csvfile(f,
                                                 sep=param['sep'],
                                                 header=param['header'],
                                                 as_is=param['as_is'],
                                                 row_names=param['row.names'])
                self.mylist.append(tmpdata)
                self.listname.append('adj_mat_'+str(rcount))
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
                                   alpha=param['alpha'],DP=param['DP'])
            return_value = True
        except ValueError:
            return_value = False
        
        self.computed = return_value
        return return_value

    def get_results(self, filepath='.'):
        
        """
        Get the results and write to a file
        """

        lapply = robjects.r['lapply']
        write_table = robjects.r['write.csv2']
                
        if self.computed:
            for i in range(len(self.res)):
                myfname = os.path.join(filepath,
                                       self.listname[i] + '_adj.tsv')
                try :
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
                    
                # Write files csv ; separated
                write_table(self.res[i],myfname,
                            quote=False)
            return True
        else:
            print 'No adjacency matrix computed, please run the compute method before.'
    
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

    def export_to_json(self, perc=90):
        """
        Create the json for d3js visualization
        """
        
        # Write a graph file for each result
        for i,r in enumerate(self.res):
            response = [{'nodes': [], 'links': []}]
            tmp = np.triu(np.array(self.res[i]))
            thr = np.percentile(tmp[tmp>0.0],100-perc)
            
            # Write nodes specifications
            for n in range(tmp.shape[1]):
                response[0]['nodes'].append({'name': str(n), 'group':0})
            
            # Write links specifications
            N = tmp.shape[1]
            for n in range(tmp.shape[1]):
                for j in range(n+1,N):
                    if (tmp[n,j] >= thr):
                        print 'n %d, j%d' % (n,j)
                        response[0]['links'].append({'source': str(n), 
                                                     'target':str(j), 
                                                     'values':tmp[n,j]})
                
            # Write json file for d3js
            try:
                f = open('graph_' + str(i) + '.json','w')
                json.dump(response,f)
                f.close()
            except IOError, e:
                print "Error writing the file %s" % e
        
        return True
