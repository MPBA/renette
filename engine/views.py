# -*- encoding: utf-8 -*-
__author__ = 'ernesto'
#This file contains only the views for the main app. It's made just to render an home page for the project

from django.views.generic import TemplateView
from django.views.generic.base import View
from django.shortcuts import redirect, render
from .utils import handle_uploads, document_validator

#class based view for home page rendering
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
        for file in request.FILES.getlist('files'):

            valid = document_validator(file)
            if valid['is_valid']:
                files.append({'name': file.name, 'type': file.content_type, 'file_to_save': file.read(), 'prop': valid})
                to_save.append(file)
        f = handle_uploads(self.request, to_save)

        context = {'posted_files': request.FILES.getlist('files'), 'uploaded_files': files}
        return render(request, self.template_name, context)
