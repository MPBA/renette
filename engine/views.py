# -*- encoding: utf-8 -*-
__author__ = 'ernesto'
#This file contains only the views for the main app. It's made just to render an home page for the project

from django.views.generic import TemplateView
from django.views.generic.base import View
from django.shortcuts import redirect, render
from django.db import DatabaseError
from django.http import Http404
from .utils import handle_uploads, document_validator, get_bootsrap_badge, read_csv_results
from .models import RunningProcess
from django.contrib import messages
from engine.tasks import test_netdist
from django.conf import settings
import djcelery
from datetime import datetime
import os

class NetworkDistanceClass(View):
    template_name = 'engine/network_distance.html'

    def get(self, request, **kwargs):
        context = {}
        return render(request, self.template_name, context)


class NetworkDistanceStep2Class(View):
    template_name = 'engine/network_distance_2.html'

    def post(self, request):
        files = []
        to_save = []
        dim = []
        if len(request.FILES.getlist('files')) < 2:
            messages.add_message(self.request, messages.ERROR, 'You must upload at least 2 files!!!')
            return redirect('network_distance')

        for file in request.FILES.getlist('files'):
            ex_col = request.POST['exclude_col_header'] if 'exclude_col_header' in request.POST else None
            ex_row = request.POST['exclude_row_header'] if 'exclude_row_header' in request.POST else None
            valid = document_validator(file, ex_col, ex_row)
            if valid['is_valid'] and valid['is_cubic']:
                dim.append(valid['nrow'])
                max_ga = valid['nrow']
                separ = valid['separator']
                files.append({'name': file.name, 'type': file.content_type, 'file_to_save': file.read(), 'prop': valid})
                to_save.append(file)
        if len(files) < 2:
            messages.add_message(self.request, messages.ERROR, 'Your files properties are not .....')
            return redirect('network_distance')
        elif not all(x == dim[0] for x in dim):
            messages.add_message(self.request, messages.ERROR, 'Your files dim are not equal')
            return redirect('network_distance')
        else:
            f = handle_uploads(self.request, to_save)
        context = {'posted_files': request.FILES.getlist('files'),
                   'uploaded_files': files,
                   'max_ga': max_ga,
                   'handled': f,
                   'sep': separ}
        return render(request, self.template_name, context)


class NetworkDistanceStep3Class(View):
    template_name = 'engine/network_distance_3.html'

    def post(self, request):
        files = []
        for file in request.POST.getlist('file'):
            files.append(os.path.join(settings.MEDIA_ROOT, file))
        components = request.POST.get("components", 'True')
        param = {
            'd': request.POST.get("distance", "HIM"),
            'ga': float(request.POST.get("ga")) if request.POST.get("ga", False) else None,
            'components': True if components == 'True' else False,
            'rho':  float(request.POST.get("rho")) if request.POST.get("rho", False) else None,
            'sep': request.POST.get("sep", "\t"),
            'header': True if request.POST.get("col", False) else False,
            'row.names': 1 if request.POST.get("row", False) else None
        }
        try:
            runp = RunningProcess(
                process_name='network_distance',
                inputs=param,
                submited=datetime.now()
            )
            t = test_netdist.delay(files, param)
            runp.task_id = t.id

        except Exception, e:
            messages.add_message(self.request, messages.ERROR, 'Error: %s' % str(e))

        try:
            runp.save()
        except DatabaseError, e:
            t.revoke(terminate=True)
            messages.add_message(self.request, messages.ERROR, 'Error: %s' % str(e))

        context = {'files': files, 'task': t, 'uuid': t.id}

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
            'uuid': uuid,
            'task': task,
            'badge': get_bootsrap_badge(task.status),
            'runp': runp
        }

        if task.status == 'SUCCESS':
            tables = read_csv_results(task.result)
            context['tables'] = tables

        return render(request, self.template_name, context)