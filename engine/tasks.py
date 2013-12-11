__author__ = 'droghetti'
import time
import celery
from engine.scripts import compute_netdist


@celery.task
def test_process():
    print "here"
    time.sleep(15)
    return True


@celery.task
def test_netdist(files, param):
    nd = compute_netdist.NetDist(files, param)

    print nd.loadfiles()
    print nd.compute()
    print nd.get_results()

    return nd.get_results()