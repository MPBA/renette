import time
from urllib2 import urlopen
from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import FlatPageSitemap
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.views.defaults import server_error
from .sitemap import StaticViewSitemap
from .views import MainView
admin.autodiscover()


def h500(*args, **kwargs):
    if ((time.time() - cache.get('last_time_status_check_launched', 0)) > 10) and hasattr(settings, 'STATUS_CHECK_URL'):
        urlopen(settings.STATUS_CHECK_URL)
        cache.set('last_time_status_check_launched', time.time())
    server_error(*args, **kwargs)

handler500 = h500


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
    url(regex='^$', view=cache_page(60 * 5)(MainView.as_view()), name='home'),
    url(r'^sendmail/$', 'renette.views.contact', name='sendmail'),

    # test url
    url(r'^test/db/$', 'renette.views.test_db'),
    url(r'^test/rabbitmq/$', 'renette.views.test_rabbitmq'),
    url(r'^test/celery/$', 'renette.views.test_celery'),

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
