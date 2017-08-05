from django.conf.urls import url
from . import studentapi

urlpatterns = [
    url(r'^categories/', studentapi.get_categories, name='categories'),
]
