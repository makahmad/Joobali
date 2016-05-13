from django.conf.urls import patterns, url

from referal import views

urlpatterns = patterns('',
	url(r'^$', views.referalForm),
)
