import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import DataFrame, ListVector
import rpy2.rlike.container as rlc
from rpy2.robjects.numpy2ri import numpy2ri
import rpy2.rinterface as ri
import numpy as np



class NetDist:
    
    def __init__(self, filelist, param={}):
        
        self.nfiles = len(filelist)
        try:
            self.nfiles > 2
        except ValueError:
            print "Not enough file loaded"
            
        self.filelist = filelist
        self.nettools = importr('nettools')
        self.mylist = rlc.TaggedList([])
        self.param = param
        
    def loadfiles(self):
        rcount = 0
        asmatrix = robjects.r['as.matrix']
        
        param = {'sep':'\t', 'header': True, 'as_is': True, 'row.names': False}

        for p in param.keys():
            if self.param.has_key(p):
                param[p] = self.param[p]
                
        
        for f in self.filelist:
            try:
                dataf = DataFrame.from_csvfile(f, sep=param['sep'], header=param['header'], as_is=param['as_is'],
                                               row_names=param['row.names'])
                dataf = asmatrix(dataf)
                self.mylist.append(dataf)
                rcount += 1
            except IOError:
                print "Error in loading file %s" % f
        
        if rcount == self.nfiles:
            return True
        else:
            return False


    def compute(self):
        ## robjects.conversion.py2ri = numpy2ri
        param = {'d': 'HIM', 'ga': ri.NULL, 'components': True, 'rho': 1}
        
        for p in param.keys():
            if self.param.has_key(p):
                param[p] = self.param[p]
        try:
            self.res = self.nettools.netdist(self.mylist, d=param['d'], components=param['components'],
                                             ga=param['ga'], **{'n.cores': 2})
            return_value = True
        except ValueError:
            print 'Error in computing network distance'
            return_value = False
        
        
        self.computed = return_value
        return return_value


    def get_results(self):
        if self.computed:
            return self.res
        else:
            print "No distance computed"
