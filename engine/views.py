# -*- encoding: utf-8 -*-
__author__ = 'ernesto'
#This file contains only the views for the main app. It's made just to render an home page for the project

from django.views.generic import TemplateView
from django.views.generic.base import View
from django.shortcuts import redirect, render, render_to_response
from django.core.files.uploadedfile import UploadedFile
from django.db import DatabaseError
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from .utils import document_validator, get_bootsrap_badge, read_csv_results, handle_upload
from .models import RunningProcess
from django.contrib import messages
from engine.tasks import test_netdist, test_netinf, test_netstab
from django.conf import settings
import djcelery
import os
import StringIO
import zipfile
import json
from datetime import datetime
import magic


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
            ex_col = request.POST['exclude_col_header'] if 'exclude_col_header' in request.POST else None
            ex_row = request.POST['exclude_row_header'] if 'exclude_row_header' in request.POST else None
            valid, ret_file = document_validator(filepath, ex_col, ex_row)
            if valid['is_valid']:
                dim.append(valid['nrow'])
                max_ga = valid['nrow']
                files.append({'name': ret_file.name,
                              'prop': valid,
                              'path': filepath
                              })
            else:
                removed_files.append(ret_file)

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
            'p': float(request.POST.get("p")) if request.POST.get("p", False) else 6,
            'fdr': float(request.POST.get("fdr")) if request.POST.get("fdr", False) else float(1e-3),
            'alpha': float(request.POST.get("alpha")) if request.POST.get("alpha", False) else 0.6,
            'c': float(request.POST.get("c")) if request.POST.get("c", False) else 15,
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
            t = test_netstab.delay(files, sep, param)
            runp.task_id = t.id

        except Exception, e:
            messages.add_message(self.request, messages.ERROR, 'Error: %s' % str(e))

        try:
            runp.save()
            context = {'files': files, 'task': t, 'uuid': t.id}

            session = self.request.session.get('runp',[])
            session.append(runp.pk)
            self.request.session['runp'] = session
            print self.request.session
        except DatabaseError, e:
            t.revoke(terminate=True)
            messages.add_message(self.request, messages.ERROR, 'Error: %s' % str(e))

        #context = {'files': files, 'task': t, 'uuid': t.id}
        print param
        messages.add_message(self.request, messages.SUCCESS, 'Process submitted with success!!!')
        return render(request, self.template_name, context)


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
            ex_col = request.POST['exclude_col_header'] if 'exclude_col_header' in request.POST else None
            ex_row = request.POST['exclude_row_header'] if 'exclude_row_header' in request.POST else None
            valid, ret_file = document_validator(filepath, ex_col, ex_row)
            if valid['is_valid']:
                dim.append(valid['nrow'])
                max_ga = valid['nrow']
                files.append({'name': ret_file.name,
                              'prop': valid,
                              'path': filepath
                              })
            else:
                removed_files.append(ret_file)

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
            'methods': request.POST.get("methods", "cor"),
            'p': float(request.POST.get("p")) if request.POST.get("p", False) else 6,
            'fdr': float(request.POST.get("fdr")) if request.POST.get("fdr", False) else float(1e-3),
            'alpha': float(request.POST.get("alpha")) if request.POST.get("alpha", False) else 0.6,
            'c': float(request.POST.get("c")) if request.POST.get("c", False) else 15,
            'measure': request.POST.get("measure", None),
            'header': True if request.POST.get("col", False) else False,
            'row.names': 1 if request.POST.get("row", False) else None
        }
        print param
        try:
            runp = RunningProcess(
                process_name='Network inference',
                inputs=param,
                submited=datetime.now()
            )
            t = test_netinf.delay(files, sep, param)
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


class NetworkDistanceClass(View):
    template_name = 'engine/network_distance.html'

    def get(self, request, **kwargs):
        context = {'step2': 'network_distance_2'}
        return render(request, self.template_name, context)


class NetworkDistanceStep2Class(View):
    template_name = 'engine/network_distance_2.html'

    def post(self, request):
        files = []
        removed_files = []
        dim = []

        if len(request.POST.getlist('uploaded')) < 2:
            messages.add_message(self.request, messages.ERROR, 'You must upload at least 2 files!!!')
            return redirect('network_distance')

        for filepath in request.POST.getlist('uploaded'):
            ex_col = request.POST['exclude_col_header'] if 'exclude_col_header' in request.POST else None
            ex_row = request.POST['exclude_row_header'] if 'exclude_row_header' in request.POST else None
            valid, ret_file = document_validator(filepath, ex_col, ex_row)
            if valid['is_valid'] and valid['is_cubic']:
                dim.append(valid['nrow'])
                max_ga = valid['nrow']
                files.append({'name': ret_file.name,
                              'prop': valid,
                              'path': filepath
                              })
            else:
                removed_files.append(ret_file)

        if len(files) < 2:
            messages.add_message(self.request, messages.ERROR, 'Your files properties are not .....')
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
            #'sep': request.POST.get("sep", "\t"),
            'header': True if request.POST.get("col", False) else False,
            'row.names': 1 if request.POST.get("row", False) else None
        }
        try:
            runp = RunningProcess(
                process_name='Network distance',
                inputs=param,
                submited=datetime.now()
            )
            t = test_netdist.delay(files, sep, param)
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


class ProcessStatus(View):
    template_name = 'engine/process_status.html'

    def get(self, request, uuid, **kwargs):
        task = djcelery.celery.AsyncResult(uuid)

        try:
            runp = RunningProcess.objects.get(task_id=uuid)
        except RunningProcess.DoesNotExist:
            runp = None
            messages.add_message(self.request, messages.ERROR, 'Alcune info non disponibili')

        context = {
            'uuid': uuid, ### TODO: e' nei models, riferirsi a quello
            'task': task, ### TODO: e' nei models, riferirisi a quello
            'badge': get_bootsrap_badge(task.status), ### TODO: e' nei model, riferirsi a quello
            'runp': runp
        }

        if task.status == 'SUCCESS':
            result = task.result
            idx = 0
            if isinstance(result, dict):
                context['download_btn'] = True  ### TODO: e' nei models
                for key in result.keys():
                    if idx == 3:
                        context['tomanyresult'] = True #todo too
                        break
                    idx += 1

                    val = result.get(key)
                    csvlist, tomanyfile = read_csv_results(val['csv_files'])
                    if csvlist:
                        val['csv_tables'] = csvlist
                        val['tomanyfile'] = tomanyfile
                    else:
                        messages.add_message(self.request, messages.ERROR, 'Impossibile trovare i file dei risultati')
                    result.update({key: val})

            context['result'] = result
        return render(request, self.template_name, context)


def download_zip_file(request, pk):
    try:
        runp = RunningProcess.objects.get(pk=pk)
    except RunningProcess.DoesNotExist:
        raise Http404

    result = runp.result
    print result
    file_list = []
    for key in result.keys():
        val = result.get(key)
        file_list += val['csv_files']
        file_list += val['img_files']
    print file_list
    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # FIXME: Set this to something better
    zip_basename = "result"
    zip_filename = "%s.zip" % zip_basename

    # Open StringIO to grab in-memory ZIP contents
    s = StringIO.StringIO()

    # The zip compressor
    zf = zipfile.ZipFile(s, "w")

    for fpath in file_list:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        print fpath
        zip_path = os.path.join("./", fname)

        # Add file, at correct path
        zf.write(os.path.join(settings.MEDIA_ROOT,fpath), zip_path)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    # ..and correct content-disposition
    resp = HttpResponse(s.getvalue(), mimetype="application/x-zip-compressed")

    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp


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

            #getting thumbnail url using sorl-thumbnail
            #generating json response array

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
    except Exception, e:
        return HttpResponseBadRequest(str(e))
