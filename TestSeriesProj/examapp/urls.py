from django.conf.urls import include, url, patterns
from examapp import views


urlpatterns = patterns('',
        url(r'^$', views.index, name='exam_index'),
        url(r'^open/$', views.open, name='open_exam')
    )