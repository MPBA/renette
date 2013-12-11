# -*- encoding: utf-8 -*-
__author__ = 'ernesto'
#This file contains only the views for the main app. It's made just to render an home page for the project

from django.views.generic import TemplateView
from django.views.generic.base import View
from django.shortcuts import redirect, render
from .utils import handle_uploads, document_validator
from django.contrib import messages


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
        print request.POST
        files = request.POST.getlist('file')
        context = {'files': files}
        messages.add_message(self.request, messages.SUCCESS, 'Process submitted with success!!!')
        return render(request, self.template_name, context)
