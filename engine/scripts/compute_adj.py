import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import DataFrame
import rpy2.rlike.container as rlc
from rpy2.robjects.numpy2ri import numpy2ri
import rpy2.rinterface as ri
import numpy as np
import os.path

class Mat2Adj:
    
    def __init__(self, filelist,param = {}):
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
        rcount = 0
        self.listname = []
        names = robjects.r['names'] 
        
        # Set the default parameter for reading from csv
        param = {'sep':'\t', 'header': True, 'as_is':True, 'row.names': ri.NULL}
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
                self.listname.append('file'+str(rcount))
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
        lapply = robjects.r['lapply']
        write_table = robjects.r['write.table']
        names = robjects.r['names'] 
        col_names = robjects.r['colnames']
        row_names = robjects.r['rownames']
        
        print self.param
        
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
                        colnames = True#robjects.NA_Integer
                        rownames = True
                except:
                    colnames = False
                    rownames = False
                
                print col_names(self.res[i])
                print row_names(self.res[i])
                write_table(self.res[i],myfname, sep=self.param['sep'], 
                            quote=False,
                            **{'col.names': colnames,
                               'row.names': rownames})
            return True
        else:
            print "No adjacency matrix computed, please run the compute method before."
            
            
