import compute_netdist as cd
import compute_adj as ca
import compute_netstab as cs

# print 'Test adjacency'
# myparam = {'method':'WGCNA','sep':'\t','row.names': None,'header': False, 'P':2}
# ad = ca.Mat2Adj(['test_noname.tsv','test_noname1.tsv'], seplist=['\t','\t'], param = myparam)
# ad.loadfiles()
# ad.compute()
# print ad.get_results(export_json=True, graph_format=False)
# ad.save_RData()
# ad.get_results_fromRData()
# print ad.export_graph()


# print 'Test Network Distance'
# myparam = {'d': 'HIM','components': True, 'rho': None,'sep': '\t','row.names': 1}
# nd = cd.NetDist(filelist=['data/test_data_3.csv'], seplist=['\t'], param=myparam)
# print nd.loadfiles()
# nd.compute()
# print nd.get_results()
# print nd.save_RData()

#
print 'Test Stability'
myparam = {'d': 'HIM', 'rho': None,'sep': '\t','row.names': 1,
          'adj_method': 'ARACNE'}

ns = cs.NetStability(['test.tsv'], ['\t'], param=myparam)
ns.loadfiles()
ns.compute()
print ns.get_results()
