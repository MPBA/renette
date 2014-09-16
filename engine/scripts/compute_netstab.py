import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import DataFrame
import rpy2.rlike.container as rlc
import rpy2.rinterface as ri
import numpy as np
import os.path
import csv
import rutils as ru

class NetStability:
    
    def __init__(self, filelist, seplist, param={}):
        
        self.nfiles = len(filelist)
        self.filelist = filelist
        self.seplist = seplist
        self.results = {}
        
        if len(self.filelist) != len(self.seplist):
            raise IOError('Not enough separators')
        
        self.param = param
        self.mylist = rlc.TaggedList([])
        self.listname = []
        self.error = []
        
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
            except IOError, e:
                self.error += e
                
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
                 'save': True, 'var_thr': 1e-15}

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
                                               **{'adj.method': param['adj_method'],
                                                  'n.cores': 1, 'var.thr': param['var_thr']}))
            return_value = True
            
        except IOError, e:
            return_value = False
            self.error = e
        except ri.RRuntimeError, e:
            return_value = False
            self.error += e
            
        self.computed = return_value
        return return_value
        
    def get_results(self, filepath='.', export_json=True, graph_format="gml", plot=True, perc=10):
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
                
                # Initialize result dictionary
                self.results[self.listname[i]] = {
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
                    self.error += e
                
                
                try:
                    Sd = np.array(tmp.rx2('Sd_boot'))
                    Sw = np.array(tmp.rx2('Sw_boot'))
                
                except IndexError, e:
                    self.error += e
                    
                    
                # Compute the degree stability indicator
                myfname = os.path.join(filepath,'%s_%s_Sd.tsv' 
                                       % (self.listname[i], self.met))
                sdw = ru.write_Sd(Sd, myfname)
                if sdw:
                    csvlist += ['%s_%s_Sd.tsv' % (self.listname[i], self.met)]
                        
                        
                # Write file for edge stability indicator
                myfname = os.path.join(filepath,'%s_%s_Sw.tsv' % (self.listname[i], self.met))
                sww = ru.write_Sw(Sw, N=Sd.shape[1], filename=myfname)
                if sww:
                    csvlist += ['%s_%s_Sw.tsv' % (self.listname[i], self.met)]
                    

                # Write adjacency matrix on the whole dataset
                myfname = os.path.join(filepath, '%s_%s_adj.tsv' % (self.listname[i], self.met))
                
                csvlist += ['%s_%s_adj.tsv' % (self.listname[i], self.met)]
                write_table(tmp.rx2('ADJ'),myfname,
                            sep='\t', quote=False, 
                            **{'col.names': robjects.NA_Logical, 
                               'row.names': True})
                
                print tmp.rx2('Sd_boot')
                
                ## Get hubs and plot stability
                hname = ru.get_hubs(tmp.rx2('ADJ'), i=i, stab_mat=tmp.rx2('Sd'),
                                    stab_mat_all=tmp.rx2('Sd_boot'),
                                    filepath=filepath, 
                                    prefix='%s_%s_hubs' % (self.listname[i], self.met))
                csvlist += [hname[0]]
                self.results[self.listname[i]]['img_files'] += [hname[1]]
                
                # export to json for visualization
                if export_json:
                    jname = ru.export_to_json(tmp.rx2('ADJ'), i=i, 
                                              filepath=filepath, perc=perc,
                                              prefix="%s_%s_" % (self.listname[i], self.met))
                    self.results[self.listname[i]]['json_files'] += [jname]
                
                # Make some plots (degree distribution for now)
                if plot:
                    plotname = ru.plot_degree_distrib(self.res[i].rx2('ADJ'), i=i,
                                                      filepath=filepath,
                                                      prefix='%s_%s_ddist' %(self.listname[i], self.met)
                    )
                    self.results[self.listname[i]]['img_files'] += [plotname]
                    myd = np.array(robjects.r.rowSums(tmp.rx2('ADJ')))
                    
                    plotname = ru.plot_edge_distrib(self.res[i].rx2('ADJ'), i=i, filepath=filepath, 
                                                    prefix='%s_%s_edist' % (self.listname[i], self.met))
                    self.results[self.listname[i]]['img_files'] += [plotname]


                    # plotname = ru.plot_degree_stab(Sd, i, myd,filepath=filepath,
                    #                                prefix='%s_%s_dstab' %(self.listname[i], self.met))
                    # self.results[self.listname[i]]['img_files'] += [plotname]

                    
                # Export to graph format    
                if graph_format:
                    gname = ru.export_graph(tmp.rx2('ADJ'), i=i, filepath=filepath, 
                                            format=graph_format, 
                                            prefix="%s_%s_" % (self.listname[i], self.met))
                    self.results[self.listname[i]]['graph_files'] += [gname]
                
                    
                self.results[self.listname[i]]['csv_files'] += csvlist
            return self.results
        else:
            self.error += 'Cannot compute the results'
            return self.error
    
    def get_S (self):
        res = []
        for i in xrange(len(self.res)):
            csvlist = []
            tmp = self.res[i]
            res += tmp.rx2('S')
        
        return res
