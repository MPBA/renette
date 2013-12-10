import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import DataFrame
import rpy2.rlike.container as rlc
from rpy2.robjects.numpy2ri import numpy2ri
import numpy as np
## robjects.conversion.py2ri = numpy2ri


class NetDist:
    
    def __init__(self, filelist, d="HIM",components=False):
        
        self.nfiles = len(filelist)
        try:
            self.nfiles > 2
        except ValueError:
            print "Not enough file loaded"
             
        self.filelist = filelist
        self.nettools = importr('nettools')
        self.mylist = rlc.TaggedList([])
        
        self.d = d
        self.components = components
        
    def loadfiles(self):
        rcount = 0
        for f in self.filelist:
            try:
                tmpdata = DataFrame.from_csvfile(f, sep = " ", header = True, as_is=True )      
                ## tmpdata = np.genfromtxt(f,)
                self.mylist.append(tmpdata)
                rcount += 1
            except IOError:
                
        if rcount == self.nfiles:
            return True
        else:
            return False


    def compute(self):
        try:
            self.res = nettools.netdist(mylist,d=self.f,components = self.components)
            return_value = True
        except ValueError:
            return_value = False
        
        self.computed = return_value
        return return_value


    def get_results(self):
        if self.computed:
            return self.res
        else:
            print "No distance computed"
