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
        print len(filelist)
        if self.nfiles < 2:
            raise ValueError("Not enough file loaded")

        self.filelist = filelist
        self.seplist = seplist
        self.param = param
        self.mylist = rlc.TaggedList([])
        
    def loadfiles(self):
        """
        Load files into R environment
        """
        rcount = 0
        asmatrix = robjects.r['as.matrix']

        
        ## Set the default parameter for reading from csv
        param = {'header': True, 'as_is': True, 'row.names': ri.NULL}
        
        ## Check the correct parameter and set the default        
        for p in param.keys():
            if p in self.param:
                if self.param[p] is not None:
                    param[p] = self.param[p]

        #for f in self.filelist:
        for f, s in zip(self.filelist, self.seplist):
            try:
                dataf = DataFrame.from_csvfile(f,
                                               sep=str(s),
                                               header=param['header'],
                                               as_is=param['as_is'],
                                               row_names=param['row.names'])

                dataf = asmatrix(dataf)
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
        ## robjects.conversion.py2ri = numpy2ri
        param = {'d': 'HIM', 'ga': ri.NULL, 'components': True, 'rho': 1}
        
        ## Check the correct parameter and set the default
        for p in param.keys():
            if p in self.param:
                if self.param[p] is not None:
                    param[p] = self.param[p]

        print len(self.mylist)
        print self.param
        print param

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
                    'desc': '%s is bla bla bla bla' % names(self.res)[i],
                    'rdata': None,
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

