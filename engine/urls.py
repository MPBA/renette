from django.conf.urls import patterns, include, url

from django.contrib import admin
from .views import (NetworkDistanceClass, NetworkDistanceStep2Class, NetworkDistanceStep3Class,
                    ProcessStatus, download_zip_file,
                    NetworkInferenceClass, NetworkInferenceStep2Class, NetworkInferenceStep3Class, NetworkInferenceStep4Class,
                    NetworkStabilityClass, NetworkStabilityStep2Class, NetworkStabilityStep3Class, ProcessStatus2)
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

                       # url(regex='^process/status/(.+)/$',
                       #     view=ProcessStatus.as_view(),
                       #     name='process_status'),
                       
                       url(regex='^process/status/(.+)/$',
                           view=ProcessStatus2.as_view(),
                           name='process_status'),

                       url(regex='^process/download/zip/(?P<pk>\d+)$',
                           view=download_zip_file,
                           name='process_download_zip'),

                       url(regex='^network/inference/$',
                           view=NetworkInferenceClass.as_view(),
                           name='network_inference'),

                       url(regex='^network/inference/2/$',
                           view=NetworkInferenceStep2Class.as_view(),
                           name='network_inference_2'),

                       url(regex='^network/inference/3/$',
                           view=NetworkInferenceStep3Class.as_view(),
                           name='network_inference_3'),

                       url(regex='^network/inference/4/(.+)/$',
                           view=NetworkInferenceStep4Class.as_view(),
                           name='network_inference_4'),

                       url(regex='^network/stability/$',
                           view=NetworkStabilityClass.as_view(),
                           name='network_stability'),

                       url(regex='^network/stability/2$',
                           view=NetworkStabilityStep2Class.as_view(),
                           name='network_stability_2'),

                       url(regex='^network/stability/3$',
                           view=NetworkStabilityStep3Class.as_view(),
                           name='network_stability_3'),

                       url(r'^multiuploader/$', 'multiuploader'),

                       url(r'^process/list/$', 'process_list', name="process_list"),
                       url(r'^datatables/(?P<pk>\d+)/$', 'datatables', name="datatables"),

                       url(regex='^process/graph/(.+)/(.+)/(\d+)/$',
                           view='process_graph',
                           name='process_graph'),

                       url(regex='^results/full_view/(.+)/(.+)/(\d+)/$',
                           view='full_results_view',
                           name='full_results_view'),
                       )

