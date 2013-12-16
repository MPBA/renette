import compute_netdist as cd
import compute_adj as ca
import compute_netstab as cs



#print 'Test adjacency'
#myparam = {'method':'WGCNA','sep':'\t','row.names': None,'header': True, 'P':2}
#ad = ca.Mat2Adj(['test.tsv','test.tsv'], param = myparam)
#ad.loadfiles()
#ad.compute()
#ad.get_results()
#ad.save_RData()
#print ad.get_results_fromRData()

print 'Test Network Distance'
myparam = {'d': 'HIM','components': True, 'rho': None,'sep': '\t','row.names': 1}
nd = cd.NetDist(['data/test_data_1.csv', 'data/test_data_2.csv', 'data/test_data_3.csv', 'data/test_data_4.csv'], myparam)
nd.loadfiles()
nd.compute()
nd.get_results()
#print nd.save_RData()

#
#print 'Test Stability'
#myparam = {'d': 'HIM', 'rho': None,'sep': '\t','row.names': 1,
#           'adj_method': 'ARACNE', 'P': 6}
#
#ns = cs.NetStability(['test.tsv'])
#ns.loadfiles()
#ns.compute()
#print ns.get_results()
