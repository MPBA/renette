import json

__author__ = 'droghetti'
import uuid
import celery
import os
from django.conf import settings
from engine.scripts import compute_netdist, compute_adj, compute_netstab, compute_stats
from .models import Results, RunningProcess
from django.core.files import File
import csv
import psycopg2


@celery.task(bind=True, name='netdist')
def netdist(self, files, sep, param):
    nd = compute_netdist.NetDist(files, sep, param)

    tmpdir = str(uuid.uuid4())
    result_path = os.path.join(settings.MEDIA_ROOT, settings.RESULT_PATH)
    result_path_full = os.path.join(result_path, tmpdir)
    media_path = os.path.join(settings.RESULT_PATH, tmpdir)
    
    if not os.path.exists(result_path_full):
        os.makedirs(result_path_full)

    self.update_state(state='RUNNING', meta='Load files...')
    nd.loadfiles()

    self.update_state(state='RUNNING', meta='Compute distance...')
    nd.compute()

    self.update_state(state='RUNNING', meta='Fetching result...')
    result = nd.get_results(filepath=result_path_full, )
    pname = 'Network Distance'
    
    if type(result) is dict:
        sdb = save_to_db(result, pname=pname, pid=self.request.id, result_path_full=result_path_full)
        ## sdb = save_to_db(result, pname=pname, pid=self.request.id, result_path_full=result_path_full)

        print 'Saving to db %s' % 'Success' if sdb else 'Error'
    else:
        if type(result) is list:
            sdb = Results(process_name='Network Distance',
                            filepath=result_path_full,
                            filetype='Error',
                            task_id=RunningProcess.objects.get(task_id=self.request.id)
            )
    
    ## print result
    return True


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


@celery.task(bind=True, name='netinf')
def netinf(self, files, sep, param):
    
    ad = compute_adj.Mat2Adj(files, sep, param)
    
    tmpdir = str(uuid.uuid4())
    result_path = os.path.join(settings.MEDIA_ROOT, settings.RESULT_PATH)
    result_path_full = os.path.join(result_path, tmpdir)
    media_path = os.path.join(settings.RESULT_PATH, tmpdir)
    
    
    if not os.path.exists(result_path_full):
        os.makedirs(result_path_full)
        
    self.update_state(state='RUNNING', meta='Load files...')
    ad.loadfiles()
    
    self.update_state(state='RUNNING', meta='Compute inference...')
    ad.compute()
    
    self.update_state(state='RUNNING', meta='Fetching result...')
    result = ad.get_results(filepath=result_path_full, )
    pname = 'Network Inference'
    
    if type(result) is dict:
        sdb = save_to_db(result, pname=pname, pid=self.request.id, result_path_full=result_path_full)
        print 'Saving to db %s' % 'Success' if sdb else 'Error'
    else:
        if type(result) is list:
            sdb = Results(process_name='Network Inference',
                            filepath=result_path_full,
                            filetype='Error',
                            task_id=RunningProcess.objects.get(task_id=self.request.id)
            )
    ## print result
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

@celery.task(bind=True, name='netstab')
def netstab(self, files, sep, param):
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
    pname = 'Network Stability'
    
    if type(result) is dict:

        sdb = save_to_db(result, pname=pname, pid=self.request.id, result_path_full=result_path_full)
        print 'Saving to db %s' % 'Success' if sdb else 'Error'
    else:
        if type(result) is list:
            resdb = Results(process_name='Network Stability',
                            filepath=result_path_full,
                            filetype='Error',
                            task_id=RunningProcess.objects.get(task_id=self.request.id)
            )
            
    return True

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


@celery.task(bind=True, name='netstats')
def netstats(self, files, sep, param, media_root, result_path):
    nd = compute_stats.NetStats(files, sep, param)

    tmpdir = str(uuid.uuid4())
    # result_path = os.path.join(settings.MEDIA_ROOT, settings.RESULT_PATH)
    result_path = os.path.join(media_root, result_path)
    result_path_full = os.path.join(result_path, tmpdir)
    media_path = os.path.join(settings.RESULT_PATH, tmpdir)
    
    if not os.path.exists(result_path_full):
        os.makedirs(result_path_full)
    
    print "Load"
    self.update_state(state='RUNNING', meta='Load files...')
    nd.loadfiles()
    
    print "Compute"
    self.update_state(state='RUNNING', meta='Compute statistics...')
    nd.compute()
    
    self.update_state(state='RUNNING', meta='Fetching result...')
    result = nd.get_results(filepath=result_path_full, )
    pname = 'Network Statistics'
    
    if type(result) is dict:
        sdb = save_to_db(result, pname=pname, pid=self.request.id, result_path_full=result_path_full)
        ## sdb = save_to_db(result, pname=pname, pid=self.request.id, result_path_full=result_path_full)
        
        print 'Saving to db %s' % 'Success' if sdb else 'Error'
    else:
        if type(result) is list:
            resdb = Results(process_name='Network Statistics',
                            filepath=result_path_full,
                            filetype='Error',
                            task_id=RunningProcess.objects.get(task_id=self.request.id)
            )
    
    ## print result
    return True


def save_to_db(result, pname, pid, result_path_full=settings.MEDIA_ROOT):
    
    """
    Save to Results db
    """

    ## Set up the DB connection
    con = psycopg2.connect(dbname='renette', user='renette', password='nette@re!!', host='geopg', port=50003)
    cursor = con.cursor()

    # Get the current running process
    cursor.execute("select id from engine_runningprocess where task_id='{}';".format(pid))
    id = cursor.fetchone()[0]

    # Cycle over all results
    for key in result.keys():
        val = result.get(key)
        for k in ['json_files', 'rdata', 'csv_files', 'img_files', 'graph_files']:
            tp = k.split('_')[0]
            if val[k]:
                for i in range(len(val[k])):
                    myn = val[k][i]
                    try:
                        # Set description for the record according to file type
                        if tp == 'csv':
                            mydesc = 'This is a csv file format. Each field is separated by a "tab" character'
                        if tp == 'json':
                            mydesc = 'This is a json file format. This is automatically created for visualization porpose. In particular it is used by the sigma js pluging. Community detection has been performed with "spinglass algorithm" and nodes are placed according to the Fructherman Reingold algorithm'
                        if tp == 'graph':
                            mydesc = 'This is a graph file format (%s). It can be imported by the most popular graph visualization softwares.' % myn.split('.')[-1]
                        if tp == 'img':
                            mydesc = 'This is an image file format produced using R.'

                        # Allocate the entry in the result db
                        cursor.execute("INSERT INTO engine_results (process_name, filepath, filetype, filename, task_id_id, desc )"
                                       "VALUES (%s, %s, %s, %s, %s, %s);", [pname, result_path_full, tp, myn, id, mydesc])

                        # Get the id of the last entry
                        cursor.execute("SELECT max(id) FROM engine_results")
                        idres = cursor.fetchone()[0]

                        # CSV file store
                        if tp == 'csv':
                            f = open(os.path.join(result_path_full, myn))
                            cursor.execute("UPDATE engine_results SET filestore=%s WHERE id=%s", [f, idres])
                            f.seek(0)
                            reader = csv.reader(f, delimiter='\t')
                            idx = 0
                            for line in iter(reader):
                                if(idx==0):
                                    cursor.execute("UPDATE engine_results SET filefirstrow=%s WHERE id=%s", [line, idres])
                                idx += 1

                            cursor.execute("UPDATE engine_results SET filerow=%s, filecol=%s WHERE id=%s",
                                            [idx, len(line) if line else None])
                            f.close()

                        # JSON and GRAPH file store
                        if tp == 'json' or tp == 'graph':
                            f = open(os.path.join(result_path_full, myn))
                            cursor.execute("UPDATE engine_results SET filestore=%s WHERE id=%s", [f, idres])
                            # resdb.filestore.save(myn, File(f))
                            f.close()

                        # IMAGE files
                        if tp == 'img':
                            f = open(os.path.join(result_path_full, myn))
                            cursor.execute("UPDATE engine_results SET imagestore=%s WHERE id=%s", [f, idres])
                            f.close()
                    except Exception, e:
                        print e
                    # try:
                    #     resdb.save()
                    # except Exception, e:
                    #     print e
    con.commit()
    cursor.close()
    con.close()
    return True