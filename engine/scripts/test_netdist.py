import compute_netdist as cd
import compute_adj as ca
import compute_netstab as cs

# print 'Test adjacency'
# myparam = {'method':'WGCNA','row.names': None,'header': True, 'P':6}
# ad = ca.Mat2Adj(['data/microbiome_Acidobacteria_0.0-diet.csv'], seplist=['\t'], param = myparam)
# ad.loadfiles()
# ad.compute()
# print ad.get_results(export_json=True, graph_format=False)
# ad.save_RData()
# ad.get_results_fromRData()
# p


print 'Test Network Distance'
myparam = {'d': 'HIM','components': True, 'rho': None,'sep': '\t','row.names': 1}
nd = cd.NetDist(filelist=['data/test_data_3.csv'], seplist=['\t'], param=myparam)
print nd.loadfiles()
nd.compute()
print nd.get_results()
print nd.save_RData()

#
# print 'Test Stability'
# myparam = {'d': 'HIM', 'rho': None,'sep': '\t','row.names': 1,
#           'adj_method': 'ARACNE'}

# ns = cs.NetStability(['test.tsv'], ['\t'], param=myparam)
# ns.loadfiles()
# ns.compute()
# print ns.get_results()
