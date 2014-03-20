from rpy2.rinterface._rinterface import RRuntimeError
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import DataFrame, ListVector
import rpy2.rlike.container as rlc
from rpy2.robjects.numpy2ri import numpy2ri
import rpy2.rinterface as ri
import numpy as np
import os.path
import rutils as ru

class NetDist:
    
    def __init__(self, filelist, seplist, param={}):
        """
        Initialize variables needed for the computation
        """
        self.nfiles = len(filelist)
        self.filelist = filelist
        self.seplist = seplist
        # Check if the number of separators are equal to the numberr of file passed
        if len(self.filelist) != len(self.seplist):
            raise IOError('Not enough separators!')
        self.param = param
        self.mylist = rlc.TaggedList([])
        self.results = {}
        ## Warning message: diagonal not 0
        self.listname = []
        self.error = []
        # self.e = []
        # self.stat = 'Success'
        # # self.dflag = False
        
    def loadfiles(self):
        """
        Load files into R environment
        """
        rcount = 0
        asmatrix = robjects.r['as.matrix']
        diag = robjects.r['diag']
        names = robjects.r['names']
        
        ## Set the default parameter for reading from csv
        param = {'header': True, 'as_is': True, 'row.names': ri.NULL}
        
        ## Check the correct parameter and set the default        
        for p in param.keys():
            if p in self.param:
                if self.param[p] is not None:
                    param[p] = self.param[p]
        
        
        for f, s in zip(self.filelist, self.seplist):
            try:
                dataf = DataFrame.from_csvfile(f,
                                               sep=str(s),
                                               header=param['header'],
                                               as_is=param['as_is'],
                                               row_names=param['row.names'])

                dataf = asmatrix(dataf)
                
                # Should be the diagonal set to 0?
                # Do it for all the inputs, just to be sure
                zcount = 0
                for i in xrange(dataf.ncol):
                    if (dataf.rx[i+1,i+1][0] - 0.0 >= 1e-8):
                        zcount += 1
                        dataf.rx[i+1,i+1] = 0
                
                if zcount:
                    self.e += f
                    
                self.mylist.append(dataf)
                rcount += 1
            except IOError, e:
                self.error += e
            
            except RRuntimeError, e:
                self.error += e
                
        # if self.e:
        #     self.e += 'Diagonal has values different from 0. \nSelf loop are not support in the current version.\nAutomatically set to 0 for the network computation in file:'
        #     self.e.reverse()
        #     self.stat = 'Warning'

        if rcount == self.nfiles:
            return True
        else:
            raise False # IOError('Cannot read all the files')
            
    def compute(self):
        """
        Compute the distances between adjacency matrices using nettools
        package

        """
        nettools = importr('nettools')
                
        param = {'d': 'HIM', 'ga': ri.NULL, 'components': True, 'rho': 1}
        
        ## Check the correct parameter and set the default
        for p in param.keys():
            if p in self.param:
                if self.param[p] is not None:
                    param[p] = self.param[p]
        
        ## If one file is passed, then compute the distance with the empty network
        if self.nfiles == 1:
            tmp = np.array(self.mylist[0])
            # Create the empty network
            emp = robjects.r.matrix(0,nrow=tmp.shape[0], ncol=tmp.shape[1])
            # Append to the data list
            self.mylist.append(emp)
            
            # Update the list of 'input' files
            self.filelist += ['empty'] 
            
            # Check if there are other warnings
            self.e += ['One file provided: computing distance between %s and empty network' % self.filelist[0]]
            self.stat = 'Warning'
                    
        try:
            self.res = nettools.netdist(self.mylist,
                                        d=param['d'],
                                        components=param['components'],
                                        ga=param['ga'], **{'n.cores': 1})
            return_value = True
        except ValueError, e:
            return_value = False
            self.error += e
            ## print 'Error in computing network distance: %s' % str(e)
            
        except RRuntimeError, e:
            return_value = False
            self.error += e
            ## print 'Error in computing network distance: %s' % str(e)
            
            
        self.computed = return_value
        return return_value
    
    def get_results(self, filepath='.', export_json=True, graph_format='gml', plot=True, perc=30):
        
        """
        Get the results and save to csv files
        """
        
        lapply = robjects.r['lapply']
        write_table = robjects.r['write.table']
        names = robjects.r['names']
        rlist = robjects.r['list']
        results = {}
        
        
        if self.computed:
            for i in xrange(len(self.res)):
                print 'get_result1 %s' % filepath
                myfname = os.path.join(filepath,
                                       names(self.res)[i] + '_distance.tsv')
                print 'myfname %s' % myfname
                self.results[names(self.res)[i]] = {
                    'csv_files': [names(self.res)[i] + '_distance.tsv'],
                    'img_files': [],
                    'json_files': [],
                    'graph_files': [],
                    'desc': '%s network distance' % names(self.res)[i],
                    'rdata': None,
                    # 'messages': [ self.e if self.e else ''],
                    # 'status': [ self.stat ]
                }

                try:
                    len(self.res[i])
                    tmp = self.res[i]
                    
                    colnames = ri.StrSexpVector([os.path.basename(f) for f in self.filelist])
                    rownames = ri.StrSexpVector([os.path.basename(f) for f in self.filelist])
                    
                    tmp.do_slot_assign("dimnames", rlist(
                        ri.StrSexpVector(colnames),
                        ri.StrSexpVector(rownames)
                    ))
                except Exception:
                    tmp = robjects.r.matrix(self.res[i], ncol=1, nrow=1)
                    tmp.do_slot_assign("dimnames", rlist(
                        ri.StrSexpVector([os.path.basename(self.filelist[0])]),
                        ri.StrSexpVector([os.path.basename(self.filelist[1])])
                    ))

                write_table(tmp, myfname, sep='\t',
                            quote=False,
                            **{
                                'col.names': ri.NA_Logical,
                                'row.names': True
                            })
                
                print 'get_result2 %s' % filepath
                if self.nfiles > 2:
                    try:
                        mds = ru.plot_mds(self.res[i],i, filepath = filepath,
                                         prefix=names(self.res)[i] + '_distance')
                        self.results[names(self.res)[i]]['img_files'] += [mds]
                        ## self.results[names(self.res)[i]]['img_files'] += [names(self.res)[i] + '_distance.png']
                    except RRuntimeError, e:
                        self.error += e
                        # if self.stat == 'Success':
                        #     self.stat = 'Warning'
                        # self.e += [e]
            
            return self.results
        else:
            self.error += 'No distance computed'
            return self.error

    def save_RData(self, filepath='.', filename='dists.RData'):

        """
        Store the variables just computed in the globalenv to an RData
        """
        
        names = robjects.r['names']
        
        # Varname contains the names of the variables stored in the RData
        resname = names(self.res)
        varname = ri.StrSexpVector(resname)
        ri.globalenv['varname'] = varname
        save_image = robjects.r['save.image']
        
        try:
            for i,f in enumerate(resname):
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


