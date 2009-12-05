from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'blog.views.default'),
    (r'^entry/(?P<entry_id>\d+)/(?P<slug>.+)/$', 'blog.views.detail'),
    (r'^entry/comment/(?P<entry_id>\d+)/$', 'blog.views.comment'),
    (r'^archive/category/(?P<category_id>\d+)/$', 'blog.views.by_category'),
    (r'^archive/tag/(?P<tag_id>\d+)/$', 'blog.views.by_tag'),
    (r'^archive/(?P<year>\d+)/$', 'blog.views.archive_year'),
    (r'^archive/(?P<year>\d+)/(?P<month>\d+)/$', 'blog.views.archive_month'),
    (r'^archive/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/$', 'blog.views.archive_day'),
)
