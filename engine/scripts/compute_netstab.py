import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import DataFrame
import rpy2.rlike.container as rlc
from rpy2.robjects.numpy2ri import numpy2ri
import rpy2.rinterface as ri
import numpy as np
import os.path
import csv
import rutils as ru

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
                fdir, fname = os.path.split(os.path.splitext(f)[0])
                self.listname.append(fname)
                rcount += 1
            except IOError:
                print "Can't load file %s" %f
        
        if rcount == self.nfiles:
            return True
        else:
            raise IOError

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

        self.met = param['adj_method']
        
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
                                               tol=0.0,
                                               var.thr=0.0,
                                               **{'adj.method': param['adj_method'],
                                                  'n.cores': 1}))
            return_value = True
            
        except IOError, e:
            self.computed = False
            print 'Error during the computation of the stability indicators: %s' % str(e)
        except ri.RRuntimeError, e:
            self.computed = False
            print 'Error during the computation of the stability indicators: %s' % str(e)
            
        if return_value:
            self.computed = True
            return return_value
        else:
            raise Exception(e)
    
    def get_results(self, filepath='.', export_json=True, graph_format="gml", perc=10):
        """
        Write the results on the file system
        """
        
        names = robjects.r['colnames']
        write_table = robjects.r['write.table']
        results = {}
        
        if self.computed:
            for i in xrange(len(self.res)):
                csvlist = []
                tmp = self.res[i]
                
                # print tmp.rx2('S')
                # print tmp.rx2('SI')
                
                # Initialize result dictionary
                results[self.listname[i]] = {
                    'csv_files': [],
                    'img_files': [],
                    'json_files': [],
                    'graph_files': [],
                    'desc': 'Stability indicators for file %s' % self.listname[i],
                    'rdata': None,
                }
                
                # Write S and SI stability indicators
                myfname = os.path.join(filepath, '%s_%s_S-SI.tsv' % (self.listname[i], self.met) )
                csvlist += ['%s_%s_S-SI.tsv' % (self.listname[i], self.met)]
                try:
                    f = open(myfname, 'wb')
                    fw = csv.writer(f, delimiter='\t', lineterminator='\n')
                    fw.writerow(['S', 'SI'])
                    fw.writerow([np.mean(tmp.rx2('S')),np.mean(tmp.rx2('SI'))])
                    f.close()
                except IOError, e:
                    print '%s' % e
                
                
                Sd = np.array(tmp.rx2('Sd'))
                Sw = np.array(tmp.rx2('Sw'))
                
                # Compute the degree stability indicator
                myfname = os.path.join(filepath,'%s_%s_Sd.tsv' 
                                       % (self.listname[i], self.met))
                sdw = ru.write_Sd(Sd, myfname)
                if sdw:
                    csvlist += ['%s_%s_Sd.tsv' % (self.listname[i], self.met)]
                
                # Compute the edge stability indicator
                myfname = os.path.join(filepath,'%s_%s_Sw.tsv' % (self.listname[i], self.met))
                print Sd.shape[1]
                # Write file for edge stability indicator
                sww = ru.write_Sw(Sw, N=Sd.shape[1], filename=myfname)
                if sww:
                    csvlist += ['%s_%s_Sw.tsv' % (self.listname[i], self.met)]

                # Write adjacency matrix on the whole dataset
                myfname = os.path.join(filepath, '%s_%s_adj.tsv' % (self.listname[i], self.met) )
                csvlist += ['%s_%s_adj.tsv' % (self.listname[i], self.met)]
                write_table(tmp.rx2('ADJ'),myfname,
                            sep='\t', quote=False, 
                            **{'col.names': robjects.NA_Logical, 
                               'row.names': True})
                
                # export to json for visualization
                if export_json:
                    jname = ru.export_to_json(tmp.rx2('ADJ'), i=i, 
                                              filepath=filepath, perc=perc,
                                              prefix="%s_%s_" % (self.listname[i], self.met))
                    results[self.listname[i]]['json_files'] += [jname]
                
                # Export to graph format    
                if graph_format:
                    gname = ru.export_graph(tmp.rx2('ADJ'), i=i, filepath=filepath, 
                                            format=graph_format, 
                                            prefix="%s_%s_" % (self.listname[i], self.met))
                    results[self.listname[i]]['graph_files'] += [gname]
                
                
                # Write matrices given by resampling
                # for j, a in enumerate(tmp.rx2('ADJlist')):
                #     myfname = os.path.join(filepath, '%s_%s_res%d.tsv' 
                #                         % (self.listname[i], self.met, j) )
                #     csvlist += ['%s_%s_res%d.tsv' % (self.listname[i], self.met, j)]
                #     #results[self.listname[i]]['csv_files'] += ['%s_%s_res%d.tsv' 
                #     #                                          % (self.listname[i], self.met, j)]
                #     write_table(tmp.rx2('ADJ'),myfname,
                #                 sep='\t', quote=False, 
                #                 **{'col.names': robjects.NA_Logical, 
                #                    'row.names': True})

                # Append the list of the files producted to the result dictionary    
                results[self.listname[i]]['csv_files'] += csvlist
            return results
        else:
            raise Exception('Cannot compute the results')

    
    def get_S (self):
        res = []
        for i in xrange(len(self.res)):
            csvlist = []
            tmp = self.res[i]
            res += tmp.rx2('S')
        
        return res
