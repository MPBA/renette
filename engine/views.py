# -*- encoding: utf-8 -*-
from redis import ConnectionError

__author__ = 'ernesto'
#This file contains only the views for the main app. It's made just to render an home page for the project

from django.views.generic.base import View
from django.shortcuts import redirect, render
from django.core.files.uploadedfile import UploadedFile
from django.db import DatabaseError
from django.http import Http404, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .utils import document_validator, get_bootsrap_badge,  handle_upload
from .models import RunningProcess, Results
from django.contrib import messages
from django.conf import settings
from tojson.decorators import render_to_json
import os
import StringIO
import zipfile
import json
from datetime import datetime


## ClassView computing stability of networks
##--------------------------------------------------
class NetworkStabilityClass(View):
    template_name = 'engine/network_stability.html'

    def get(self, request, **kwargs):
        context = {'step2': 'network_stability_2'}
        return render(request, self.template_name, context)


class NetworkStabilityStep2Class(View):
    template_name = 'engine/network_stability_2.html'

    def post(self, request):
        files = []
        removed_files = []
        dim = []

        for filepath in request.POST.getlist('uploaded'):
            ex_first_row = request.POST['exclude_col_header'] if 'exclude_col_header' in request.POST else None
            ex_first_col = request.POST['exclude_row_header'] if 'exclude_row_header' in request.POST else None
            valid, ret_file = document_validator(filepath, ex_first_row, ex_first_col)
            if valid['is_valid']:
                dim.append(valid['nrow'])
                max_ga = valid['nrow']
                files.append({'name': ret_file.name,
                              'prop': valid,
                              'path': filepath
                              })
            else:
                removed_files.append(ret_file)
        
        
        if len(files) < 1:
            messages.add_message(self.request, messages.ERROR, 'Your files properties are not valid.')
            return redirect('network_stability')

        context = {
                   'uploaded_files': files,
                   'max_ga': max_ga,
                   'removed_files': removed_files
                   }
        return render(request, self.template_name, context)


class NetworkStabilityStep3Class(View):
    template_name = 'engine/network_stability_3.html'

    def post(self, request):
        files = []
        for file in request.POST.getlist('file'):
            files.append(os.path.join(settings.MEDIA_ROOT, file))

        components = request.POST.get("components", 'True')
        sep = request.POST.getlist('sep')
        param = {
            'method':  request.POST.get("resmethods", "montecarlo"),
            'k': int(request.POST.get("k")) if request.POST.get("k", False) else 3,
            'h': int(request.POST.get("h")) if request.POST.get("h", False) else 20,

            'adj_method': request.POST.get("methods", "cor"),
            'P': float(request.POST.get("p")) if request.POST.get("p", False) else 6,
            'FDR': float(request.POST.get("fdr")) if request.POST.get("fdr", False) else float(1e-3),
            'alpha': float(request.POST.get("alpha")) if request.POST.get("alpha", False) else 0.6,
            'C': float(request.POST.get("c")) if request.POST.get("c", False) else 15,
            'measure': request.POST.get("measure", None),

            'd': request.POST.get("distance", "HIM"),
            'ga': float(request.POST.get("ga")) if request.POST.get("ga", False) else None,
            'components': True if components == 'True' else False,
            'rho':  float(request.POST.get("rho")) if request.POST.get("rho", False) else None,
            #'sep': request.POST.get("sep", "\t"),
            'header': True if request.POST.get("col", False) else False,
            'row.names': 1 if request.POST.get("row", False) else None
        }
        try:

            runp = RunningProcess(
                process_name='Network stability',
                inputs=param,
                submited=datetime.now()
            )
            # t = netstab.delay(files, sep, param)
            t = settings.APP.send_task('netdist', [files, sep, param, settings.MEDIA_ROOT, settings.RESULT_PATH])
            runp.task_id = t.id
            
        except Exception, e:
            messages.add_message(self.request, messages.ERROR, 'Error: %s' % str(e))

        try:
            runp.save()
            context = {'files': files, 'task': t, 'uuid': t.id}

            session = self.request.session.get('runp',[])
            session.append(runp.pk)
            self.request.session['runp'] = session
        except DatabaseError, e:
            t.revoke(terminate=True)
            messages.add_message(self.request, messages.ERROR, 'Error: %s' % str(e))

        messages.add_message(self.request, messages.SUCCESS, 'Process submitted with success!!!')
        return render(request, self.template_name,  context)


class NetworkStabilityStep4Class(View):
    template_name = 'engine/network_stability_4.html'

    def get(self, request, uuid, **kwargs):
        
        # task = djcelery.celery.AsyncResult(uuid)
        task = settings.APP.AsyncResult(uuid)
        
        try:
            runp = RunningProcess.objects.get(task_id=uuid)
        except RunningProcess.DoesNotExist:
            runp = None
            messages.add_message(self.request, messages.ERROR, 'Some information not available!')

        context = {
            'runp': runp,
            'tables': runp.results_set.filter(filetype='csv'),
            'charts': runp.results_set.filter(filetype='img'),
            'json': runp.results_set.filter(filetype='json'),
            'graphs': runp.results_set.filter(filetype='graph'),
            'rdata': runp.results_set.filter(filetype='rdata'),
            'charts_length': runp.results_set.filter(filetype='img').count(),
            'task': task,
            'badge': get_bootsrap_badge(task.status)

        }
        
        return render(request, self.template_name, context)


## ClassView computing inference of networks
##--------------------------------------------------
class NetworkInferenceClass(View):
    template_name = 'engine/network_inference.html'

    def get(self, request, **kwargs):
        context = {'step2': 'network_inference_2'}
        return render(request, self.template_name, context)


class NetworkInferenceStep2Class(View):
    template_name = 'engine/network_inference_2.html'

    def post(self, request):
        files = []
        removed_files = []
        dim = []

        for filepath in request.POST.getlist('uploaded'):
            ex_first_row = request.POST['exclude_col_header'] if 'exclude_col_header' in request.POST else None
            ex_first_col = request.POST['exclude_row_header'] if 'exclude_row_header' in request.POST else None
            valid, ret_file = document_validator(filepath, ex_first_row, ex_first_col)
            if valid['is_valid']:
                dim.append(valid['nrow'])
                max_ga = valid['nrow']
                files.append({'name': ret_file.name,
                              'prop': valid,
                              'path': filepath
                              })
            else:
                removed_files.append(ret_file)
        if len(files) < 1:
            messages.add_message(self.request, messages.ERROR, 'Your files properties are not valid.')
            return redirect('network_inference')

        context = {
                   'uploaded_files': files,
                   'max_ga': max_ga,
                   'removed_files': removed_files
                   }
        return render(request, self.template_name, context)


class NetworkInferenceStep3Class(View):
    template_name = 'engine/network_inference_3.html'

    def post(self, request):
        files = []
        for file in request.POST.getlist('file'):
            files.append(os.path.join(settings.MEDIA_ROOT, file))

        sep = request.POST.getlist('sep')

        param = {
            'method': request.POST.get("methods", "cor"),
            'P': float(request.POST.get("p")) if request.POST.get("p", False) else 6,
            'FDR': float(request.POST.get("fdr")) if request.POST.get("fdr", False) else float(1e-3),
            'alpha': float(request.POST.get("alpha")) if request.POST.get("alpha", False) else 0.6,
            'C': float(request.POST.get("c")) if request.POST.get("c", False) else 15,
            'measure': request.POST.get("measure", None),
            'header': True if request.POST.get("col", False) else False,
            'row.names': 1 if request.POST.get("row", False) else None
        }
        try:
            runp = RunningProcess(
                process_name='Network inference',
                inputs=param,
                submited=datetime.now()
            )
            # t = netinf.delay(files, sep, param)
            t = settings.APP.send_task('netinf', [files, sep, param, settings.MEDIA_ROOT, settings.RESULT_PATH])
            runp.task_id = t.id
        except Exception, e:
            messages.add_message(self.request, messages.ERROR, 'Error: %s' % str(e))

        # try:
        runp.save()
        context = {'files': files, 'task': t, 'uuid': t.id}

        session = self.request.session.get('runp',[])
        session.append(runp.pk)
        self.request.session['runp'] = session
        # except DatabaseError, e:
        #     t.revoke(terminate=True)
        #     messages.add_message(self.request, messages.ERROR, 'Error: %s' % str(e))

        messages.add_message(self.request, messages.SUCCESS, 'Process submitted with success!!!')
        return render(request, self.template_name, context)


# Process status view from database
class NetworkInferenceStep4Class(View):
    template_name = 'engine/network_inference_4.html'

    def get(self, request, uuid, **kwargs):
        
        # task = djcelery.celery.AsyncResult(uuid)
        task = settings.APP.AsyncResult(uuid)
        
        try:
            runp = RunningProcess.objects.get(task_id=uuid)
        except RunningProcess.DoesNotExist:
            runp = None
            messages.add_message(self.request, messages.ERROR, 'Some information not available!')

        context = {
            'runp': runp,
            'tables': runp.results_set.filter(filetype='csv'),
            'charts': runp.results_set.filter(filetype='img'),
            'json': runp.results_set.filter(filetype='json'),
            'graphs': runp.results_set.filter(filetype='graph'),
            'rdata': runp.results_set.filter(filetype='rdata'),
            'charts_length': runp.results_set.filter(filetype='img').count(),
            'task': task,
            'badge': get_bootsrap_badge(task.status)

        }

        return render(request, self.template_name, context)


## ClassView computing distance between network
##--------------------------------------------------

class NetworkDistanceClass(View):
    template_name = 'engine/network_distance.html'

    def get(self, request, **kwargs):
        context = {'step2': 'network_distance_2',
                   'from_web': True}
        return render(request, self.template_name, context)


class NetworkDistanceStep2Class(View):
    template_name = 'engine/network_distance_2.html'

    def post(self, request):
        files = []
        removed_files = []
        dim = []
        from_web = True if request.POST.get('from_web') == 'true' else False
        print from_web
        # if from_web:
        for filepath in request.POST.getlist('uploaded'):
            ex_first_row = request.POST['exclude_col_header'] if 'exclude_col_header' in request.POST else None
            ex_first_col = request.POST['exclude_row_header'] if 'exclude_row_header' in request.POST else None
            valid, ret_file = document_validator(filepath, ex_first_row, ex_first_col)
            if valid['is_valid'] and valid['is_cubic']:
                dim.append(valid['nrow'])
                max_ga = valid['nrow']
                files.append({'name': ret_file.name,
                              'prop': valid,
                              'path': filepath
                              })
            else:
                removed_files.append(ret_file)
        print files
        if len(files) < 1:
            messages.add_message(self.request, messages.ERROR, 'Your files properties are not valid.')
            return redirect('network_distance')
        elif not all(x == dim[0] for x in dim):
            messages.add_message(self.request, messages.ERROR, 'Your files dim are not equal')
            return redirect('network_distance')

        context = {
                   'uploaded_files': files,
                   'max_ga': max_ga,
                   'removed_files': removed_files
                  }
        return render(request, self.template_name, context)


class NetworkDistanceStep3Class(View):
    template_name = 'engine/network_distance_3.html'

    def post(self, request):
        files = []
        for file in request.POST.getlist('file'):
            files.append(os.path.join(settings.MEDIA_ROOT, file))

        components = request.POST.get("components", 'True')
        sep = request.POST.getlist('sep')
        param = {
            'd': request.POST.get("distance", "HIM"),
            'ga': float(request.POST.get("ga")) if request.POST.get("ga", False) else None,
            'components': True if components == 'True' else False,
            'rho':  float(request.POST.get("rho")) if request.POST.get("rho", False) else None,
            'header': True if request.POST.get("col", False) else False,
            'row.names': 1 if request.POST.get("row", False) else None
        }
        try:
            runp = RunningProcess(
                process_name='Network distance',
                inputs=param,
                submited=datetime.now()
            )
            # t = netdist.delay(files, sep, param, settings.MEDIA_ROOT, settings.RESULT_PATH)
            t = settings.APP.send_task('netdist', [files, sep, param, settings.MEDIA_ROOT, settings.RESULT_PATH])
            runp.task_id = t.id

        except Exception, e:
            messages.add_message(self.request, messages.ERROR, 'Error: %s' % str(e))

        try:
            runp.save()
            context = {'files': files, 'task': t, 'uuid': t.id}

            session = self.request.session.get('runp',[])
            session.append(runp.pk)
            self.request.session['runp'] = session
        except DatabaseError, e:
            t.revoke(terminate=True)
            messages.add_message(self.request, messages.ERROR, 'Error: %s' % str(e))

        messages.add_message(self.request, messages.SUCCESS, 'Process submitted with success!!!')
        return render(request, self.template_name, context)

# Process status view from database
class NetworkDistanceStep4Class(View):
    template_name = 'engine/network_distance_4.html'

    def get(self, request, uuid, **kwargs):
        
        # task = djcelery.celery.AsyncResult(uuid)
        task = settings.APP.AsyncResult(uuid)

        try:
            runp = RunningProcess.objects.get(task_id=uuid)
        except RunningProcess.DoesNotExist:
            runp = None
            messages.add_message(self.request, messages.ERROR, 'Some information not available!')


        context = {
            'runp': runp,
            'tables': runp.results_set.filter(filetype='csv'),
            'charts': runp.results_set.filter(filetype='img'),
            'json': runp.results_set.filter(filetype='json'),
            'graphs': runp.results_set.filter(filetype='graph'),
            'rdata': runp.results_set.filter(filetype='rdata'),
            'charts_length': runp.results_set.filter(filetype='img').count(),
            'task': task,
            'badge': get_bootsrap_badge(task.status)
        }

        return render(request, self.template_name, context)


## ClassView computing statistic on network
##--------------------------------------------------
class NetworkStatsClass(View):
    template_name = 'engine/network_stats.html'

    def get(self, request, **kwargs):
        context = {'step2': 'network_stats_2'}
        return render(request, self.template_name, context)


class NetworkStatsStep2Class(View):
    template_name = 'engine/network_stats_2.html'

    def post(self, request):
        files = []
        removed_files = []
        dim = []

        for filepath in request.POST.getlist('uploaded'):
            ex_first_row = request.POST['exclude_col_header'] if 'exclude_col_header' in request.POST else None
            ex_first_col = request.POST['exclude_row_header'] if 'exclude_row_header' in request.POST else None
            valid, ret_file = document_validator(filepath, ex_first_row, ex_first_col)
            if valid['is_valid'] and valid['is_cubic']:
                dim.append(valid['nrow'])
                ## max_ga = valid['nrow']
                files.append({'name': ret_file.name,
                              'prop': valid,
                              'path': filepath
                              })
            else:
                removed_files.append(ret_file)

        if len(files) < 1:
            messages.add_message(self.request, messages.ERROR, 'Your files properties are not valid.')
            return redirect('network_stats')
        elif not all(x == dim[0] for x in dim):
            messages.add_message(self.request, messages.ERROR, 'Your files dim are not equal')
            return redirect('network_stats')

        context = {
                   'uploaded_files': files,
                   # 'max_ga': max_ga,
                   'removed_files': removed_files
                  }
        return render(request, self.template_name, context)


class NetworkStatsStep3Class(View):
    template_name = 'engine/network_stats_3.html'

    def post(self, request):
        files = []
        for file in request.POST.getlist('file'):
            files.append(os.path.join(settings.MEDIA_ROOT, file))

        components = request.POST.get("components", 'True')
        sep = request.POST.getlist('sep')
        param = {
            # 'd': request.POST.get("distance", "HIM"),
            # 'ga': float(request.POST.get("ga")) if request.POST.get("ga", False) else None,
            # 'components': True if components == 'True' else False,
            # 'rho':  float(request.POST.get("rho")) if request.POST.get("rho", False) else None,
            'header': True if request.POST.get("col", False) else False,
            'row.names': 1 if request.POST.get("row", False) else None
        }
        try:
            runp = RunningProcess(
                process_name='Network stats',
                inputs=param,
                submited=datetime.now()
            )
            # t = netstats.delay(files, sep, param, settings.MEDIA_ROOT, settings.RESULT_PATH)
            t = settings.APP.send_task('netdist', [files, sep, param, settings.MEDIA_ROOT, settings.RESULT_PATH])
            runp.task_id = t.id

        except Exception, e:
            messages.add_message(self.request, messages.ERROR, 'Error: %s' % str(e))

        try:
            runp.save()
            context = {'files': files, 'task': t, 'uuid': t.id}

            session = self.request.session.get('runp',[])
            session.append(runp.pk)
            self.request.session['runp'] = session
        except DatabaseError, e:
            t.revoke(terminate=True)
            messages.add_message(self.request, messages.ERROR, 'Error: %s' % str(e))

        messages.add_message(self.request, messages.SUCCESS, 'Process submitted with success!!!')
        return render(request, self.template_name, context)

# Process status view from database
class NetworkStatsStep4Class(View):
    template_name = 'engine/network_stats_4.html'

    def get(self, request, uuid, **kwargs):
        
        # task = djcelery.celery.AsyncResult(uuid)
        task = settings.APP.AsyncResult(uuid)
        
        try:
            runp = RunningProcess.objects.get(task_id=uuid)
        except RunningProcess.DoesNotExist:
            runp = None
            messages.add_message(self.request, messages.ERROR, 'Some information not available!')

        
        context = {
            'runp': runp,
            'tables': runp.results_set.filter(filetype='csv'),
            'charts': runp.results_set.filter(filetype='img'),
            'json': runp.results_set.filter(filetype='json'),
            'graphs': runp.results_set.filter(filetype='graph'),
            'rdata': runp.results_set.filter(filetype='rdata'),
            'charts_length': runp.results_set.filter(filetype='img').count(),
            'task': task,
            'badge': get_bootsrap_badge(task.status)
        }

        return render(request, self.template_name, context)


































# Process status view from database
class ProcessStatus2(View):
    template_name = 'engine/process_status.html'

    def get(self, request, uuid, **kwargs):
        #task = djcelery.celery.AsyncResult(uuid)
        try:
            runp = RunningProcess.objects.get(task_id=uuid)
        except RunningProcess.DoesNotExist:
            runp = None
            messages.add_message(self.request, messages.ERROR, 'Some information not available!')

        context = {
            'runp': runp
        }

        return render(request, self.template_name, context)


def download_zip_file(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Bad request")

    files = request.POST.getlist('files', [])

    if len(files):
        file_list = Results.objects.filter(pk__in=files)

        ## Folder name in ZIP archive which contains the above files
        zip_basename = "result"
        zip_filename = "%s.zip" % zip_basename
        #
        # Open StringIO to grab in-memory ZIP contents
        s = StringIO.StringIO()

        # The zip compressor
        zf = zipfile.ZipFile(s, "w")

        for fpath in file_list:
            # nome file interno allo zip
            zip_path = os.path.join("./", fpath.filename)

            # Add file, at correct path
            if fpath.filetype == 'img':
                zf.write(fpath.imagestore.path, zip_path)
            else:
                zf.write(fpath.filestore.path, zip_path)

        # Must close zip for all contents to be written
        zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    # ..and correct content-disposition
        resp = HttpResponse(s.getvalue(), mimetype="application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp
    else:
        # TODO: check
        messages.add_message(request, messages.ERROR, 'No file selected.')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@render_to_json(mimetype='application/json')
def datatables(request, pk):
    try:
        res = Results.objects.get(pk=pk)
    except RunningProcess.DoesNotExist:
        raise Http404

    return res.tables_to_json()


def multiuploader(request):
    if request.method == 'POST':
        if request.FILES == None:
            return HttpResponseBadRequest('No file uploaded')
        try:
            #getting file data for farther manipulations
            file = request.FILES[u'files[]']
            wrapped_file = UploadedFile(file)
            filename = wrapped_file.name
            file_size = wrapped_file.file.size

            #getting file url here
            file_url = handle_upload(request, file)

            result = []
            result.append({"name": filename,
                           "size": file_size,
                           "url": str(file_url),
                           "thumbnail_url": '',
                           "delete_url": '',
                           "delete_type": "POST"})
            response_data = json.dumps({
                'files': result
            })
            return HttpResponse(response_data, mimetype='application/json')
        except Exception, e:
            return HttpResponseBadRequest(str(e))
    else: #GET
        messages.add_message(request, messages.ERROR, 'Bad request')
        context = {}
    return render(request, 'engine/network_distance.html', context)


def process_list(request):
    try:
        session = request.session.get('runp', [])
    
        if len(session):
            runp = RunningProcess.objects.filter(pk__in=session)
        else:
            runp = []
            
        context = {
            'runp': runp
        }

        return render(request, 'engine/my_process_list.html', context)
    except ConnectionError, e:
        context = None
        messages.add_message(request, messages.ERROR, 'Sorry, error connecting to worker server. Try again later.')
        return render(request, 'engine/my_process_list.html', context)
    except Exception, e:
        context = None
        messages.add_message(request, messages.ERROR, 'Sorry, unexpected error occured. Try again.')
        return render(request, 'engine/my_process_list.html', context)
    
def revoke_job(request):
    if request.POST:
        runp = RunningProcess.objects.get(pk=request.POST['taskid'])
        try:
            task = settings.APP.AsyncResult(runp.task_id)
            task.revoke(terminate=True, signal="SIGKILL")
            payload = {'success': True}
            messages.add_message(request, messages.SUCCESS, 'Job stopped')
        except:
            payload = {'success': False}
            messages.add_message(request, messages.SUCCESS, 'Could not revoke the job')
        return HttpResponse(json.dumps(payload), content_type='application/json')

@csrf_exempt
def fake_save(request):

    if request.POST:
        param = {'pp': request.POST.get('p1')}
        process_name = request.POST.get('process_name')
        task_id = request.POST.get('task_id')
        runp = RunningProcess(
                process_name=process_name,
                inputs=param,
                submited=datetime.now()
        )
        try:
            runp.save()
            payload = {'success': True}
        except:
            payload = {'success': False}

        return HttpResponse(json.dumps(payload), content_type='application/json')