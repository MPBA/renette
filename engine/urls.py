from django.conf.urls import patterns, include, url

from django.contrib import admin
from .views import NetworkDistanceClass, NetworkDistanceStep2Class, NetworkDistanceStep3Class
admin.autodiscover()

urlpatterns = patterns('engine.views',

                       url(regex='^network/distance/$',
                           view=NetworkDistanceClass.as_view(),
                           name='network_distance'),

                       url(regex='^network/distance/2$',
                           view=NetworkDistanceStep2Class.as_view(),
                           name='network_distance_2'),

                       url(regex='^network/distance/3$',
                           view=NetworkDistanceStep3Class.as_view(),
                           name='network_distance_3'),
                       )
