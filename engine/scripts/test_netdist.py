import compute_netdist as cd
import compute_adj as ca
import compute_netstab as cs
import compute_stats as csa
# import rutils as ru



if __name__ == '__main__':

    print 'Test adjacency'
    myparam = {'method':'CLR','row.names': None,'header': True, 'measure': None, 'col.names': True}
    ad = ca.Mat2Adj(['data/microbiome_Acidobacteria_0.0-diet.csv'], seplist=['\t'], param = myparam)
    # ad = ca.Mat2Adj(['/home/michele/work/HCC_data/data/HUMAN_HCC_MALE_1.dat','/home/michele/work/HCC_data/data/HUMAN_HCC_MALE_1.dat'], seplist=['\t', '\t'], param = myparam)
    print ad.loadfiles()
    print ad.compute()
    print ad.get_results(export_json=True, graph_format=False, plot=True)
    # ad.save_RData()
    # ad.get_results_fromRData()
    # p
    print 'Test Network Distance'
    myparam = {'d': 'HIM', 'components': True, 'rho': None, 'sep': '\t', 'row.names': 1, 'header': True}
    nd = cd.NetDist(filelist=['data/test_data_2.csv', 'data/test_data_1.csv', 'data/test_data_2.csv',
                              'data/test_data_3.csv'], seplist=['\t' for i in xrange(4)], param=myparam)
    print nd.loadfiles()
    print nd.compute()
    print nd.get_results()
    # print nd.save_RData()
    


    #
    print 'Test Stability'
    myparam = {'d': 'HIM', 'rho': None,
               'sep': ['\t'],
               'header': True,
               'adj_method': 'CLR','var_thr':0.0, 'tol':0.0 }

    print myparam
    ###
    nss = cs.NetStability(['data/microbiome_Acidobacteria_0.0-diet.csv'], ['\t'], param=myparam)
    # ns = cs.NetStability(['/home/michele/work/HCC_data/data/HUMAN_HCC_MALE_1.dat','/home/michele/work/HCC_data/data/HUMAN_HCC_MALE_-1.dat', '/home/michele/work/HCC_data/data/HUMAN_HCC_FEMALE_1.dat', '/home/michele/work/HCC_data/data/HUMAN_HCC_FEMALE_-1.dat'],['\t' for i in range(4)],  param=myparam)
    ## ns = cs.NetStability(['/home/michele/work/HCC_data/data/HUMAN_HCC_MALE_1.dat'],['\t'],  param=myparam)
    nss.loadfiles()
    nss.compute()
    print nss.get_results(export_json=True, graph_format=False, plot=True)

    print 'Test Network Stats'
    myparam = {'d': 'HIM', 'components': True, 'rho': None,'sep': '\t', 'header': True,
               'row.names': 1}
    nsa = csa.NetStats(filelist=['data/test_data_2.csv'], seplist=['\t'], param=myparam)
    ## nd = cns.NetStats(filelist=['/home/michele/Downloads/Adj_1'], seplist=['\t'], param=myparam)
    ## , 'data/test_data_1.csv', 'data/test_data_2.csv', 'data/test_data_3.csv'], seplist=['\t' for i in xrange(4)], param=myparam)
    print nsa.loadfiles()
    print nsa.compute()
    print nsa.get_results()