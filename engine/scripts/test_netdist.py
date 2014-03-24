import compute_netdist as cd
import compute_adj as ca
import compute_netstab as cs
import rutils as ru


#print 'Test adjacency'
#myparam = {'method':'ARACNE','row.names': None,'header': True, 'measure': None}
#ad = ca.Mat2Adj(['data/microbiome_Acidobacteria_0.0-diet.csv'], seplist=['\t'], param = myparam)
#print ad.loadfiles()
#print ad.compute()
#print ad.get_results(export_json=True, graph_format=False, plot=True)
# ad.save_RData()
# ad.get_results_fromRData()
# p


#print 'Test Network Distance'
#myparam = {'d': 'HIM','components': True, 'rho': None,'sep': '\t','row.names': 1, 'header': True}
#nd = cd.NetDist(filelist=['data/test_data_2.csv', 'data/test_data_1.csv', 'data/test_data_2.csv', 'data/test_data_3.csv'], seplist=['\t' for i in xrange(4)], param=myparam)
#print nd.loadfiles()
#print nd.compute()
#print nd.get_results()
## print nd.save_RData()

#
##print 'Test Stability'
myparam = {'d': 'HIM', 'rho': None,'sep': '\t','header': True,
          'adj_method': 'ARACNE','var_thr':0.0 }
##
ns = cs.NetStability(['data/microbiome_Acidobacteria_0.0-diet.csv'], ['\t'], param=myparam)
ns.loadfiles()
ns.compute()
print ns.get_results(export_json=True, graph_format=False, plot=True)
