from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('hamexam.exam.views',
      (r'^index', 'index'),
      (r'^grade', 'grade_exam'),
      (r'^exam/(?P<exam_class>.+)$', 'exam'),
      (r'^$', 'index'),
      #(r'^(?P<some_stuff>.+)/$', 'index2'),
)
