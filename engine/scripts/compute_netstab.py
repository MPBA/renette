import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import DataFrame
import rpy2.rlike.container as rlc
from rpy2.robjects.numpy2ri import numpy2ri
import rpy2.rinterface as ri
import numpy as np
import os.path


class NetStability:
    
    def __init__(self, filelist, param={}):
        
        self.filelist = filelist
        self.mylist = rlc.TaggedList([])
        self.nfiles = len(filelist)
        self.param = param
        
    def loadfiles (self):

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
        Method for the computation of network stability
        """
        
        nettools = importr('nettools')
        lapply = robjects.r['lapply']
        
        # Get patameter and set default
        param = {'indicator': 'all', 'd': 'HIM', 'adj_method': 'cor', 
                 'method': 'montecarlo', 'k': 3, 'h': 20, 'FDR': 1e-3, 
                 'P': 6, 'measure': ri.NULL, 'alpha': 0.6, 'C': 15, 'DP': 1}
        for p in param.keys():
            if p in self.param:
                if self.param[p] is not None:
                    param[p] = self.param[p]
        
        # Start the computation
        try:
            self.res = []
            
            for i in self.mylist:
                self.res.append(nettools.netSI(i,
                                               indicator=param['indicator'],
                                               d=param['d'],
                                               method=param['method'],
                                               k=param['k'],
                                               h=param['h'],
                                               FDR=param['FDR'],
                                               P=param['P'],
                                               measure=param['measure'],
                                               alpha=param['alpha'],
                                               C=param['C'],
                                               DP=param['DP'], 
                                               **{'adj.method': param['adj_method'],
                                                  'n.cores': 1}))
            return_value = True
            self.computed = True
        except IOError, e:
            self.computed = False
            print 'Error during the computation of the stability indicators: %s' % str(e)
        except ri.RRuntimeError, e:
            self.computed = False
            print 'Error during the computation of the stability indicators: %s' % str(e)
    
    def get_results(self, filepath='.'):
        
        # write_table = robjects.r['write.table']
        names = robjects.r['names']
        if self.computed:
            print names(self.res[0])
            return True
        else:
            raise ValueError('No stability computed')
            return False
        
            