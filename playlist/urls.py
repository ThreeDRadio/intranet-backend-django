from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^summary/$', views.summary, name='summary'),
    url(r'^reports/$', views.reports, name='reports'),
]
