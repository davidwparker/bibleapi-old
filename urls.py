from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.views.generic.simple import direct_to_template

admin.autodiscover()

#defaults -- index, admin, login, logout, profile
urlpatterns = patterns('',
  (r'^$', direct_to_template, {
    'template': 'index.html'
  }),
  (r'^admin/(.*)', admin.site.root),
  (r'^accounts/login/$',  login),
  (r'^accounts/logout/$', logout),
  (r'^accounts/profile/$', direct_to_template, {
    'template': 'registration/profile.html'
  }),
)

#static content for development
if settings.DEBUG:
  urlpatterns += patterns('',
    (r'^site_media/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
  )

urlpatterns += patterns('',
  (r'^api/$', direct_to_template, {
    'template': 'api.html'
  }),
)

urlpatterns += patterns('',
  (r'^search/$', direct_to_template, {
    'template': 'search_form.html'
  }),
)
urlpatterns += patterns('',
  (r'^bible/', include('verses.urls')),
)
