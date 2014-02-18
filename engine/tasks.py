__author__ = 'droghetti'
import time
import uuid
import celery
import os
from django.conf import settings
from django.contrib import messages
from engine.scripts import compute_netdist, compute_adj, compute_netstab
from django.db import DatabaseError, models
from .models import Results, RunningProcess
from django.core.files import File

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
def netinf(self, files, sep, param):
    
    print self.request.id
    
    ad = compute_adj.Mat2Adj(files, sep, param)
    
    tmpdir = str(uuid.uuid4())
    print 'tmpdir %s' % tmpdir
    result_path = os.path.join(settings.MEDIA_ROOT, settings.RESULT_PATH)
    result_path_full = os.path.join(result_path, tmpdir)
    media_path = os.path.join(settings.RESULT_PATH, tmpdir)
    
    print 'results full %s' % result_path_full
    
    if not os.path.exists(result_path_full):
        os.makedirs(result_path_full)
        
    self.update_state(state='RUNNING', meta='Load files...')
    ad.loadfiles()
    
    self.update_state(state='RUNNING', meta='Compute inference...')
    ad.compute()
    
    self.update_state(state='RUNNING', meta='Fetching result...')
    result = ad.get_results(filepath=result_path_full, )
        
    if result:
        
        sdb = save_to_db(result, pid=self.request.id, result_path_full=result_path_full)
        print 'Saving to db %s' % 'Success' if sdb else 'Error'
    print result
    return True


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



def save_to_db(result, pid, result_path_full=settings.MEDIA_ROOT):
    
    """
    Save to Results db
    """
    print 'I am the save to db %s' % pid
    for key in result.keys():
        val = result.get(key)
        for k in ['json_files', 'rdata', 'csv_files', 'img_files', 'graph_files']:
            tp = k.split('_')[0]
            if val[k]:
                for i in range(len(val[k])):
                    myn = val[k][i]
                    print myn
                    try:
                        resdb = Results(
                            process_name='Network Inference',
                            filepath=result_path_full,
                            filetype=tp,
                            filename=myn,
                            task_id = RunningProcess.objects.get(task_id = pid)
                        )
                        
                        if tp == 'csv':
                            mydesc = 'This is a csv file format. Each field is separated by a "tab" character'
                        if tp == 'json':
                            mydesc = 'This is a json file format. This is automatically created for visualization porpose. In particular it is used by the sigma js pluging. Community detection has been performed with "spinglass algorithm" and nodes are placed according to the Fructherman Reingold algorithm'
                        if tp == 'graph':
                            mydesc = 'This is a graph file format (%s). It can be imported by the most popular graph visualization softwares.' % myn.split('.')[-1]
                        if tp == 'img':
                            mydesc = 'This is an image file format produced using R.'
                            
                        # Store description in the DB
                        resdb.desc = mydesc
                            
                        # Store files in the DB
                        if tp == 'csv' or tp == 'json' or tp == 'graph':
                            f = open(os.path.join(result_path_full, myn))
                            resdb.filestore.save(myn, File(f))
                            f.close()
                        if tp == 'img':
                            f = open(os.path.join(result_path_full, myn))
                            resdb.imagestore.save(myn, File(f))
                            f.close()
                    except Exception, e:
                        print e
                         # messages.add_message(messages.ERROR, 'Error: %s' % str(e))
                    try:
                        resdb.save()
                    except Exception, e:
                        print e

    return True


