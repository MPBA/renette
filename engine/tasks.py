__author__ = 'droghetti'
import time
import uuid
import celery
import os
from django.conf import settings
from engine.scripts import compute_netdist



@celery.task
def test_process():
    print "here"
    time.sleep(15)
    return True


@celery.task(bind=True)
def test_netdist(self, files, param):
    nd = compute_netdist.NetDist(files, param)

    tmpdir = str(uuid.uuid4())
    result_path = os.path.join(settings.MEDIA_ROOT, settings.RESULT_PATH)
    result_path_full = os.path.join(result_path, tmpdir)

    if not os.path.exists(result_path_full):
        os.makedirs(result_path_full)

    self.update_state(state='RUNNING', meta={'current_action': 'load files...'})
    nd.loadfiles()

    self.update_state(state='RUNNING', meta={'current_action': 'compute distance'})
    nd.compute()

    self.update_state(state='RUNNING', meta={'current': 'fetching result'})
    result = nd.get_results(filepath=result_path_full, )

    ## calc relative path
    #result_path_relative = []
    #for f in filenames:
    #    result_path_relative.append(os.path.join(settings.RESULT_PATH, tmpdir, f))

    for key in result.keys():
        val = result.get(key)
        val['csv_files'] = [os.path.join(settings.RESULT_PATH, tmpdir, f) for f in val['csv_files']]
        val['img_files'] = [os.path.join(settings.RESULT_PATH, tmpdir, f) for f in val['img_files']]
        val['rdata'] = os.path.join(settings.RESULT_PATH, tmpdir, val['rdata']) if val['rdata'] else None
        result.update({key: val})
    return result