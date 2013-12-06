from django.conf.urls import patterns, include, url

from django.contrib import admin
from .views import MainView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'renette.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    (r'^pages/', include('django.contrib.flatpages.urls')),
    url(regex='^$', view=MainView.as_view(), name='home'),
)
