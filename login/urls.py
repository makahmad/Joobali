from django.conf.urls import patterns, url

from login import views

urlpatterns = patterns('',
	url(r'^$', views.form),
	url(r'^home', views.home),
)
