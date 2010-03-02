from django.conf.urls.defaults import patterns
from django.views.generic.simple import direct_to_template

from views import search

urlpatterns = patterns('',
  (r'^search/$', search),  
)

urlpatterns += patterns('verses.views',
  (r'^(?P<version>\w+)/$', 'book_chapters'),
  (r'^(?P<version>\w+)/(?P<book>[a-zA-Z0-9 ]+)/$', 'chapters'),
  (r'^(?P<version>\w+)/(?P<book>[a-zA-Z0-9 ]+)/(?P<chapter>\d+)/?(?P<verse>\d+)?(\-)?(?P<verse2>\d+)?/$', 'verses'),
)
