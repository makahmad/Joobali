from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
	url(r'^listprograms', views.listPrograms, name='listPrograms'),
)
