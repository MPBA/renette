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
    
    def __init__(self, filelist, seplist, param={}):
        self.nfiles = len(filelist)
        # if self.nfiles < 2:
        #     raise IOError("Not enough file loaded")
        
        self.filelist = filelist
        self.seplist = seplist
        # Check if the number of separators are equal to the numberr of file passed
        if len(self.filelist) != len(self.seplist):
            raise IOError('Not enough separators!')
        self.param = param
        self.mylist = rlc.TaggedList([])
        self.results = {}
        ## Warning message: diagonal not 0
        self.e = 'Warning: diagonal has values different from 0. \nSelf loop are not support in the current version.\nAutomatically set to 0 for the network computation in file: '
        self.dflag = False
        
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
                    self.dflag = True
                    
                self.mylist.append(dataf)
                rcount += 1
            except IOError, RRuntimeError:
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
        igraph = importr('igraph')
        
        param = {'d': 'HIM', 'ga': ri.NULL, 'components': True, 'rho': 1}
        
        ## Check the correct parameter and set the default
        for p in param.keys():
            if p in self.param:
                if self.param[p] is not None:
                    param[p] = self.param[p]
        
        ## If one file is passed, then compute the distance between empty and full network
        if self.nfiles == 1:
            tmp = np.array(self.mylist[0])
            directed = True
            if np.allclose(tmp.transpose(),tmp):
                directed = False
            
            self.mylist.append(igraph.graph_empty(n=tmp.shape[0], directed=directed))
            self.mylist.append(igraph.graph_full(n=tmp.shape[0], directed=directed))
            self.filelist += ['empty','full']

            if self.dflag:
                self.e += 'Warning: one file provided: computing distance between %s, empty and full binary network' % self.filelist[0]
            else:
                self.e = 'Warning: one file provided: computing distance between %s,  empty and full binary network' % self.filelist[0]
                self.dflag = True

        try:
            self.res = nettools.netdist(self.mylist,
                                        d=param['d'],
                                        components=param['components'],
                                        ga=param['ga'], **{'n.cores': 1})

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
        
        """
        Get the results and save to csv files
        """
        
        lapply = robjects.r['lapply']
        write_table = robjects.r['write.table']
        names = robjects.r['names']
        rlist = robjects.r['list']
        rmat = robjects.r['as.matrix']
        results = {}

        if self.computed:
            for i in range(len(self.res)):
                myfname = os.path.join(filepath,
                                       names(self.res)[i] + '_distance.tsv')
                
                results[names(self.res)[i]] = {
                    'csv_files': [names(self.res)[i] + '_distance.tsv'],
                    'img_files': [],
                    'desc': '%s network distance' % names(self.res)[i],
                    'rdata': None,
                    'messages': [ self.e if self.dflag else ''],
                    'status': [ 'Warning' if self.dflag else 'Success' ]
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
            return results
        else:
            print "No distance computed"
            return False

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

