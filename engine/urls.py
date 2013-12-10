from django.conf.urls import patterns, include, url

from django.contrib import admin
from .views import NetworkDistanceClass
admin.autodiscover()

urlpatterns = patterns('engine.views',

                       url(regex='^network/distance/$', view=NetworkDistanceClass.as_view(), name='network_distance'),

                       )
