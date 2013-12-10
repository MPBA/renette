# -*- encoding: utf-8 -*-
__author__ = 'ernesto'
#This file contains only the views for the main app. It's made just to render an home page for the project

from django.views.generic import TemplateView


#class based view for home page rendering
class NetworkDistanceClass(TemplateView):
    template_name = 'engine/network_distance.html'

    def get_context_data(self, **kwargs):
        context = super(NetworkDistanceClass, self).get_context_data()
        return context
