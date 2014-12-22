from rpy2.rinterface._rinterface import RRuntimeError
import rpy2.robjects as robjects
from rpy2.robjects.vectors import DataFrame
import rpy2.rlike.container as rlc
<<<<<<< HEAD
import os.path
import net_stats as ns
import csv
=======
>>>>>>> develop
import rpy2.rinterface as ri
import numpy as np
import os.path
import rutils as ru
<<<<<<< HEAD
=======
import net_stats as ns
import csv
from rpy2.robjects import DataFrame
>>>>>>> develop

class NetStats:
    
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
        self.e = []
        self.res = []

    def loadfiles(self):
        """
        Load files into R environment
        """
        rcount = 0
        asmatrix = robjects.r['as.matrix']
        diag = robjects.r['diag']
        names = robjects.r['names']
        
        ## Set the default parameter for reading from csv
        param = {'header': True, 'as_is': True, 'row.names': ri.RNULLArg}
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
                    if (dataf.rx(i+1,i+1)[0] - 0.0 >= 1e-8):
                        zcount += 1
                        dataf.rx[i+1,i+1] = 0

                if zcount:
                    self.e += f
                    
                self.mylist.append(dataf)
                fdir, fname = os.path.split(os.path.splitext(f)[0])
                self.listname.append(fname)

                rcount += 1
            except IOError, e:
                self.error += e
            
            except RRuntimeError, e:
                self.error += e

        if rcount == self.nfiles:
            return True
        else:
            return False # IOError('Cannot read all the files')
            
    def compute(self):
        """
        Compute the distances between adjacency matrices using nettools
        package

        """
        names = robjects.r['colnames']
        self.mynames = []
        ## Insert here the measure to compute
        try:
            self.netres = []
            for r in self.mylist:
                netstat = ns.Net_Stats(r)
                nn = np.array(netstat.ret_names())
                self.mynames.append(nn)
                degres = np.empty((robjects.r.length(nn)[0],11))
                degres[:,0] = np.array(netstat.degree())
                degres[:,1] = np.array(netstat.compute_modularity())
                degres[:,2] = np.array(netstat.degree_by_community())
                degres[:,3] = np.array(netstat.pgrank())
                degres[:,4] = np.array(netstat.pgrank_by_community())
                degres[:,5] = np.array(netstat.eccentricity())
                degres[:,6] = np.array(netstat.ecc_by_community())
                degres[:,7] = np.array(netstat.alphac())
                degres[:,8] = np.array(netstat.alphac_by_community())
                degres[:,9] = np.array(netstat.evcent())
                degres[:,10] = np.array(netstat.evcent_by_community())
                self.netres += [[ netstat.modularity().rx(1)[0],netstat.radius().rx(1)[0],netstat.density().rx(1)[0]]]
                self.res += [degres]

            return_value = True
        except ValueError, e:
            return_value = False
            self.error += e
            print 'merda: %s' % e

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
                myfname = os.path.join(filepath,
                                       self.listname[i] + '_stats.tsv')
                self.results[self.listname[i]] = {
                    'csv_files': [],
                    'img_files': [],
                    'json_files': [],
                    'graph_files': [],
                    'desc': '%s network stats' % self.listname[i],
                    'rdata': None,
                }

                try:
                    len(self.res[i])
                    tmp = self.res[i]
                    
                    # colnames = ri.StrSexpVector([os.path.basename(f) for f in self.filelist])
                    # rownames = ri.StrSexpVector([os.path.basename(f) for f in self.filelist])
                    
                    # tmp.do_slot_assign("dimnames", rlist(
                    #     ri.StrSexpVector(colnames),
                    #     ri.StrSexpVector(rownames)
                    # ))
                except Exception:
                    tmp = robjects.r.matrix(self.res[i], ncol=1, nrow=1)
                    tmp.do_slot_assign("dimnames", rlist(
                        ri.StrSexpVector([os.path.basename(self.filelist[0])]),
                        ri.StrSexpVector([os.path.basename(self.filelist[1])])
                    ))

                # write_table(tmp, myfname, sep='\t',
                #             quote=False,
                #             **{
                #                 'col.names': ri.NA_Logical,
                #                 'row.names': True
                #             })
                
                myfname = '%s_%d_node_stats.csv' % (self.listname[i],i)
                filename = os.path.join(filepath, myfname)
                head = ['Node', 'Degree', 'Communities', 'Degree_by_community',
                        'PageRank', 'PageRank_by_Community', 
                        'Eccentricity', 'Eccentricity_by_community', 
                        'AlphaCentr', 'AlphaCentr_by_community',
                        'EigenCentrality', 'EigenCentrality_by_community']
                
                with open(filename, 'wb') as ff:
                    fw = csv.writer(ff, delimiter='\t', lineterminator='\n')
                    fw.writerow(head)
                    for l in zip(self.mynames[i], self.res[i]):
                        tmpl = [l[0]]
                        tmpl.extend(l[1])
                        fw.writerow(tmpl)
                
                self.results[self.listname[i]]['csv_files'] += [myfname]
                
                myfname = '%s_%d_net_stats.csv' % (self.listname[i],i)
                filename = os.path.join(filepath, myfname)
                try:
                    f = open(filename, 'wb')
                    fw = csv.writer(f, delimiter='\t')
                except IOError, e:
                    self.e += e
                fw.writerow(['Modularity', 'Radius', 'Density'])

                fw.writerow([np.float(n) for n in self.netres[i]])
                f.close()
                self.results[self.listname[i]]['csv_files'] += [myfname]
                
                hname = ru.get_hubs(self.mylist[i], i, 90, 
                                    filepath=filepath, 
                                    prefix='%s_hubs' % self.listname[i])
                self.results[self.listname[i]]['csv_files'] += [hname]
                
                
                
                
                # if self.nfiles > 2:
                #     try:
                #         mds = ru.plot_mds(self.res[i],i, filepath = filepath,
                #                          prefix=names(self.res)[i] + '_distance')
                #         self.results[names(self.res)[i]]['img_files'] += [mds]
                #     except RRuntimeError, e:
                #         self.error += e
                
            # self.results['input'] = {
            #     'csv_files': [],
            #     'img_files': [],
            #     'json_files': [],
            #     'graph_files': [],
            #     'desc': 'network distance' ,
            #     'rdata': None,
            # }
            
            # for j, f in enumerate(self.mylist):
            #     hname = ru.get_hubs(f, j, 90, 
            #                         filepath=filepath, 
            #                         prefix='%d_hubs' % j)
                
            #     self.results['input']['csv_files'] += [hname]
            #     if export_json:
                    
            #         jname = ru.export_to_json(f, i=j, filepath=filepath, 
            #                                   perc=perc, 
            #                                   prefix='%d_%s' % (j, 'topology'))
            #         self.results['input']['json_files'] += [jname]
                
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
