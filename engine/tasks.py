__author__ = 'droghetti'
import time
import uuid
import celery
import os
from django.conf import settings
from engine.scripts import compute_netdist, compute_adj, compute_netstab


@celery.task(bind=True)
def test_netdist(self, files, sep, param):
    nd = compute_netdist.NetDist(files, sep, param)

    tmpdir = str(uuid.uuid4())
    result_path = os.path.join(settings.MEDIA_ROOT, settings.RESULT_PATH)
    result_path_full = os.path.join(result_path, tmpdir)

    if not os.path.exists(result_path_full):
        os.makedirs(result_path_full)

    self.update_state(state='RUNNING', meta='Load files...')
    nd.loadfiles()

    self.update_state(state='RUNNING', meta='Compute distance...')
    nd.compute()

    self.update_state(state='RUNNING', meta='Fetching result...')
    result = nd.get_results(filepath=result_path_full, )

    if result:
        for key in result.keys():
            val = result.get(key)
            val['csv_files'] = [os.path.join(settings.RESULT_PATH, tmpdir, f) for f in val['csv_files']]
            val['img_files'] = [os.path.join(settings.RESULT_PATH, tmpdir, f) for f in val['img_files']]
            val['rdata'] = os.path.join(settings.RESULT_PATH, tmpdir, val['rdata']) if val['rdata'] else None
            result.update({key: val})
    return result


@celery.task(bind=True)
def test_netinf(self, files, sep, param):
    ad = compute_adj.Mat2Adj(files, sep, param)

    tmpdir = str(uuid.uuid4())
    result_path = os.path.join(settings.MEDIA_ROOT, settings.RESULT_PATH)
    result_path_full = os.path.join(result_path, tmpdir)

    if not os.path.exists(result_path_full):
        os.makedirs(result_path_full)

    self.update_state(state='RUNNING', meta='Load files...')
    ad.loadfiles()

    self.update_state(state='RUNNING', meta='Compute inference...')
    ad.compute()

    self.update_state(state='RUNNING', meta='Fetching result...')
    result = ad.get_results(filepath=result_path_full, )

    if result:
        for key in result.keys():
            val = result.get(key)
            val['csv_files'] = [os.path.join(settings.RESULT_PATH, tmpdir, f) for f in val['csv_files']]
            val['json_files'] = [os.path.join(settings.RESULT_PATH, tmpdir, f) for f in val['json_files']]
            val['graph_files'] = [os.path.join(settings.RESULT_PATH, tmpdir, f) for f in val['graph_files']]
            val['img_files'] = [os.path.join(settings.RESULT_PATH, tmpdir, f) for f in val['img_files']]
            val['rdata'] = os.path.join(settings.RESULT_PATH, tmpdir, val['rdata']) if val['rdata'] else None
            result.update({key: val})
    return result


@celery.task(bind=True)
def test_netstab(self, files, sep, param):
    ad = compute_netstab.NetStability(files, sep, param)

    tmpdir = str(uuid.uuid4())
    result_path = os.path.join(settings.MEDIA_ROOT, settings.RESULT_PATH)
    result_path_full = os.path.join(result_path, tmpdir)

    if not os.path.exists(result_path_full):
        os.makedirs(result_path_full)

    self.update_state(state='RUNNING', meta='Load files...')
    ad.loadfiles()

    self.update_state(state='RUNNING', meta='Compute stability...')
    ad.compute()

    self.update_state(state='RUNNING', meta='Fetching result...')
    result = ad.get_results(filepath=result_path_full, )

    if result:
        for key in result.keys():
            val = result.get(key)
            val['csv_files'] = [os.path.join(settings.RESULT_PATH, tmpdir, f) for f in val['csv_files']]
            val['json_files'] = [os.path.join(settings.RESULT_PATH, tmpdir, f) for f in val['json_files']]
            val['graph_files'] = [os.path.join(settings.RESULT_PATH, tmpdir, f) for f in val['graph_files']]
            val['img_files'] = [os.path.join(settings.RESULT_PATH, tmpdir, f) for f in val['img_files']]
            val['rdata'] = os.path.join(settings.RESULT_PATH, tmpdir, val['rdata']) if val['rdata'] else None
            result.update({key: val})
    return result