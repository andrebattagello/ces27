from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static  # Just for development=
from django.views.generic.simple import redirect_to
from django.conf import settings

admin.autodiscover()

urlpatterns = patterns('',

    (r'^super/admin/', include(admin.site.urls)),
    (r'^super/admin/doc/', include('django.contrib.admindocs.urls')),

    # our home page
    #url(r'^$', 'home_view', name='home'),
)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)  # Also for dev
