# -*- encoding: utf-8 -*-
__author__ = 'ernesto'
from datetime import datetime

#This file contains only the views for the main app. It's made just to render an home page for the project

from django.views.generic import TemplateView


#class based view for home page rendering
class MainView(TemplateView):
    template_name = 'renette/home.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data()
        context['msg'] = "ciao"
        return context