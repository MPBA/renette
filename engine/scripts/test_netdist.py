import compute_netdist as cd
import compute_adj as ca
import compute_netstab as cs



# print 'Test adjacency'
# myparam = {'method':'WGCNA','sep':'\t','row.names': None,'header': True, 'P':2}
# ad = ca.Mat2Adj(['test.tsv','test.tsv'], param = myparam)
# ad.loadfiles()
# ad.compute()
# ad.get_results()
# ## ad.save_RData()
# print ad.export_to_json(perc=10)
# ad.get_results_fromRData()

# print 'Test Network Distance'
# myparam = {'d': 'HIM','components': True, 'rho': None,'sep': '\t','row.names': 1}
# nd = cd.NetDist(['data/test_data_1.csv', 'data/test_data_2.csv', 'data/test_data_3.csv', 'data/test_data_4.csv'], myparam)
# nd.loadfiles()
# nd.compute()
# nd.get_results()
#print nd.save_RData()

#
print 'Test Stability'
myparam = {'d': 'HIM', 'rho': None,'sep': '\t','row.names': 1,
          'adj_method': 'ARACNE'}

ns = cs.NetStability(filelist=['test_data_1.csv'], seplist=['\t'], param=myparam)
ns.loadfiles()
ns.compute()
print ns.get_results()
