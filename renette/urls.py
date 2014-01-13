from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import FlatPageSitemap
from .sitemap import StaticViewSitemap
from .views import MainView
admin.autodiscover()


sitemaps = {
    'flatpages': FlatPageSitemap,
    'static': StaticViewSitemap
}

urlpatterns = patterns('',
    # base url
    url(r'^admin/', include(admin.site.urls)),
    (r'^pages/', include('django.contrib.flatpages.urls')),
    (r'^robots\.txt$', include('robots.urls')),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    # main app url
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
    url(r'^faq/$', 'django.contrib.flatpages.views.flatpage', {'url': '/faq/'}, name='faq'),
    url(r'^redactor/', include('redactor.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
