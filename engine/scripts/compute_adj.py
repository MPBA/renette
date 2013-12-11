import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import DataFrame
import rpy2.rlike.container as rlc
from rpy2.robjects.numpy2ri import numpy2ri
import numpy as np

class Mat2Adj:
    
    def __init__(self, filelist,method='cor',param = {'sep':'\t','header':True, 'as_is':True}):
        """
        Import the needed functions and packages to be available for computation
        """
        self.method = method
        self.filelist = filelist
        self.nettools = importr('nettools')
        self.lapply = robjects.r['lapply']
        self.mylist = rlc.TaggedList([])
        self.nfiles = len(filelist)
        self.param = param
        
    def loadfiles(self):
        rcount = 0
        for f in self.filelist:
            try:
                #tmpdata = DataFrame.from_csvfile(f, sep = "\t", header = True, as_is=True)      
                tmpdata = DataFrame.from_csvfile(f, \
                                                 sep=self.param['sep'],\
                                                 header=self.param['header'],\
                                                 as_is=self.param['as_is'])     
                self.mylist.append(tmpdata)
                rcount += 1
            except IOError:
                print "Can't load file %s" %f
                
        if rcount == self.nfiles:
            return True
        else:
            return False
            
    
    def compute(self):
        try:
            self.res = self.lapply(self.mylist,self.nettools.mat2adj,method=self.method)
            return_value = True
        except ValueError:
            return_value = False
        
        self.computed = return_value
        return return_value

    def get_results(self):
        if self.computed:
            return self.res
        else:
            print "No adjacency matrix computed"
            
