from django.conf.urls import patterns, url

from django.contrib import admin
from .views import (NetworkDistanceClass, NetworkDistanceStep2Class, NetworkDistanceStep3Class,
                    NetworkDistanceStep4Class, download_zip_file, NetworkInferenceClass, NetworkInferenceStep2Class,
                    NetworkInferenceStep3Class, NetworkInferenceStep4Class, NetworkStabilityClass,
                    NetworkStabilityStep2Class, NetworkStabilityStep3Class, NetworkStabilityStep4Class,
                    NetworkStatsClass, NetworkStatsStep2Class, NetworkStatsStep3Class, NetworkStatsStep4Class, 
                    ProcessStatus2)
admin.autodiscover()

urlpatterns = patterns('engine.views',
                       url(r'^process/list/$', 'process_list', name="process_list"),

                       url(regex='^network/distance/$',
                           view=NetworkDistanceClass.as_view(),
                           name='network_distance'),
                       
                       url(regex='^network/distance/2$',
                           view=NetworkDistanceStep2Class.as_view(),
                           name='network_distance_2'),
                       
                       url(regex='^network/distance/3$',
                           view=NetworkDistanceStep3Class.as_view(),
                           name='network_distance_3'),
                       
                       url(regex='^network/distance/4/(.+)/$',
                           view=NetworkDistanceStep4Class.as_view(),
                           name='network_distance_4'),

                       url(regex='^network/stats/$',
                           view=NetworkStatsClass.as_view(),
                           name='network_stats'),
                       
                       url(regex='^network/stats/2$',
                           view=NetworkStatsStep2Class.as_view(),
                           name='network_stats_2'),
                       
                       url(regex='^network/stats/3$',
                           view=NetworkStatsStep3Class.as_view(),
                           name='network_stats_3'),
                       
                       url(regex='^network/stats/4/(.+)/$',
                           view=NetworkStatsStep4Class.as_view(),
                           name='network_stats_4'),


                       # url(regex='^process/status/(.+)/$',
                       #     view=ProcessStatus.as_view(),
                       #     name='process_status'),
                       
                       url(regex='^process/status/(.+)/$',
                           view=ProcessStatus2.as_view(),
                           name='process_status'),

                       url(regex='^process/download/zip/$',
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
                       
                       url(regex='^network/stability/4/(.+)/$',
                           view=NetworkStabilityStep4Class.as_view(),
                           name='network_stability_4'),


                       url(r'^multiuploader/$', 'multiuploader'),

                       
                       url(r'^datatables/(?P<pk>\d+)/$', 'datatables', name="datatables"),

                       url(r'^revoke/job', 'revoke_job', name='revoke_job'),

                       url(r'^save/fake', 'fake_save', name='fake_save'),
                       url(r'^get/fake', 'fake_get', name='fake_get'),

                       #url(regex='^process/graph/(.+)/(.+)/(\d+)/$',
                       #    view='process_graph',
                       #    name='process_graph'),
                       #
                       #url(regex='^results/full_view/(.+)/(.+)/(\d+)/$',
                       #    view='full_results_view',
                       #    name='full_results_view'),
                       )

