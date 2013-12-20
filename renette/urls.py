from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from .views import MainView
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'renette.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    (r'^pages/', include('django.contrib.flatpages.urls')),
    (r'^engine/', include('engine.urls')),
    url(regex='^$', view=MainView.as_view(), name='home'),
    url(r'^sendmail/$', 'renette.views.contact', name='sendmail'),
    # engine urls
    (r'^engine/', include('engine.urls')),
    # admin area
    url(r'^admin/', include(admin.site.urls)),
    # specific flatpages urls
    url(r'^about/$', 'django.contrib.flatpages.views.flatpage', {'url': '/about/'}, name='about'),
    url(r'^contact/$', 'django.contrib.flatpages.views.flatpage', {'url': '/contact/'}, name='contact'),
    url(r'^tutorial/$', 'django.contrib.flatpages.views.flatpage', {'url': '/tutorial/'}, name='tutorial'),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
