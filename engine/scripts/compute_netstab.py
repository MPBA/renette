import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import DataFrame
import rpy2.rlike.container as rlc
from rpy2.robjects.numpy2ri import numpy2ri
import rpy2.rinterface as ri
import numpy as np
import os.path


class NetStability:
    
    def __init__(self, filelist, seplist, param={}):
        
        self.filelist = filelist
        self.seplist = seplist
        if len(self.filelist) != len(self.seplist):
            raise IOError('Not conformable arrays')
                    
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
        for f, s in zip(self.filelist, self.seplist):
            try:
                tmpdata = DataFrame.from_csvfile(f,
                                                 sep=str(s),
                                                 header=param['header'],
                                                 as_is=param['as_is'],
                                                 row_names=param['row.names'])
                self.mylist.append(tmpdata)
                self.listname.append('stab_'+str(rcount))
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
        
        # Get parameter and set default
        param = {'indicator': 'all', 'd': 'HIM', 'adj_method': 'cor', 
                 'method': 'montecarlo', 'k': 3, 'h': 20, 'FDR': 1e-3, 
                 'P': 6, 'measure': ri.NULL, 'alpha': 0.6, 'C': 15, 'DP': 1, 
                 'save': True}
        for p in param.keys():
            if p in self.param:
                if self.param[p] is not None:
                    param[p] = self.param[p]

        # Start the computation
        try:
            # Test if the computation is ok
            self.res = []
            
            for x in self.mylist:
                self.res.append(nettools.netSI(x,
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
                                               save=param['save'],
                                               tol=0,
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
        """
        Write the results on the file system
        """
                
        names = robjects.r['names']
        write_table = robjects.r['write.table']
        results = {}
        
        if self.computed:
            for i in range(len(self.res)):
                
                tmp = self.res[i]
                myfname = os.path.join(filepath, '%s_ADJ.tsv' % self.listname[i] )
                # Write result dictionary
                results[self.listname[i]] = {
                    'csv_files': ['%s_ADJ.tsv' % self.listname[i]],
                    'img_files': [],
                    'desc': '%s is bla bla bla bla' % self.listname[i],
                    'rdata': None,
                }
                
                # Write adjacency matrix on the whole dataset
                write_table(tmp.rx2('ADJ'),myfname,
                            sep='\t', quote=False, 
                            **{'col.names': robjects.NA_Logical, 
                               'row.names': True})
                
                # Write matrices given by resampling
                for j, a in enumerate(tmp.rx2('ADJlist')):
                    myfname = os.path.join(filepath, '%s_ADJ_res%d.tsv' 
                                           % (self.listname[i], j) )
                    results[self.listname[i]]['csv_files'] += ['%s_ADJ_res%d.tsv' % (self.listname[i], j)]
                    write_table(tmp.rx2('ADJ'),myfname,
                                sep='\t', quote=False, 
                                **{'col.names': robjects.NA_Logical, 
                                   'row.names': True})
            return results
        else:
            return False



    
