from django.conf.urls import include, url
from django.contrib import admin
from adminapp import views
from examapp import urls as examurl
from studentapp import urls as studenturl
from teacherapp import urls as teacherurl
from mobileapp import urls as mobileurl


urlpatterns = [
    # Examples:
    # url(r'^$', 'TestSeriesProj.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^index/', views.index),
    url(r'^teacher/', views.teacher),
    url(r'^exam/', include(examurl,namespace='exam')),
    url(r'^api/', include(mobileurl,namespace='mobile')),
    url(r'^open-teacher/', views.open_teacher),


]
