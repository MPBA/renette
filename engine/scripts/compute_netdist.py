from rpy2.rinterface._rinterface import RRuntimeError
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import DataFrame, ListVector
import rpy2.rlike.container as rlc
from rpy2.robjects.numpy2ri import numpy2ri
import rpy2.rinterface as ri
import numpy as np
import os.path


class NetDist:
    
    def __init__(self, filelist, param={}):
        self.nfiles = len(filelist)
        try:
            self.nfiles > 2
        except ValueError:
            print "Not enough file loaded"
            
        self.filelist = filelist
        self.param = param
        self.mylist = rlc.TaggedList([])
        
    def loadfiles(self):
        """
        Load files into R environment
        """
        rcount = 0
        asmatrix = robjects.r['as.matrix']

        
        ## Set the default parameter for reading from csv
        param = {'sep': '\t', 'header': True, 'as_is': True, 'row.names': ri.NULL}
        
        ## Check the correct parameter and set the default        
        for p in param.keys():
            if p in self.param:
                if self.param[p] is not None:
                    param[p] = self.param[p]
        
        for f in self.filelist:
            try:
                dataf = DataFrame.from_csvfile(f,
                                               sep=param['sep'],
                                               header=param['header'],
                                               as_is=param['as_is'],
                                               row_names=param['row.names'])

                dataf = asmatrix(dataf)
                self.mylist.append(dataf)
                rcount += 1
            except IOError:
                print "Can't load file %s" % f

        if rcount == self.nfiles:
            return True
        else:
            return False

    def compute(self):
        """
        Compute the distances between adjacency matrices using nettools
        package

        """
        
        nettools = importr('nettools')
        ## robjects.conversion.py2ri = numpy2ri
        param = {'d': 'HIM', 'ga': ri.NULL, 'components': True, 'rho': 1}
        
        ## Check the correct parameter and set the default
        for p in param.keys():
            if p in self.param:
                if self.param[p] is not None:
                    param[p] = self.param[p]

        try:
            self.res = nettools.netdist(self.mylist,
                                        d=param['d'],
                                        components=param['components'],
                                        ga=param['ga'], **{'n.cores': 1})
            print len(self.res)
            
            return_value = True
        except ValueError, e:
            print 'Error in computing network distance: %s' % str(e)
            return_value = False
        except RRuntimeError, e:
            print 'Error in computing network distance: %s' % str(e)
            return_value = False

        self.computed = return_value
        return return_value

    def get_results(self, filepath='.'):
        lapply = robjects.r['lapply']
        write_table = robjects.r['write.table']
        names = robjects.r['names'] 
        
        if self.computed:
            for i in range(len(self.res)):
                myfname = os.path.join(filepath, 
                                       names(self.res)[i] + '_distance.tsv')
                try :
                    ll = len(self.res[i]) 
                    if (ll == 1):
                        colnames = False
                        rownames = False
                    else:
                        colnames = robjects.NA_Integer
                        rownames = True
                except:
                    colnames = False
                    rownames = False
                    
                write_table(self.res[i],myfname, sep=self.param['sep'], 
                            quote=False,
                            **{'col.names': colnames,
                               'row.names': rownames})
            return True
        else:
            print "No distance computed"
            return False
