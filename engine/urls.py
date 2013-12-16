from django.conf.urls import patterns, include, url

from django.contrib import admin
from .views import NetworkDistanceClass, NetworkDistanceStep2Class, NetworkDistanceStep3Class, ProcessStatus,\
    download_zip_file
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

                       url(regex='^process/status/(.+)$',
                           view=ProcessStatus.as_view(),
                           name='process_status'),

                       url(regex='^process/download/zip/(?P<pk>\d+)$',
                           view=download_zip_file,
                           name='process_download_zip'),
                       )
