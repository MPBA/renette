__author__ = 'droghetti'
import time
import celery
from engine.scripts import compute_netdist


@celery.task
def test_process():
    print "here"
    time.sleep(15)
    return True


@celery.task(bind=True)
def test_netdist(self, files, param):
    nd = compute_netdist.NetDist(files, param)

    self.update_state(state='RUNNING', meta={'current_action': 'load files...'})
    print nd.loadfiles()

    self.update_state(state='RUNNING', meta={'current_action': 'compute distance'})
    print nd.compute()

    self.update_state(state='RUNNING', meta={'current': 'fetching result'})
    print nd.get_results()

    return nd.get_results()